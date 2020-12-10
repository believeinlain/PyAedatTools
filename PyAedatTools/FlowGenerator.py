
import numpy as np

from math import ceil
from math import pi
from math import sin

from collections import namedtuple

event = namedtuple('event', 'x y t p')

# Flow Generator takes in events and assigns them flow vectors based on
# an optical flow assessment
class FlowGenerator:
    def __init__(self, 
            screenWidth, 
            screenHeight, 
            projRes, 
            projAng, 
            maxConvergenceThreshold,
            eventAssociationThreshold,
            successiveProjectionScale,
            numSuccessiveProjections, 
            projResTrackPlane,
            projAngTrackPlane,
            newCellThreshold,
            pixelLifetime):
        self.p = maxConvergenceThreshold # number of events with constant max metric to find a structure
        self.w = eventAssociationThreshold # standard deviation coefficient for events to associate with a projection
        self.flowPlaneModule = FlowPlaneModule(
            screenWidth, 
            screenHeight, 
            projRes, 
            projAng, 
            successiveProjectionScale, 
            numSuccessiveProjections)
        self.trackPlaneModule = TrackPlaneModule(
            screenWidth, 
            screenHeight, 
            projResTrackPlane, 
            projAngTrackPlane, 
            newCellThreshold, 
            pixelLifetime)

        self.maxMetricIndex = None
        self.eventsWithConstantMax = 0
        self.eventAccumulator = []

    # Takes an event and assigns it to a track plane, from which it determines
    # that event's flow vector. 
    def processNewEvent(self, x, y, t, p):
        # TODO: this is probably a bad way to cache events but can't really think of a better one rn
        # data types chosen to minimize memory usage without overflow
        e = event(np.uint16(x), np.uint16(y), np.uint32(t), np.int8(p))

        self.reprocessEvent(e)
        
    # separate function to process events already cached after identifying a new structure
    def reprocessEvent(self, e):
        # keep the event in the cache of unassociated events
        self.eventAccumulator.append(e)

        # accumulate events that don't match a track plane in the flow plane module
        self.flowPlaneModule.projectEvent(e)

        # increment events with constant max
        self.eventsWithConstantMax += 1

    # update the metrics in the flow plane module and find new track planes if applicable
    def updateFlowPlaneMetrics(self):
        # update metrics in all flow planes
        self.flowPlaneModule.updateMetrics()

        # reset eventsWithConstantMax if the maxMetricIndex changes
        if self.maxMetricIndex is None:
            self.maxMetricIndex = self.flowPlaneModule.getMaxMetricIndex()
        else:
            newMaxMetricIndex = self.flowPlaneModule.getMaxMetricIndex()
            if newMaxMetricIndex != self.maxMetricIndex:
                self.maxMetricIndex = newMaxMetricIndex
                self.eventsWithConstantMax = 0

        # identify new structure if eventsWithConstantMax > p
        if self.eventsWithConstantMax > self.p:
            self.eventsWithConstantMax = 0
            (assocEvents, normal) = self.flowPlaneModule.getAssociatedEvents(self.w)

            print("Found TrackPlane with angle ", normal)

            # remove associated events from accumulator
            self.eventAccumulator = [e for e in self.eventAccumulator if e not in assocEvents]

            # clear flow planes
            self.flowPlaneModule.clear()

            # reproject accumulated events
            for e in self.eventAccumulator:
                self.flowPlaneModule.projectEvent(e)

# Flow plane module projects events onto flow planes and computes a grid
# of metrics for events encountered so far
class FlowPlaneModule:
    def __init__(self, width, height, n, r, q, c):
        self.width = width
        self.height = height
        self.n = n # normal angles are stored in nxn grid
        self.r = r # angles in metric array range from [-r/2 to r/2]
        self.q = q
        self.c = c
        
        self.flowPlaneIndices = []
        for i in range(self.n):
            for j in range(self.n):
                self.flowPlaneIndices.append((i, j))
        
        # fill dict of flow planes (to use dict comprehension)
        # store flow planes in a dict by index tuples
        self.flowPlanes = {
            (i, j): FlowPlane(width, height, 
                    (ceil(i-self.n/2)/(self.n-1)*self.r, 
                    ceil(j-self.n/2)/(self.n-1)*self.r) )
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
    def getAssociatedEvents(self, threshold):
        # get the locations of all events associated with the max metric projection
        maxMetricProjection = self.flowPlanes[self.getMaxMetricIndex()]
        assocEvents = maxMetricProjection.findAssocEvents(threshold)

        # if we have iterations of refinement left to do
        # create a new flow plane module with a smaller angle r/q
        if self.c > 0:
            self.childFlowPlaneModule = FlowPlaneModule(self.width, self.height, self.n, self.r*self.q, self.q, self.c-1)

            # project associated events onto the new flow plane module
            for e in assocEvents:
                self.childFlowPlaneModule.projectEvent(e)
            
            # get the events associated with the refined projection
            self.childFlowPlaneModule.updateMetrics()
            return self.childFlowPlaneModule.getAssociatedEvents(threshold)
        
        # otherwise, return the events we've already collected and the angle of projection
        else:
            return (assocEvents, maxMetricProjection.normal)

    # clear all the flow planes
    def clear(self):
        self.flowPlanes = {
            (i, j): FlowPlane(self.width, self.height, 
                    (ceil(i-self.n/2)/(self.n-1)*self.r, 
                    ceil(j-self.n/2)/(self.n-1)*self.r) )
            for (i, j) in self.flowPlaneIndices}
        self.childFlowPlaneModule = None
            

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
        # break apart the normal angle into vector components
        vu = sin(self.normal[0])*self.width
        vv = sin(self.normal[1])*self.height
        # project the event onto the normal
        x = int(e.x - vu*e.t)
        y = int(e.y - vv*e.t)
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
                if self.eventPolarities[i][j] > average + stdDev*threshold:
                    events.extend(self.projectedEvents[i][j])

        return events
    
# TrackPlane module to match events to best fit projections and manage track planes
class TrackPlaneModule:
    def __init__(self, 
            width, 
            height,
            projRes, 
            projAng,
            newCellThreshold, # number of misses in a cell before declaring it valid
            pixelLifetime=3 # number of pixels to travel before events expire 
            ):
        self.width = width
        self.height = height
        self.m = projRes
        self.h = projAng
        self.p = pixelLifetime
        self.newCellThreshold = newCellThreshold

        self.trackPlanes = []

    # get the TrackPlane matching this event or None if no match
    def tryEvent(self, e):
        for tp in self.trackPlanes:
            if tp.tryEvent(e):
                # return the track plane to which this event belongs
                return tp
        
        # event did not fit any track planes
        return None

    # create a new TrackPlane
    def createNewTrackPlane(self, assocEvents, bestFitProjection):
        self.trackPlanes.append(
            TrackPlane(self.width, self.height, bestFitProjection, self.m, self.h, self.newCellThreshold, self.p))

# a TrackPlane represents a best fit velocity vector corresponding to a structure
class TrackPlane:
    def __init__(self, 
            width, 
            height, 
            normal, # best estimate projection in tuple form (radians, radians)
            projRes, 
            projAng, 
            assocEvents, # events associated with this trackplane
            newCellThreshold, # number of misses in a cell before declaring it valid
            pixelLifetime=3 # number of pixels to travel before events expire 
            ):  
        self.width = width
        self.height = height
        self.normal = normal
        self.m = projRes
        self.h = projAng
        self.p = pixelLifetime
        self.newCellThreshold = newCellThreshold
        self.assocEvents = assocEvents

        # TODO: maintain an mxm array of accumulators and cells?
        self.accumulator = {} # accumulate misses to find new valid cells
        self.validCells = set() # cells considered part of this trackplane

        # add all associated events to the set of valid cells
        for e in assocEvents:
            loc = self.projectEvent(e)
            if loc is not None:
                self.validCells.add(loc)

    # try an event against this trackplane to see if it fits
    def tryEvent(self, e):
        loc = self.projectEvent(e)
        if loc is None:
            return False
        else:
            if loc in self.validCells:
                self.assocEvents.append(e)
                return True
            else:
                # TODO: add new valid cell if accumulator goes above newCellThreshold
                # maybe keep track of missed events to add them to assocEvents later?
                self.accumulator[loc] += 1
        
        return False

    # project the event onto this plane
    def projectEvent(self, e):
        # break apart the normal angle into vector components
        vu = sin(self.normal[0])*self.width
        vv = sin(self.normal[1])*self.height
        # project the event onto the normal
        x = int(e.x - vu*e.t)
        y = int(e.y - vv*e.t)
        # return the location on the plane where the event fell
        if (x >= 0 and x < self.width and y >= 0 and y < self.height):
            return (x, y)
        else:
            return None
