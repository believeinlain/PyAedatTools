
import numpy as np

from math import floor

from PyAedatTools import FlowGenerator

# Flow plane module projects events onto flow planes and computes a grid
# of metrics for events encountered so far
class FlowPlaneModule:
    def __init__(self, width, height, n, r, c, centerAngle=(0,0)):
        self.width = width
        self.height = height
        self.n = n # normal angles are stored in nxn grid
        self.r = r # angles in metric array range from [-r/2 to r/2]
        self.c = c
        self.centerAngle = centerAngle
        
        self.flowPlaneIndices = []
        for i in range(self.n):
            for j in range(self.n):
                self.flowPlaneIndices.append((i, j))
        
        # fill dict of flow planes (to use dict comprehension)
        # store flow planes in a dict by index tuples
        self.flowPlanes = {
            (i, j): self.createFlowPlane(i, j)
            for (i, j) in self.flowPlaneIndices}

        self.childFlowPlaneModule = None
    
    # project an event onto each flow projection
    def projectEvent(self, e):
        for i in range(self.n):
            for j in range(self.n):
                self.flowPlanes[(i, j)].projectEvent(e)

    def updateMetrics(self):
        # update all metrics
        for f in self.flowPlanes.values():
            f.updateMetric()

    def getMaxMetricIndex(self):
        return max(self.flowPlanes, key=lambda plane: self.flowPlanes[plane].metric)

    # get normalized metric array (numpy array)
    # make sure to update metrics beforehand or you'll have nothing new
    def getNormalizedMetricArray(self):
        # get the value of the max metric
        maxMetric = self.flowPlanes[self.getMaxMetricIndex()].metric

        normalizedArray = np.zeros((self.n, self.n), np.float)

        # if max metric is 0, just return the array of zeros
        if maxMetric == 0:
            return normalizedArray

        for (i, j) in self.flowPlanes.keys():
            normalizedArray[i][j] = float(self.flowPlanes[(i, j)].metric) / float(maxMetric)
        
        return normalizedArray
    
    # find the set of events associated with the predominant structure
    def getAssociatedEvents(self, angle, threshold):
        # get the locations of all events associated with the max metric projection
        maxMetricProjection = self.flowPlanes[self.getMaxMetricIndex()]
        assocEvents = maxMetricProjection.findAssocEvents(threshold)

        # if we have iterations of refinement left to do
        # create a new flow plane module with a smaller angle to refine the projection
        if self.c > 0:
            self.childFlowPlaneModule = FlowPlaneModule(self.width, 
                self.height, 
                self.n, 
                (self.r/self.n)*2, # child plane should cover adjacent planes and then some
                self.c-1,
                angle)

            # project associated events onto the new flow plane module
            for e in assocEvents:
                self.childFlowPlaneModule.projectEvent(e)
            
            # get the events associated with the refined projection
            self.childFlowPlaneModule.updateMetrics()
            return self.childFlowPlaneModule.getAssociatedEvents(
                self.childFlowPlaneModule.flowPlanes[self.childFlowPlaneModule.getMaxMetricIndex()].normal, 
                threshold)
        
        # otherwise, return the events we've already collected and the angle of projection
        else:
            return (assocEvents, maxMetricProjection.normal)

    # clear all the flow planes
    def clear(self):
        self.flowPlanes = {
            (i, j): self.createFlowPlane(i, j)
            for (i, j) in self.flowPlaneIndices}
        self.childFlowPlaneModule = None
    
    def createFlowPlane(self, i, j):
        return FlowPlane(self.width, self.height, 
                    ((i-(self.n-1)/2)*self.r/self.n + self.centerAngle[0], 
                    (j-(self.n-1)/2)*self.r/self.n + self.centerAngle[1]) )
            

# Flow plane consists of a plane and a normal onto which events are projected
# and summed to compute a metric which corresponds to how well events follow
# this plane's angle
class FlowPlane:
    def __init__(self, width, height, normal):
        self.width = width
        self.height = height
        self.normal = normal
        self.eventPolarities = np.zeros((width, height), np.int)
        self.projectedEvents = [[ [] for i in range(height)] for j in range(width)]
        self.metric = 0
    
    # project the event onto this plane
    def projectEvent(self, e):
        (x, y) = FlowGenerator.projectUVOntoPlane(e.x, e.y, e.t, self.normal, self.width, self.height)

        # add the event to the plane if it is within bounds
        if (x >= 0 and x < self.width and y >= 0 and y < self.height):
            self.eventPolarities[x][y] += e.p # assume p can only be +/-1
            self.projectedEvents[x][y].append(e)
    
    # update metric (sum of the square of the sum at each location in the plane) 
    def updateMetric(self):
        self.metric = np.sum(np.square(self.eventPolarities))

    # get events at locations where f(x, y) > ave + stdDev*w in flowPlanes[projIndex]
    # TODO: and connected locations by flood fill
    def findAssocEvents(self, threshold):
        events = []

        average = np.average(self.eventPolarities)
        stdDev = np.std(self.eventPolarities)

        # iterate through locations in the chosen projection and add them if significant
        for i in range(self.width):
            for j in range(self.height):
                if abs(self.eventPolarities[i][j]) > average + stdDev*threshold:
                    events.extend(self.projectedEvents[i][j])

        return events
