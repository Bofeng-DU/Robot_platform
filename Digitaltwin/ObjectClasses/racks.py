# Trials of objects for the robo platform
from .ObjectBaseClass import OBC

# ALL INTERNAL LENGTH UNITS IN METERS, ANGLES IN RADIAN
# ALL EXTERNAL LENGTH UNITS IN MM, ANGLES IN DEGREE
class baseRack(OBC):
    """
    Racks are derived from ObjectBaseClass. 
    These have the following additions:
     * positions: a dictionary of labels and associated locations. These can be read by the objects and taken over once an object rests on a position.
     * liftHeight: the height an object needs to be lifted before it can be safely extracted
     * approachVector: the vector from which it is safe to approach. in table XYZ directions for now. 

    """
    material = 'ABS'
    objectType = 'objectHolder'
    _approachVector = None # vector from which the holder positions can be safely approached
    _positions = {}        # dictionary of position labels and x, y, z resting positions for samples, relative to the origin/location of the object, translated by the location of the object
    _liftHeight = None     # height the samples need to be lifted above their resting positions before they can be safely extracted 

    def __init__(self, **kwargs):
        # add the approach vector to the store and load
        self.storeKeys += ['approachVector', 'positions', 'liftHeight']
        self.loadKeys += ['approachVector', 'positions', 'liftHeight']
        # now call the original init method of OBC
        super().__init__(**kwargs)

    @property        
    def approachVector(self):
        return self._approachVector
    @approachVector.setter
    def approachVector(self, avec):
        self._approachVector = avec
        self.event(f'Object approach vector updated to {avec}')
    
    @property        
    def positions(self):
        return self._positions
    @positions.setter
    def positions(self, posDict):
        assert isinstance(posDict, dict), 'positions must be a dict'
        self._positions = posDict
        self.event(f'Object position dictionary updated to {posDict}')
    
    @property        
    def liftHeight(self):
        return self._internalToExternalUnits(self._liftHeight, unitLabel = 'Length')
    @liftHeight.setter
    def liftHeight(self, liftHeight):
        self._liftHeight = self._externalToInternalUnits(liftHeight, unitLabel = 'Length')
        self.event(f"Object sink distance updated to {liftHeight} {self._externalUnits['Length'].units}")

class slideRackSven(baseRack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) # run the base class init
        # update values specific to this rack
        self.positions = { # slide position offsets with respect to the location/origin
            'A': [0, 0, 104],
            'B': [0, 0, 104 - 13],
            'C': [0, 0, 104 - 13 * 2],
            'D': [0, 0, 104 - 13 * 3],
            'E': [0, 0, 104 - 13 * 4],
            'F': [0, 0, 104 - 13 * 5],            
        }
        self.liftHeight = 8 # mm
        self.extent = [-50, 50, -50, 50, 0, 120] # extent from location/origin
        self.approachVector = [1, 0, 0] # approach from +x *before rotation*

class gripper(baseRack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) # run the base class init
        # update values specific to this rack
        self.positions = { # slide position offsets with respect to the location/origin
            'actuator': [0, 66, -11], 
            'centerOfRotation' : [0, 0, 0]
        }
        self.liftHeight = 8 # mm
        self.extent = [-50, 50, -50, 50, 0, 120] # extent from location/origin
        self.approachVector = [1, 0, 0] # approach from +x *before rotation*
