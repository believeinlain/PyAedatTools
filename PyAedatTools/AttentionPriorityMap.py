
import numpy as np

from PyAedatTools import EventBuffer

class AttentionPriorityMap:
    def __init__(self, width, height, radius, eventBuffer):
        self.width = width
        self.height = height
        self.APM = [[ [] for i in range(height)] for j in range(width)]
        self.intensityArray = np.zeros((width, height), np.int)
        self.peak = 1
        self.radius = radius
        self.eventBuffer = eventBuffer
    
    # modify the APM based on the given event
    def processEvent(self, e):

        # clip affected area to edges of APM
        xLeft = 0 if e.x < self.radius else e.x - self.radius 
        xRight = self.width if e.x + self.radius > self.width else e.x + self.radius 
        yLeft = 0 if e.y < self.radius else e.y - self.radius 
        yRight = self.height if e.y + self.radius > self.height else e.y + self.radius 
        # select affected area
        for u in range(xLeft, xRight):
            for v in range(yLeft, yRight):
                # add event to the list for this location
                self.APM[u][v].append(e)
                for el in self.APM[u][v]:
                    # filter out events older than oldestTimeStamp in buffer
                    if el.t < self.eventBuffer.oldestTimestamp:
                        self.APM[u][v].remove(el)
                
                self.intensityArray[u, v] = len(self.APM[u][v])

        # set the peak to the max value in the intensity array
        # corresponding to the length of the array where the most events affected
        self.peak = np.amax(self.intensityArray)
    
    # return the normalized intensity at a given point
    # based on the number of events in the list for this location
    def getNormalizedIntensity(self, x, y):
        return float(self.intensityArray[x, y]) / float(self.peak)


