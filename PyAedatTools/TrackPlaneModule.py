
import ColorWheel

from PyAedatTools import FlowGenerator

# TrackPlane module to match events to best fit projections and manage track planes
class TrackPlaneModule:
    def __init__(self, 
            width, 
            height,
            projRes, 
            projAng,
            newCellThreshold, # number of misses in a cell before declaring it valid
            pixelLifetime # number of pixels to travel before events expire 
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
            TrackPlane(self.width, self.height, bestFitProjection, self.m, self.h, assocEvents, self.newCellThreshold, self.p))

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
            pixelLifetime # number of pixels to travel before events expire 
            ):  
        self.width = width
        self.height = height
        self.normal = normal
        self.m = projRes
        self.h = projAng
        self.p = pixelLifetime
        self.newCellThreshold = newCellThreshold
        self.assocEvents = assocEvents
        self.hue = ColorWheel.getNextHue() # give each trackplane a unique color

        # TODO: maintain an mxm array of accumulators and cells?
        self.accumulator = {} # accumulate misses to find new valid cells
        self.validCells = set() # cells considered part of this trackplane

        # add all associated events to the set of valid cells
        for e in self.assocEvents:
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
                if loc in self.accumulator: 
                    self.accumulator[loc] += 1
                else:
                    self.accumulator[loc] = 1
        
        return False

    # project the event onto this plane
    def projectEvent(self, e):
        (x, y) = FlowGenerator.projectUVOntoPlane(e.x, e.y, e.t, self.normal, self.width, self.height)

        # return the location on the plane where the event fell
        if (x >= 0 and x < self.width and y >= 0 and y < self.height):
            return (x, y)
        else:
            return None
