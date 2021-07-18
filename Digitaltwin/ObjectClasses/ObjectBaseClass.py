# Trials of objects for the robo platform
# HDF5 class for storing object parameters and provenance (not sure how to do the latter)
from McHDF import McHDF
from pathlib import Path
# requires 'pip install cfunits', and 'conda install -c conda-forge udunits2' on the command line
import cfunits # documentation on UDUNITS package https://ncas-cms.github.io/cfunits/cfunits.Units.html
import datetime # for events. Timestamp should be datetime.datetime.utcnow().isoformat()
import h5py 
# pip install numpy-stl
from stl import mesh
import numpy as np
# ALL INTERNAL LENGTH UNITS IN METERS, ANGLES IN RADIAN
# ALL EXTERNAL LENGTH UNITS IN MM, ANGLES IN DEGREE
from scipy.spatial import transform 

class OBC(McHDF):
    """
    Class that describes a single object. 
     * filename: the filename that tracks and logs the object. Here you can store an object in a particular state and recreate it from that storage. This is an HDF5 file
     * nxsEntryPoint: root point from which this object is described in the HDF5 file
     * location: The location of the object's origin /with respect to the parent object/. An absolute location can be requested, which traverses the parents and adds the locations. 
     * rotation: The rotation of the object /with respect to the parent object/. An absolute rotation can be requested, which traverses the parents rotations and adds them..
     * isAlive: Whether the object has been destroyed/dropped or not
     * name: A freeform string to identify the object
     * events: A list of dictionaries, each representing an event in the log. This can be simple movements, but also changes in parent (e.g. moving a slide from the rack to the hotplate), or AFM scans, measurements, etc. These will also be stored in the log and retrieved
     * not sure we will need attachedAt.. we'll see. 
    The object is attached to a parent object (such as a robot arm or table). 
    attachedAt is on the bottom surface, center of slide.
    """
    filename = None  # path to the HDF5 file that tracks the object
    nxsEntryPoint = '/object/'
    storeKeys = [      # keys to store in an HDF5 output file
        "filename",    # filename to the HDF5 file that tracks this object
        "extent",      # six-element vector [-x, x, -y, y, -z, z] from location
        "attachedAt",  # three-element location offset of where the object attaches to parent if not at grab point/location
        "location",    # three-element vector of x, y, z where the attachedAt is
        "rotation",    # rotation of object in proper Euler angles from its original definition. extent and rack/holder positions rotate along, around "location"
        "isAlive",     # if object has not crashed, burned or otherwise killed
        "stlFilename", # not sure if Path object can be stored..
        "parent",      # not sure how this should be stored... probably storing the filename.
        # "events",    # list of events (dicts) that tracks what happened to the object. Not sure how to save this in H5
        "name"         # object name (freeform)
    ]
    loadKeys = [  # keys to load from an HDF5 output file
        "extent",
        "attachedAt",
        "location",
        "rotation", 
        "isAlive",
        "events",
        "name"         # object name (freeform)
    ]
    _name = '' 
    _extent = [] # [0, 0, 0]
    _attachedAt = None # [0, 0, 0] where it is attached to parent
    _rotation = [0, 0, 1] # up is Z
    _location = None # [0, 0, 0]
    _isAlive = True
    _provenance = [] # a list of events. Every event is a dict with 'timestamp', 'event', and possible other fields such as microscope images, temperature scans, etc.
    _externalUnits = {'Length': cfunits.Units('mm'), 'Angle': cfunits.Units('degree')}
    _internalUnits = {'Length': cfunits.Units('m'), 'Angle': cfunits.Units('radian')}

    parent = None # object it is attached to
    children = [] # object's immediate children
    _stlFilename = None # maybe objects can carry an STL representation of themselves for collision estimation, including a rotation and translation
    _stl = None # stl object from the numpy-stl library
    # collision is where the STLS of the objects share a space. Can probably be calculated with VTK

    def __init__(self, filename:Path = Path('testSlide.h5'), loadFromFile = False, deleteExisting = False, debugPrintStatements = False, **kwargs):
        """loadFromFile must be a previous object instance. """
        # reset all values to make sure we're instantiating it clean
        self.filename = None  # path to the HDF5 file that tracks the object
        self.nxsEntryPoint = '/object/'
        self._name = '' 
        self._extent = [] # [0, 0, 0]
        self._attachedAt = [0, 0, 0] # attached at location origin to parent by default
        self._rotation = [0, 0, 0] # no rotation. 
        self._location = None # [0, 0, 0] location of attachedAt/grab point
        self._isAlive = True # assume it hasn't yet been killed/destroyed
        self._provenance = [] # a list of events. Every event is a dict with 'timestamp', 'event', and possible other fields such as microscope images, temperature scans, etc.
        self._externalUnits = {'Length': cfunits.Units('mm'), 'Angle': cfunits.Units('degree')}
        self._internalUnits = {'Length': cfunits.Units('m'), 'Angle': cfunits.Units('radian')}
        self._stlFilename = None
        self.parent = None # object it is attached to
        self._debugPrint = debugPrintStatements
        self.children = []

        for key, value in kwargs.items():
            assert key in self.storeKeys, "Key {} is not a valid option".format(key)
            setattr(self, key, value)

        assert filename is not None, 'needs a filename for tracking and provenance'
        self.filename = Path(filename)
        if deleteExisting and self.filename.exists():
            # remove the file if it already exists and we explicitly request it
            self.filename.unlink()

        if loadFromFile:
            self.resetProvenance()
            self.load(loadFromFile)
        
        if self.parent != None:
            assert isinstance(self.parent, OBC), 'WARNING: Given parent is not a subclass of OBC class!'
            self.parent.children.append(self)
                
    
    def _externalToInternalUnits(self, listIn, unitLabel = 'Length'):
        if isinstance(listIn, list):
            return [
                cfunits.Units.conform(inVal, self._externalUnits[unitLabel], self._internalUnits[unitLabel])
                for inVal in listIn
            ]
        else: # just a single value
            return cfunits.Units.conform(listIn, self._externalUnits[unitLabel], self._internalUnits[unitLabel])
    def _internalToExternalUnits(self, listIn, unitLabel = 'Length'):
        if isinstance(listIn, list):
            return [
                cfunits.Units.conform(inVal, self._internalUnits[unitLabel], self._externalUnits[unitLabel])
                for inVal in listIn
            ]
        else:
            return cfunits.Units.conform(listIn, self._internalUnits[unitLabel], self._externalUnits[unitLabel])

    @property        
    def stl(self):
        if (self._stl is None) and (isinstance(self.stlFilename, Path)):
            # load STL from filename:
            self.loadStl()
        if (self._stl is None) and (not isinstance(self.stlFilename, Path)):
            # generate STL from extent:
            if self._debugPrint:
                print('stl not found and stlFilename not set, generating STL cube from extent')
            self.extentCube(setStl = True)
        return self._stl
    @stl.setter
    def stl(self, stlInstance):
        self._stl = stlInstance

    @property        
    def stlFilename(self):
        return self._stlFilename
    @stlFilename.setter
    def stlFilename(self, filename):
        if not isinstance(filename, Path): filename = Path(filename)
        assert filename.exists(), 'STL file name {filename} does not exist'
        self._stlFilename = filename
        self.event(f"Object STL filename updated to {filename}.")

    def loadStl(self):
        self.stl = mesh.Mesh.from_file(self.stlFilename)
        self.event(f"Object STL mesh loaded from {self.filename}.")

    def extentFromStl(self, setExtent = False):
        if self.stl is None: self.loadStl()
        'use setExtent = True to export this extent to the object extent'
        minx = float(self.stl.x.min())
        maxx = float(self.stl.x.max())
        miny = float(self.stl.y.min())
        maxy = float(self.stl.y.max())
        minz = float(self.stl.z.min())
        maxz = float(self.stl.z.max())
        self.event(f"extent determined from STL: {minx, maxx, miny, maxy, minz, maxz}.")

        if setExtent: 
            self.extent = [minx, maxx, miny, maxy, minz, maxz]
        return minx, maxx, miny, maxy, minz, maxz

    def unityCube(self):
        "cube with side lenght 1, centered around the cube center of mass"
        # from: https://numpy-stl.readthedocs.io/en/latest/usage.html
        # Define the 8 vertices of the cube
        vertices = np.array([\
            [-0.5, -0.5, -0.5],
            [+0.5, -0.5, -0.5],
            [+0.5, +0.5, -0.5],
            [-0.5, +0.5, -0.5],
            [-0.5, -0.5, +0.5],
            [+0.5, -0.5, +0.5],
            [+0.5, +0.5, +0.5],
            [-0.5, +0.5, +0.5]])
        # Define the 12 triangles composing the cube
        faces = np.array([\
            [0,3,1],
            [1,3,2],
            [0,4,7],
            [0,7,3],
            [4,5,6],
            [4,6,7],
            [5,1,2],
            [5,2,6],
            [2,3,6],
            [3,7,6],
            [0,1,5],
            [0,5,4]])

        # Create the mesh
        cube = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(faces):
            for j in range(3):
                cube.vectors[i][j] = vertices[f[j],:]
        return cube

    def extentCube(self, setStl = True):
        """returns a mesh object that describes a cube of the dimensions of the extent"""
        cube = self.unityCube()
        # set to size
        xsize = np.abs(self.extent[1] - self.extent[0])
        ysize = np.abs(self.extent[3] - self.extent[2])
        zsize = np.abs(self.extent[5] - self.extent[4])
        cube.vectors *= [xsize, ysize, zsize]
        # shift sideways:
        xcen = (self.extent[1] + self.extent[0])/2
        ycen = (self.extent[3] + self.extent[2])/2
        zcen = (self.extent[5] + self.extent[4])/2
        cube.vectors += [xcen, ycen, zcen]
        if setStl:
            self.stl = cube
        return cube

    def units(self):
        "prints units used internally in the object and externally"
        retStr = [f'Internal (object) unit for {key}: {val}' for key, val in self._internalUnits.items()]
        retStr += [f'External (user) unit for {key}: {val}' for key, val in self._externalUnits.items()]
        return retStr

    def event(self, eventData = None):
        assert eventData is not None, 'When registering an event, eventData must be a dictionary with timestamp and event, as well as potential extra associated data'
        if isinstance(eventData, dict):
            # add directly to the list
            assert all([item in eventData.keys() for item in ['timestamp', 'event']]), 'eventData must contain at least "timestamp" and "event"'
            self._provenance += [eventData]
        elif isinstance(eventData, str):
            self._provenance += [{'timestamp': datetime.datetime.utcnow().isoformat(), 'event': eventData}]
        
    @property        
    def extent(self):
        if self._extent == []:
            # check if we can calculate it from STL:
            if self._debugPrint:
                print('extent not provided, deriving it from STL')
            self.extentFromStl(setExtent = True)
        assert self._extent != [], 'Extent could not be calculated, check the provided STL or extent parameters'
        return np.array(self._internalToExternalUnits(self._extent, unitLabel = 'Length'))
    @extent.setter
    def extent(self, dim):
        self._extent = self._externalToInternalUnits(dim, unitLabel = 'Length')
        self.event(f"Object extent updated to {dim} {self._externalUnits['Length'].units}")
 
    @property        
    def name(self):
        return self._name
    @name.setter
    def name(self, newname):
        self._name = newname
        self.event(f'Object name updated to {newname}')

    @property        
    def attachedAt(self):
        return self._internalToExternalUnits(self._attachedAt, unitLabel = 'Length')
    @attachedAt.setter
    def attachedAt(self, orig):
        self._attachedAt = self._externalToInternalUnits(orig, unitLabel = 'Length')
        self.event(f"Object attachedAt updated to {orig} {self._externalUnits['Length'].units}")

    # def getAbsolute(self, prop):
    #     """ not quite so easy anymore when rotations are added, superseded by getAbsoluteLocation and getAbsoluteRotation """
    #     assert hasattr(self, prop), f'property: {prop} must exist in class'
    #     absProp = getattr(self, prop)
    #     parent = self.parent
    #     while isinstance(parent, OBC):
    #         absProp += getattr(parent, prop)
    #         parent = getattr(parent, 'parent') # get its parent to continue the traverse
    #     return absProp
    
    def getAbsoluteLocation(self):
        absLoc = np.array([0., 0., 0.]) # in meters
        parent = self # start here. 
        while isinstance(parent, OBC):
            # apply rotation of parent to object first
            parentRot = transform.Rotation.from_rotvec(parent._rotation)
            # if parentRot.magnitude() != 0: 
            #     rv = parentRot.as_rotvec() / parentRot.magnitude()
            # else:
            #     rv = [1., 0., 0.]
            # stlCopy.rotate(1*np.array(rv), parentRot.magnitude(), point=[0,0,0])
            absLoc = parentRot.apply(absLoc)
            # then shift by location of parent in m
            absLoc += parent._location
            parent = getattr(parent, 'parent') # get its parent to continue the traverse

        # while isinstance(parent, OBC):
        #     # apply rotation of parent to location
        #     parentRot = transform.Rotation.from_rotvec(parent._rotation)
        #     absLoc = parentRot.apply(absLoc)
        #     # then shift by location of parent 
        #     absLoc += parent._location
        #     parent = getattr(parent, 'parent') # get its parent to continue the traverse
        return self._internalToExternalUnits(absLoc, unitLabel = 'Length')

    def getAbsoluteRotationInstance(self):
        absRot = transform.Rotation.from_rotvec(self._rotation) # in radians of rotvec
        parent = self.parent
        while isinstance(parent, OBC):
            absRot *= transform.Rotation.from_rotvec(parent._rotation)
            parent = getattr(parent, 'parent') # get its parent to continue the traverse
        return absRot # as transform.Rotation instance
    
    def renderAbsoluteStlVectors(self):
        """returns an absolute representation of the STL"""
        # copy STL
        stlCopy = mesh.Mesh(self.stl.data.copy())
        # objStlVectors = stlCopy.vectors
        parent = self # start here. 
        while isinstance(parent, OBC):
            # apply rotation of parent to object first
            parentRot = transform.Rotation.from_rotvec(parent._rotation)
            if parentRot.magnitude() != 0: 
                rv = parentRot.as_rotvec() / parentRot.magnitude()
            else:
                rv = [1., 0., 0.]
            stlCopy.rotate(1*np.array(rv), parentRot.magnitude(), point=[0,0,0])
            # objStlVectors = parentRot.apply(objStlVectors)
            # then shift by location of parent in mm (STL units)
            stlCopy.translate(parent.location)
            parent = getattr(parent, 'parent') # get its parent to continue the traverse
        objStlVectors = stlCopy.vectors
        return objStlVectors

        # This can't work like this, need to do that stepwise, people 
        # r = self.getAbsoluteRotationInstance()
        # # decompose the rotvec to a vector and magnitude:
        # if r.magnitude() != 0: 
        #     rv = r.as_rotvec() / r.magnitude()
        # else:
        #     rv = [1., 0., 0.]
        # stlCopy.rotate(-1*np.array(rv), r.magnitude(), point=[0,0,0])
        # # translate to location
        # objStlVectors = stlCopy.vectors
        # loc = self.getAbsoluteLocation()
        # objStlVectors += loc
        # return objStlVectors

    @property        
    def location(self, absolute = False):
        if absolute: prop = self.getAbsolute('location')
        else: prop = self._location
        return np.array(self._internalToExternalUnits(prop, unitLabel = 'Length'))
    @location.setter
    def location(self, loc, absolute = False):
        assert not absolute, 'absolute setting of location not implemented yet'

        self._location = self._externalToInternalUnits(loc, unitLabel = 'Length')
        self.event(f"Object location updated to {loc} {self._externalUnits['Length'].units}")

    @property        
    def rotation(self):
        return np.array(self._internalToExternalUnits(self._rotation, unitLabel = 'Angle'))
    @rotation.setter
    def rotation(self, rot):
        self._rotation = self._externalToInternalUnits(rot, unitLabel = 'Angle')
        self.event(f"Object rotation vector updated to {rot} {self._externalUnits['Angle'].units}")

    def provenance(self):
        return f'{self._provenance}'
    
    def store(self, filename=None, path=None): # copied from McSAS3
        """stores the object in an output file (HDF5)"""
        if path is None: path=f"{self.nxsEntryPoint}"
        if filename is None: filename = self.filename
        for key in self.storeKeys:
            value = getattr(self, key, None)
            self._HDFstoreKV(filename=filename, path=path, key=key, value=value)
        # store provenance:
        for num, item in enumerate(self._provenance): 
            if self._debugPrint:
                print(f'{num}: {item}')
            self._HDFstoreKV(filename=filename, path=path+f'events/', key=f'event{num}', value=item)

    def resetProvenance(self):
        self._provenance = []

    def load(self, filename=None): # copied from McSAS3
        """load from previous instance"""
        path=f"{self.nxsEntryPoint}"
        if filename is None: filename = self.filename
        for key in self.loadKeys:
            if key == 'events': continue # we do this at the end...
            with h5py.File(filename, "r") as h5f:
                if key in h5f[f"{path}"]:
                    setattr(self, key, h5f[f"{path}{key}/"][()])
        # now to load the events special loading, events are stored as a list of dicts.
        self.resetProvenance() # reset provenance to an empty list
        curPath = path + 'events/'
        if self._debugPrint:
            print(f'curPath: {curPath}')
        with h5py.File(filename, "r") as h5f: # fill dict with items in event
            for subpath in h5f[f'{curPath}'].keys(): # for every event
                print(f'subpath: {subpath}')
                # here's how to load back a dict:
                curDict = {} # fresh dict
                [curDict.update({key: val[()]}) for key, val in h5f[f'{curPath}{subpath}'].items()]
                print(f'curDict = {curDict}')
                # add recovered event to events
                self.event(curDict)
        self.event(f'Completed object restore from file {filename}')