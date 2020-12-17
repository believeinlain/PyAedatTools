
import numpy as np

from math import pi
from math import tan

from collections import namedtuple
from collections import deque

from PyAedatTools import FlowPlaneModule
from PyAedatTools import TrackPlaneModule

event = namedtuple('event', 'x y t p')

# project a point in 3D (u, v, time) space onto a plane by
# collapsing the 3D space along vector normal, represented as
# an angle along the u axis and an angle along the v axis
def projectUVOntoPlane(u, v, t, normal, planeWidth, planeHeight):
    # angle scaling factor is set for the number of microseconds
    # it takes to travel 1 pixel at an angle of 45 degrees in
    # temporal space
    angleScale = 50000
    # break apart the normal angle into vector components
    vu = tan(normal[0])/angleScale
    vv = tan(normal[1])/angleScale
    # project the event onto the normal
    x = int(u - vu*t)
    y = int(v - vv*t)

    return (x, y)

# array of events indexed by screen location
# since events are sequential, they are stored in a deque for each pixel
class eventArray:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.event = [[ deque() for i in range(height)] for j in range(width)]
    
    def addEvent(self, e):
        self.event[e.x][e.y].append(e)
    
    def removeEvent(self, e):
        self.event[e.x][e.y].remove(e)

    def performOnEvents(self, func):
        for col in self.event:
            for queue in col:
                for e in queue:
                    func(e)
    
    def filterProjectedEventsByMask(self, mask, normal):
        filteredEvents = []
        for col in self.event:
            for queue in col:
                for e in queue:
                    (x, y) = projectUVOntoPlane(e.x, e.y, e.t, normal, self.width, self.height)
                    if mask[x, y] == 1:
                        filteredEvents.extend(self.event[x][y])
        
        return filteredEvents


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
            numSuccessiveProjections, 
            projResTrackPlane,
            projAngTrackPlane,
            newCellThreshold,
            pixelLifetime):
        self.width = screenWidth
        self.height = screenHeight
        self.p = maxConvergenceThreshold # number of events with constant max metric to find a structure
        self.w = eventAssociationThreshold # standard deviation coefficient for events to associate with a projection
        self.flowPlaneModule = FlowPlaneModule.FlowPlaneModule(
            screenWidth, 
            screenHeight, 
            projRes, 
            projAng,
            numSuccessiveProjections)
        self.trackPlaneModule = TrackPlaneModule.TrackPlaneModule(
            screenWidth, 
            screenHeight, 
            projResTrackPlane, 
            projAngTrackPlane, 
            newCellThreshold, 
            pixelLifetime)

        self.maxMetricIndex = None
        self.eventsWithConstantMax = 0
        self.eventAccumulator = eventArray(screenWidth, screenHeight)

    # Creates an event namedtuple and processes the event
    def processNewEvent(self, x, y, t, p):
        # TODO: this is probably a bad way to cache events but can't really think of a better one rn
        # data types chosen to minimize memory usage without overflow
        e = event(np.uint16(x), np.uint16(y), np.uint32(t), np.int8(p))

        # try to match the event to a trackplane
        tp = self.trackPlaneModule.tryEvent(e)

        # no match, so accumulate the event in search of other structures
        if tp is None:
            self.processEvent(e)
            return None
        else:
            return tp.hue
        
    # separate function to process new events or reprocess event after identifying a new structure
    def processEvent(self, e):
        # keep the event in the cache of unassociated events
        self.eventAccumulator.addEvent(e)

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
            (assocEvents, normal) = self.flowPlaneModule.getAssociatedEvents(
                self.flowPlaneModule.flowPlanes[self.maxMetricIndex].normal, self.w)

            print("\nFound TrackPlane with angle ", normal)

            # project assocEvents onto newTrackPlaneMask to floodfill
            #newTrackPlaneMask = np.zeros((self.width, self.height), np.int8)
            for e in assocEvents:
                # project it onto the mask
                #(x, y) = projectUVOntoPlane(e.x, e.y, e.t, normal, self.width, self.height)
                #newTrackPlaneMask[(x-1):(x+1), (y-1):(y+1)] = 1

                # remove associated events from accumulator
                self.eventAccumulator.removeEvent(e)
            
            # the filtered events /should/ include all assocEvents too
            #assocEvents = self.eventAccumulator.filterProjectedEventsByMask(newTrackPlaneMask, normal)

            # create a new trackplane
            self.trackPlaneModule.createNewTrackPlane(assocEvents, normal)

            # clear flow planes
            self.flowPlaneModule.clear()

            # reproject accumulated events
            self.eventAccumulator.performOnEvents(self.flowPlaneModule.projectEvent)
    
    # get a list of (hue, size, normal) tuples for all trackplanes
    def getTrackPlaneDisplayData(self):
        return [(tp.hue, len(tp.assocEvents), tp.normal, tp.validCells) for tp in self.trackPlaneModule.trackPlanes]
