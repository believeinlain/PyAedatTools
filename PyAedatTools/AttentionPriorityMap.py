
import numpy as np

from PyAedatTools import EventBuffer

class AttentionPriorityMap:
    def __init__(self, width, height, radius):
        self.width = width
        self.height = height
        self.APM = [[ [] for i in range(height)] for j in range(width)]
        self.intensityArray = np.zeros((width, height), np.int)
        self.peak = 0
        self.radius = radius
        # TODO: pass this parameter, maybe share a buffer with clustering?
        self.eventBuffer = EventBuffer.EventBuffer(1000)
    
    # modify the APM based on the given event
    def processEvent(self, x, y, t):
        newEvent = EventBuffer.event(x, y, t)
        self.eventBuffer.update(newEvent)

        # clip affected area to edges of APM
        xLeft = 0 if x < self.radius else x - self.radius 
        xRight = self.width if x + self.radius > self.width else x + self.radius 
        yLeft = 0 if y < self.radius else y - self.radius 
        yRight = self.height if y + self.radius > self.height else y + self.radius 
        # select affected area
        for u in range(xLeft, xRight):
            for v in range(yLeft, yRight):
                # add event to the list for this location
                self.APM[u][v].append(newEvent)
                for e in self.APM[u][v]:
                    # filter out events older than oldestTimeStamp in buffer
                    if e.t < self.eventBuffer.oldestTimestamp:
                        self.APM[u][v].remove(e)
                
                self.intensityArray[u, v] = len(self.APM[u][v])

        # set the peak to the max value in the intensity array
        # corresponding to the length of the array where the most events affected
        self.peak = np.amax(self.intensityArray)
    
    # return the normalized intensity at a given point
    # based on the number of events in the list for this location
    def getNormalizedIntensity(self, x, y):
        return float(self.intensityArray[x, y]) / float(self.peak)


