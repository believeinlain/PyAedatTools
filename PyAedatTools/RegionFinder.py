
import numpy as np

from PyAedatTools import SurfaceOfActiveEvents

class Region:
    def __init__(self, x, y, birth, regionFinder,  lifespan):
        self.locations = [(x, y)]
        self.lifespan = lifespan
        self.finder = regionFinder
        self.birth = birth
        self.centroid = (0, 0)
    
    def addLocation(self, x, y):
        # calculate the new centroid
        mass = len(self.locations)
        if mass==0:
            self.centroid = (x, y)
        else:
            newEventWeight = 1/mass
            (cx, cy) = self.centroid
            cx += (x-cx)*newEventWeight
            cy += (y-cy)*newEventWeight
            self.centroid = (cx, cy)

        # add the new location
        self.locations.append((x, y))

    # TODO: update centroid on event removal?
    def update(self, t):
        # clear expired locations
        for (x, y) in self.locations:
            if t - self.finder.SAE.tr[x, y] > self.lifespan:
                self.locations.remove((x, y))
                self.finder.clearLocation(x, y)

    def mergeInto(self, other):
        # calculate the new centroid
        # mass = len(self.locations)
        # otherMass = len(other.locations)
        # if mass==0:
        #     self.centroid = other.centroid
        # else:
        #     newRegionWeight = otherMass/mass
        #     (cx, cy) = self.centroid
        #     (ox, oy) = other.centroid
        #     cx += (ox-cx)*newRegionWeight
        #     cy += (oy-cy)*newRegionWeight
        #     self.centroid = (cx, cy)
        
        # add the new location
        for (x, y) in other.locations:
            self.addLocation(x, y)
            # self.locations.append((x, y))

    def getCentroid(self):
        return self.centroid

class RegionFinder:
    def __init__(self, width, height, SAE, regionLifespan=100000):
        self.width = width
        self.height = height
        self.regionIndex = np.full((width, height), -1, np.int)
        self.regions = {}
        self.SAE = SAE
        self.regionLifespan = regionLifespan
    
    def processEvent(self, x, y, t):
        # assign the event to the region at (x, y)
        assignedRegion = self.regionIndex[x][y]
        # if the location is not already part of a region
        if assignedRegion == -1:
            # check adjacent locations for a region
            adjacentRegions = set()
            for i in range(x-2, x+3):
                for j in range(y-2, y+3):
                    if i!=x and j!=y and i>=0 and j>=0 and i<self.width and j<self.height:
                        if self.regionIndex[i][j] != -1:
                            adjacentRegions.add(self.regionIndex[i][j])
            
            if len(adjacentRegions) > 1:
                # find the largest region
                largestRegion = max(adjacentRegions, key=lambda i: len(self.regions[i].locations))
                # merge all adjacent regions into the largest one
                adjacentRegions.remove(largestRegion)
                for r in adjacentRegions:
                    for (x, y) in self.regions[r].locations:
                        self.regionIndex[x, y] = largestRegion
                    self.regions[largestRegion].mergeInto(self.regions[r])

                assignedRegion = largestRegion
            
            elif len(adjacentRegions) == 1:
                assignedRegion = adjacentRegions.pop()

        # if there were no adjacent regions
        if assignedRegion == -1:
            # assign the event to a new region
            assignedRegion = self.createNewRegion(x, y, t)
        # actually add the location to the assigned region
        self.regions[assignedRegion].addLocation(x, y)
        
        # assign the index to the location
        self.regionIndex[x][y] = assignedRegion

        return assignedRegion
    
    def updateRegions(self, t):
        keys = list(self.regions.keys())
        for index in keys:
            self.regions[index].update(t)
            # remove empty regions
            if len(self.regions[index].locations) == 0:
                self.regions.pop(index)
    
    def clearLocation(self, x, y):
        self.regionIndex[x, y] = -1
    
    def createNewRegion(self, x, y, t):
        # find a region index that isn't being used
        index = 0
        while index in self.regions:
            index += 1
        # create a new region with that index
        self.regions[index] = Region(x, y, t, self, self.regionLifespan)
        # return the index of the new region
        return index

    def getOldestRegion(self):
        return self.regions[min(self.regions, key=lambda i: self.regions[i].birth)]
            
