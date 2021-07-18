# Trials of objects for the robo platform
from .ObjectBaseClass import OBC

# ALL INTERNAL LENGTH UNITS IN METERS, ANGLES IN RADIAN
# ALL EXTERNAL LENGTH UNITS IN MM, ANGLES IN DEGREE
class baseMotion(OBC):
    """
    motion platforms are derived from ObjectBaseClass. 
    These have the following additions:
    (none so far.. )
    location defines their end-point location in 3D space, relative to their central position on the baseplate. 
    rotation defines the arm rotation on the mounting platform, as before
    positions dict is available maybe for default positions (park, calibration, actuator, etc.)
    orientations is a dict following positions, that has the orientation (transformations.rotation instance) of the end point in it. 
    """
    objectType = 'motion'
    _positions = {}        # dictionary of position labels and x, y, z resting positions for samples, relative to the origin/location of the object, translated by the location of the object
    _orientations = {}     # dictionary of position labels and x, y, z resting positions for samples, relative to the origin/location of the object, translated by the location of the object

    def __init__(self, **kwargs):
        self._positions = {}
        self._orientations = {}
        self.storeKeys += ['positions', 'orientations']
        self.loadKeys += ['positions', 'orientations']
        # now call the original init method of OBC
        super().__init__(**kwargs)
    
    @property        
    def positions(self):
        return self._positions
    @positions.setter
    def positions(self, posDict):
        assert isinstance(posDict, dict), 'positions must be a dict'
        self._positions = posDict
        self.event(f'Object position dictionary updated to {posDict}')

    @property        
    def orientations(self):
        return self._orientations
    @orientations.setter
    def orientations(self, oriDict):
        assert isinstance(oriDict, dict), 'orientations must be a dict'
        self._orientations = oriDict
        self.event(f'Object orientation dictionary updated to {oriDict}')

class roboArm(baseMotion):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs) # run the base class init

        self._x_dim = 114.
        self._y_dim = 88.
        self._z_dim = 104.
        self.extent = [-self._x_dim/2., self._x_dim/2., -self._y_dim/2., self._y_dim/2., 0., self._z_dim] # extent from location/origin