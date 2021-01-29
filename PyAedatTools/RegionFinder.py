
import numpy as np

class SurfaceOfActiveEvents:
    def __init__(self, width, height, noiseFilter):
        self.width = width
        self.height = height
        self.k = noiseFilter
        self.tr = np.zeros((width, height), np.int)
        self.tl = np.zeros((width, height), np.int)

    def processEvent(self, x, y, t):
        # update tr only if t > tl + k
        if t > self.tl[x, y]+self.k:
            self.tr[x, y] = t
        # always update tl
        self.tl[x, y] = t

class Region:
    def __init__(self, x, y, birth, regionFinder,  lifespan):
        self.locations = [(x, y)]
        self.lifespan = lifespan
        self.finder = regionFinder
        self.birth = birth
    
    def addLocation(self, x, y):
        self.locations.append((x, y))

    def update(self, t):
        for (x, y) in self.locations:
            if t - self.finder.SAE.tr[x, y] > self.lifespan:
                self.locations.remove((x, y))
                self.finder.clearLocation(x, y)

    def getCentroid(self):
        arr = np.array(self.locations)
        length = arr.shape[0]
        sum_x = np.sum(arr[:, 0])
        sum_y = np.sum(arr[:, 1])
        return sum_x/length, sum_y/length

class RegionFinder:
    def __init__(self, width, height, regionLifespan=100000, SAEThreshold=50000):
        self.width = width
        self.height = height
        self.regionIndex = np.full((width, height), -1, np.int)
        self.regions = {}
        self.SAE = SurfaceOfActiveEvents(width, height, SAEThreshold)
        self.regionLifespan = regionLifespan
    
    def processEvent(self, x, y, t):
        # update the SAE
        self.SAE.processEvent(x, y, t)

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
                        self.regions[largestRegion].addLocation(x, y)
                assignedRegion = largestRegion
            
            elif len(adjacentRegions) == 1:
                assignedRegion = adjacentRegions.pop()

        # if there were no adjacent regions
        if assignedRegion == -1:
            # assign the event to a new region
            assignedRegion = self.createNewRegion(x, y, t)
        # actually add the location to the assigned region
        self.regions[assignedRegion].addLocation(x, y)

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
        # assign the index to the location
        self.regionIndex[x][y] = index
        # create a new region with that index
        self.regions[index] = Region(x, y, t, self, self.regionLifespan)
        # return the index of the new region
        return index

    def getOldestRegion(self):
        return self.regions[min(self.regions, key=lambda i: self.regions[i].birth)]
            
