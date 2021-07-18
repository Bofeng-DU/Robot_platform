# Trials of objects for the robo platform
from .ObjectBaseClass import OBC

# ALL INTERNAL LENGTH UNITS IN METERS, ANGLES IN RADIAN
# ALL EXTERNAL LENGTH UNITS IN MM, ANGLES IN DEGREE
class baseSyringeActuator(OBC):
    """
    Cylinders are derived from ObjectBaseClass. 
    These have the following additions:
     * syringePositions: a dictionary of labels and associated locations. These can be read by the objects and taken over once an object rests on a position. Keys are integers starting at 0. Stores the positions of the needle tips of syringes relative to the syringe actuator.
    """
    material = 'unknown'
    objectType = 'base'
    _syringePositions = {}        # dictionary of position labels and x, y, z resting positions for samples, relative to the origin/location of the object, translated by the location of the object

    def __init__(self, **kwargs):
        self._syringePositions = {}
        self.storeKeys += ['syringePositions']
        self.loadKeys += ['syringePositions']
        # now call the original init method of OBC
        super().__init__(**kwargs)
    
    @property        
    def syringePositions(self):
        return self._syringePositions
    @syringePositions.setter
    def syringePositions(self, posDict):
        assert isinstance(posDict, dict), 'syringePositions must be a dict'
        self._syringePositions = posDict
        self.event(f'Object position dictionary updated to {posDict}')

class Alladin_1000(baseSyringeActuator):

    '''
    Origin at the top of the red housing where it touches the SMT profile in the middle
    '''

    def __init__(self, **kwargs):

        super().__init__(**kwargs) # run the base class init

        self.width = 146. # mm      from left to right of red housing
        self.depth = 131. # mm      from surface of SMT profile to most outer extent (black curved plastic)
        self.height = 279. # mm     from top of red housing down to tip of syringe needle

        # Define syringePositions
        self.syringePositions[0] = [-127.8, -25., -self.height]

        # Define extent
        self.extent = [73., -(self.width-73.), 0., self.depth, 0., -self.height]

class Harvard_PHD(baseSyringeActuator):

    '''
    Origin at the lower right corner when viewed from the front syringe needle side
    '''

    def __init__(self, **kwargs):

        super().__init__(**kwargs) # run the base class init

        self.width = 157. # mm      from left to right when viewed from the front syringe needle side
        self.depth = 310. # mm      depth when viewed from the front syringe needle side
        self.height = 279. # mm     height when viewed from the front syringe needle side

        syringe_offset_x = -11.

        # Define syringePositions
        self.syringePositions[0] = [-39., syringe_offset_x, 123.5]
        self.syringePositions[1] = [-102., syringe_offset_x, 123.5]

        # Define extent
        self.extent = [0., -self.width, self.depth + syringe_offset_x, syringe_offset_x, self.height, 0.]