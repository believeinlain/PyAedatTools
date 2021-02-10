
import numpy as np

class BinaryCorrelativeFilter:
    def __init__(self, width, height, dt, subsample):
        self.width = width
        self.height = height
        self.dt = dt
        self.subsample = subsample
        self.cells = np.zeros((int(width/subsample), int(height/subsample)), np.int)
    
    # p should be 0 for off event, 1 for on event
    # x, y should be in range width, height
    # return True if we let event through, False if event should be filtered out
    def processEvent(self, x, y, t, p):
        cellX = int(x/self.subsample)
        cellY = int(y/self.subsample)
        self.cells[cellX][cellY] = t
        return self.cells[cellX][cellY] + self.dt > t