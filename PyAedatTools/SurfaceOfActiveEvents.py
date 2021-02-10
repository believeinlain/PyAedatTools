
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
    
    # return the number of locations with events within range more recent than t-dt
    def getLocalDensity(self, x, y, t, r, dt):
        left = x-r if x-r>0 else 0
        top = y-r if y-r>0 else 0
        right = x+r+1 if x+r+1<self.width else self.width-1
        bottom = y+r+1 if y+r+1<self.height else self.height-1
        local = self.tr[left:right, top:bottom]
        return len(local[local>t-dt])

