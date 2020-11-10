
from collections import namedtuple

from PyAedatTools import QuadTree

feature = namedtuple('feature', 'x y t')

class FeatureTracker:
    def __init__(self, maxBufferSize, trackRange, noiseThreshold, dimCenter, dimWidth, dimHeight, searchRes):
        self.maxBufferSize = maxBufferSize
        self.trackRange = trackRange
        self.noiseThreshold = noiseThreshold
        self.featureBuffer = deque()
        self.featureLocations = QuadTree.QuadTree(dimCenter, dimWidth, dimHeight, searchRes)
        self.oldestEventTimestamp = 0
        
    
    # process a new feature
    def processFeature(self, x, y, t):
        # create a tuple for the new feature
        f = feature(x, y, t)

        # find existing features within trackRange
        self.featureLocations.getVerticesWithinDistance(QuadTree.point(x, y), self.trackRange)



