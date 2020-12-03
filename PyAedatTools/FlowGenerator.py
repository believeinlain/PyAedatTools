
import numpy as np

from math import ceil
from math import pi

# Flow Generator takes in events and assigns them flow vectors based on
# an optical flow assessment
class FlowGenerator:
    def __init__(self):
        self.flowPlane = FlowPlane()
        return

    # Takes an event and assigns it to a track plane, from which it determines
    # that event's flow vector. If an event cannot be immediately assigned,
    # the flow vector will be (0, 0)
    def processEvent(self, x, y, t):
        flowVector = (0, 0)
        return flowVector

# Flow plane consists of a plane and a normal onto which events are projected
# and summed to compute a metric which corresponds to how well events follow
# this plane's angle
class FlowPlane:
    def __init__(self, width, height, normal):
        self.width = width
        self.height = height
        self.normal = normal
        self.eventPolarities = np.zeros((width, height), np.int)
    
    # project the event onto this plane
    def projectEvent(self, u, v, t, s):
        # break apart the normal into components
        (vu, vv) = self.normal
        # project the event onto the normal
        x = u - vu*t 
        y = v - vv*t
        # add the event to the plane if it is within bounds
        if (x >= 0 and x < self.width and y >= 0 and y < self.height):
            self.eventPolarities[x][y] += s
    
    # return the sum of the square of the sum at each location in the plane
    def getMetric(self):
        return np.sum(np.square(self.eventPolarities))


# Flow plane module projects events onto flow planes and computes a grid
# of metrics for events encountered so far
class FlowPlaneModule:
    def __init__(self, width, height, projectionResolution, projectionAngle):
        self.width = width
        self.height = height
        self.n = projectionResolution # perturbations are stored in nxn grid
        # an odd grid size is recommended so that we have a center of (0,0)
        self.r = projectionAngle # perturbations range from [-r/2 to r/2]
        # fill array of flow projections
        self.sumProjectedEvents = [[
            np.zeros((width, height)) for i in range(self.n)
        self.flowProjections = [[
            (ceil(i-self.n/2)/(self.n-1)*self.r, 
            ceil(j-self.n/2)/(self.n-1)*self.r) 
            for i in range(self.n)] for j in range(self.n)]
    
    # project an event onto each flow projection
    def projectEvent(self, u, v, t, s):
        for i in range(self.n):
            for j in range(self.n):
                # get the velocity from the projection angles
                (vu, vv) = self.flowProjections[i][j]
                # project the event onto that angle
                x = u - vu*t 
                y = v - vv*t
        
        self.sumProjectedEvents[x][y] += s# + self.sumProjectedEvents(projectedEvent)

                

