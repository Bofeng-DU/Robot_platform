# Trials of objects for the robo platform
from .ObjectBaseClass import OBC

# ALL INTERNAL LENGTH UNITS IN METERS, ANGLES IN RADIAN
# ALL EXTERNAL LENGTH UNITS IN MM, ANGLES IN DEGREE
class baseMicroscope(OBC):
    """
    Microscopes are derived from ObjectBaseClass. 
    These have the following additions:
     * positions: a dictionary of labels and associated locations. These can be read by the objects and taken over once an object rests on a position.
    """
    material = 'unknown'
    objectType = 'base'
    _positions = {}        # dictionary of position labels and x, y, z resting positions for samples, relative to the origin/location of the object, translated by the location of the object

    def __init__(self, **kwargs):
        # add the approach vector to the store and load
        self._positions = {}
        self.storeKeys += ['positions']
        self.loadKeys += ['positions']
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

class wildType374547(baseMicroscope):

    '''
    Origin in the center of the rectangle at the bottom
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs) # run the base class init

        self._extent_x = 265. # mm
        self._extent_y = 180. # mm
        self._extent_z = 650. # mm
        self._offset_x = 30. # mm

        self.extent = [-self._extent_x/2. - self._offset_x, self._extent_x/2. - self._offset_x, -self._extent_y/2., self._extent_y/2., 0., self._extent_z] # extent from location/origin