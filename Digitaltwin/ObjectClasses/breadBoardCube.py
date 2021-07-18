# Trials of objects for the robo platform
from .ObjectBaseClass import OBC

# ALL INTERNAL LENGTH UNITS IN METERS, ANGLES IN RADIAN
# ALL EXTERNAL LENGTH UNITS IN MM, ANGLES IN DEGREE
class baseBreadBoardCube(OBC):
    """
    Bread board cubes are derived from ObjectBaseClass. 
    These have the following additions:
     * positions: a dictionary of labels and associated locations. These can be read by the objects and taken over once an object rests on a position.
     This is a one-element dictionary with indices from 1 to 6 corresponding to a dice setup. In the default orientation, the "1" is at the bottom und thus points towards the negative z-axis, the "3" points in the positive x-axis, the "5" points in the positive y-axis.
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

class simpleBreadBoardCube(baseBreadBoardCube):

    '''
    Origin at bottom of cube
    '''

    def __init__(self, **kwargs):
        super().__init__(**kwargs) # run the base class init

        self._side_length = 25. # mm

        self.extent = [-self._side_length/2., self._side_length/2., -self._side_length/2., self._side_length/2., 0., self._side_length] # extent from location/origin

        self.positions[1] = [0., 0., 0.]
        self.positions[2] = [0., -self._side_length/2., self._side_length/2.]
        self.positions[3] = [self._side_length/2., 0., self._side_length/2.]
        self.positions[4] = [-self._side_length/2., 0., self._side_length/2.]
        self.positions[5] = [0., self._side_length/2., self._side_length/2.]
        self.positions[6] = [0., 0., self._side_length]