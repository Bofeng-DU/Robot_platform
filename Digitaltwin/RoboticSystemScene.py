from IPython.display import display
import numpy as np
import matplotlib.pyplot as plt

# Import required classes individually from pythreejs instead of altogether because pythreejs's objects file clashes with the objects variable used in this notebook
from pythreejs import Mesh, MeshPhysicalMaterial, BoxBufferGeometry, SphereBufferGeometry, BufferGeometry, MeshStandardMaterial, ShaderMaterial, BufferAttribute, PerspectiveCamera, DirectionalLight, AmbientLight, VectorKeyframeTrack, QuaternionKeyframeTrack, AnimationClip, AnimationAction, AnimationMixer, Scene, OrbitControls, Renderer, LightShadow, NumberKeyframeTrack, AxesHelper
from pyquaternion import Quaternion


class RoboticSystemScene():


    def __init__(self, objects, debugPrintStatements=False):
        assert type(objects) == list
        self._objects = objects
        self._debugPrint = debugPrintStatements

    
    def objectToMesh(self, object, color):

        if self._debugPrint:
            print(f'Converting object {object.name} to mesh')

        # Four step process to generate pythreejs based Mesh object

        objStlVectors = object.renderAbsoluteStlVectors()

        vertices = BufferAttribute(array=objStlVectors, normalized=False)

        geometry = BufferGeometry( attributes={'position': vertices}, )

        return Mesh(geometry=geometry, material=MeshStandardMaterial(color=color))


    def convertObjectsToMeshes(self):

        self._meshes = []
        self._colors = {} # Store colors of each object here. This is later used to identify object's meshes in the PyThreeJS scene

        # first let's get some colors for the objects:
        rbColors = 255*plt.cm.rainbow(np.linspace(0, 1, len(self._objects)))[:,0:3]

        # Load the STL files and add the vectors to the plot
        for num, obj in enumerate(self._objects):

            # Compute the color string
            color = tuple(rbColors[num].astype(int))

            color = '#%02x%02x%02x' % color

            self._colors[num] = color
            
            self._meshes.append(self.objectToMesh(obj, color))


    def _updateObjectMesh(self, obj_idx):
        color = self._meshes[obj_idx].material.color

        self._meshes[obj_idx] = self.objectToMesh(self._objects[obj_idx], color)


    def createSceneThreeJs(self):

        # Set up window size
        view_width = 1600
        view_height = 600
        self.camera = PerspectiveCamera(position=[1000,0,1000], aspect=view_width/view_height, zoom=1.)

        # Set up camera and lighting conditions
        key_light = DirectionalLight(position=[400., 600. ,50.], intensity=10.)
        ambient_light = AmbientLight(intensity=1.)

        # Create coordinate system axes and move it slightly upwards so it doesn't disappear in table
        axesHelper = AxesHelper(100)
        axesHelper.position = (0., 0., 1.)

        # Set up scene
        self._children = self._meshes + [self.camera, key_light, ambient_light, axesHelper]

        self.scene_3js = Scene(children=self._children)

        # Render scene
        controller = OrbitControls(controlling=self.camera)
        self.renderer = Renderer(camera=self.camera, scene=self.scene_3js, controls=[controller],
                            width=view_width, height=view_height)


    def showSceneThreeJs(self):
        assert hasattr(self, 'renderer')
        display(self.renderer)

    
    def _getChildIndex(self, obj_idx):

        '''
        Get the index of a child corresponding to object with index obj_idx.
        Works through comparison of colors.
        Therefore it MUST be ensured that all meshes differ in color at any time!
        '''

        child_idx = -1

        for i in range(len(self._children)):
            if isinstance(self._children[i], Mesh):
                if self._children[i].material.color == self._colors[obj_idx]:
                    child_idx = i
        
        if child_idx != -1:
            return child_idx
        else:
            raise Exception('Could not translate object: Object not found.')
    

    def translateObject(self, translation, obj_idx, originalCall=True):

        assert isinstance(translation, np.ndarray)
        assert len(translation) == 3

        child_idx = self._getChildIndex(obj_idx)

        if originalCall:
            self._objects[obj_idx].location += translation
        self._updateObjectMesh(obj_idx)

        self.scene_3js.remove(children=self._children[child_idx])
        self.scene_3js.add(children=self._meshes[obj_idx])

        self._children[child_idx] = self._meshes[obj_idx]   # Update children list with new mesh object

        for child in self._objects[obj_idx].children:
            for object_idx, object in enumerate(self._objects):
                if object == child:
                    self.translateObject(translation, object_idx, originalCall=False)
                    break


    def rotateObject(self, rotation, obj_idx, originalCall=True):
        assert isinstance(rotation, np.ndarray)
        assert len(rotation) == 3

        child_idx = self._getChildIndex(obj_idx)

        if originalCall:
            self._objects[obj_idx].rotation += rotation
        self._updateObjectMesh(obj_idx)

        self.scene_3js.remove(children=self._children[child_idx])
        self.scene_3js.add(children=self._meshes[obj_idx])

        self._children[child_idx] = self._meshes[obj_idx]   # Update children list with new mesh object

        for child in self._objects[obj_idx].children:
            for object_idx, object in enumerate(self._objects):
                if object == child:
                    self.rotateObject(rotation, object_idx, originalCall=False)
                    break