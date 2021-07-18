# Trials of objects for the robo platform
from .ObjectBaseClass import OBC

# ALL INTERNAL LENGTH UNITS IN METERS, ANGLES IN RADIAN
# ALL EXTERNAL LENGTH UNITS IN MM, ANGLES IN DEGREE
class baseProfileSMT(OBC):
    """
    SMT profiles are derived from ObjectBaseClass. 
    These have the following additions:
    None at this point
    """
    material = 'unknown'
    objectType = 'base'

    def __init__(self, **kwargs):
        # now call the original init method of OBC
        super().__init__(**kwargs)
    

class smt_50x25(baseProfileSMT):

    '''
    Origin centered in the middle of one side of the profile
    '''

    def __init__(self, **kwargs):

        super().__init__(**kwargs) # run the base class init

        self.side_length_1 = 50. # mm
        self.side_length_2 = 25. # mm
        self.length = 578. # mm

        # Define extent
        self.extent = [self.side_length_1/2., -self.side_length_1/2., -self.side_length_2/2., self.side_length_2/2., 0., self.length]