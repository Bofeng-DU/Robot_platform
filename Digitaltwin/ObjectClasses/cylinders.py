# Trials of objects for the robo platform
from .ObjectBaseClass import OBC

# ALL INTERNAL LENGTH UNITS IN METERS, ANGLES IN RADIAN
# ALL EXTERNAL LENGTH UNITS IN MM, ANGLES IN DEGREE
class baseCylinder(OBC):
    """
    Cylinders are derived from ObjectBaseClass. 
    These have the following additions:
     * positions: a dictionary of labels and associated locations. These can be read by the objects and taken over once an object rests on a position. Keys are integers starting at 0.
    """
    material = 'unknown'
    objectType = 'base'
    _positions = {}        # dictionary of position labels and x, y, z resting positions for samples, relative to the origin/location of the object, translated by the location of the object

    def __init__(self, **kwargs):
        self._positions = {}
        self.storeKeys += ['positions']
        self.loadKeys += ['positions']
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

class robotCylinder(baseCylinder):

    '''
    Origin centered at the bottom (i.e. one side) of the cylinder
    '''

    def __init__(self, **kwargs):

        super().__init__(**kwargs) # run the base class init

        self.diameter = 37.9 # mm
        self.height = 102.1 # mm

        # Define positions
        self.positions[0] = [0., 0., 0.]
        self.positions[1] = [0., 0., self.height]

        # Define extent
        self.extent = [-self.diameter/2., self.diameter/2., -self.diameter/2., self.diameter/2., 0., self.height]