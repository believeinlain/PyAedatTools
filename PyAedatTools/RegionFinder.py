
import numpy as np
from collections import namedtuple
import recordclass

point = namedtuple('point', 'x y')
# recordclass since we want it to be mutable
surface = recordclass('surface', 'tr tl')

# define what type of integer we will be using in case we need to change it later
integerType = np.int32
zero = integerType(0)

class SurfaceOfActiveEvents:
    def __init__(self, width, height, threshold, startTime=0):
        self.array = np.full((width, height), surface(zero, zero))
        self.threshold = threshold
        self.startTime = startTime

    def update(self, x, y, timeStamp):
        # get event time relative to startTime
        t = timeStamp-startTime

        # update tr only if t > tl + threshold
        if t > self.array[x, y].tl + threshold:
            self.array[x, y].tr = t
        # always update tl
        self.array[x, y].tl = t

class Region:
    def __init__(self, SAE):
        self.points = []
    