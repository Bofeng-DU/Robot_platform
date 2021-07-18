# Trials of objects for the robo platform
from .ObjectBaseClass import OBC

# ALL INTERNAL LENGTH UNITS IN METERS, ANGLES IN RADIAN
# ALL EXTERNAL LENGTH UNITS IN MM, ANGLES IN DEGREE
class baseTable(OBC):
    """
    Tables are derived from ObjectBaseClass. 
    These have the following additions:
     * positions: a dictionary of labels and associated locations. These can be read by the objects and taken over once an object rests on a position. This is a two-element dictionary with (x, y)
    """
    material = 'stainless steel'
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
    
    @property        
    def liftHeight(self):
        return self._internalToExternalUnits(self._liftHeight, unitLabel = 'Length')
    @liftHeight.setter
    def liftHeight(self, liftHeight):
        self._liftHeight = self._externalToInternalUnits(liftHeight, unitLabel = 'Length')
        self.event(f"Object sink distance updated to {liftHeight} {self._externalUnits['Length'].units}")

def setPositions(table, xNumHoles, yNumHoles, height):
    for ix in range(xNumHoles):
        for iy in range(yNumHoles):
            table.positions[ix, iy] = [ix * 25, iy * 25, height] # in mm

def setExtentBreadboard(board, xNumHoles, yNumHoles, height, threadOffset):
    board.extent = [-threadOffset, (xNumHoles - 1) * 25 + threadOffset, -threadOffset, (yNumHoles - 1) * 25 + threadOffset, 0., height] # extent from location/origin

def setExtentCenteredBreadboard(board, xNumHoles, yNumHoles, height, threadOffset, xDimBoard, yDimBoard):
    board.extent = [- xDimBoard/2, xNumHoles * 25 - xDimBoard/2, - yDimBoard/2, yNumHoles * 25 - yDimBoard/2, 0, height] # extent from location/origin

class opticalTableL(baseTable):
    '''
    Origin upper left corner
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs) # run the base class init
        # update values specific to this table
        xNumHoles = 33
        yNumHoles = 57

        setPositions(self, xNumHoles, yNumHoles, 0.)
        # self.location = [0, 0, 0] # at origin of the room
        self.extent = [-45, 870, -45, 1470, -1200, 0] # extent from location/origin

class breadboard4545(baseTable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) # run the base class init
        # update values specific to this table
        xNumHoles = 18
        yNumHoles = 18
        height = 12.7
        threadOffset = 12.5

        setPositions(self, xNumHoles, yNumHoles, height)
        # self.location = [0, 0, 0] # at origin of the room
        setExtentBreadboard(self, xNumHoles, yNumHoles, height, threadOffset)

class breadboard1545(baseTable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) # run the base class init
        # update values specific to this table
        xNumHoles = 6
        yNumHoles = 18
        height = 12.7
        threadOffset = 12.5

        setPositions(self, xNumHoles, yNumHoles, height)
        # self.location = [0, 0, 0] # at origin of the room
        setExtentBreadboard(self, xNumHoles, yNumHoles, height, threadOffset)

class breadboard1515C(baseTable):
    "centered variant with the origin in the center of the baseplate"
    def __init__(self, **kwargs):
        super().__init__(**kwargs) # run the base class init
        # update values specific to this table
        xNumHoles = 6
        yNumHoles = 6
        height = 12.7
        threadOffset = 12.5
        xDimBoard = 150.
        yDimBoard = 150.
        
        setPositions(self, xNumHoles, yNumHoles, height)
        # self.location = [0, 0, 0] # at origin of the room
        setExtentCenteredBreadboard(self, xNumHoles, yNumHoles, height, threadOffset, xDimBoard, yDimBoard)

class breadboard1515(baseTable):
    "Non centered version"
    def __init__(self, **kwargs):
        super().__init__(**kwargs) # run the base class init
        # update values specific to this table
        xNumHoles = 6
        yNumHoles = 6
        height = 12.7
        threadOffset = 12.5
        
        setPositions(self, xNumHoles, yNumHoles, height)
        # self.location = [0, 0, 0] # at origin of the room
        setExtentBreadboard(self, xNumHoles, yNumHoles, height, threadOffset)

class breadboard1530(baseTable):
    "for robot arm"
    def __init__(self, **kwargs):
        super().__init__(**kwargs) # run the base class init
        # update values specific to this table
        xNumHoles = 12
        yNumHoles = 6
        height = 12.7
        threadOffset = 12.5

        setPositions(self, xNumHoles, yNumHoles, height)
        # self.location = [0, 0, 0] # at origin of the room
        setExtentBreadboard(self, xNumHoles, yNumHoles, height, threadOffset)

class breadboard3045(baseTable):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) # run the base class init
        # update values specific to this table
        xNumHoles = 18
        yNumHoles = 12
        height = 12.7
        threadOffset = 12.5

        setPositions(self, xNumHoles, yNumHoles, height)
        # self.location = [0, 0, 0] # at origin of the room
        setExtentBreadboard(self, xNumHoles, yNumHoles, height, threadOffset)