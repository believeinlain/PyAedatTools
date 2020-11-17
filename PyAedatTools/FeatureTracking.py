
from collections import deque
from collections import namedtuple

from PyAedatTools import QuadTree

feature = namedtuple('feature', 'x y t')

class FeatureTracker:
    def __init__(self, maxBufferSize, trackRange, noiseThreshold, dimWidth, dimHeight, searchRes=5):
        self.maxBufferSize = maxBufferSize
        self.trackRange = trackRange
        self.noiseThreshold = noiseThreshold
        self.featureList = []
        self.featureBuffer = deque()
        self.featureLocations = QuadTree.QuadTree(dimWidth, dimHeight, searchRes)
        self.oldestFeatureTimestamp = 0
    
    # process a new feature
    def processFeature(self, x, y, t):
        # find existing features within trackRange
        nearbyFeatures = self.featureLocations.getVerticesWithinDistance(QuadTree.point(x, y), self.trackRange)

        # create a new feature tuple
        f = feature(x, y, t)

        # add new feature to the feature buffer and location map
        self.updateFeatureBuffer(f)

        # if there are < threshold features nearby, do not track (noise rejection)
        if len(nearbyFeatures)<self.noiseThreshold:
            return

        # filter for features which are being tracked currently
        trackedFeatures = [fi for fi in nearbyFeatures if fi in self.featureList]

        # if no nearby features
        if len(trackedFeatures)==0:
            # new_track: add a new feature
            
            # add to the feature buffer with a new index
            self.featureList.append(f)
        
        # there are 1 or more nearby features
        else:
            # track_update

            # pop the nearby feature (being tracked) with the lowest index
            trackedFeatures.sort(key=lambda f: self.featureList.index(f))
            longestTracked = trackedFeatures.pop()

            # update the lowest index feature in the buffer
            # updating the timestamp will keep it from being cleaned
            # and since it will have the same index it will maintain its seniority
            self.featureList[self.featureList.index(longestTracked)] = f

            # remove the other nearby features
            # TODO: sometimes feature not in list? debug later
            for fi in trackedFeatures:
                try:
                    self.featureList.remove(fi)
                except:
                    print("Error: Feature could not be removed, not in list.")
                
        
        for f in self.featureList:
            # remove features if they are too old
            if f.t < self.oldestFeatureTimestamp:
                self.featureList.remove(f)

    # add a new feature to the buffer and update the oldestFeatureTimestamp
    # return True iff self.oldestFeatureTimestamp was updated
    def updateFeatureBuffer(self, f):
        # add new event to the buffer and location map
        self.featureBuffer.append(f)
        self.featureLocations.addVertex(f)

        # get the bufferSize
        bufferSize = len(self.featureBuffer)

        # if it's the first feature, then it is the oldest
        if bufferSize == 0:
            self.oldestFeatureTimestamp = f.t
            return True
        # if there are less than maxBufferSize features in queue then the oldest feature won't change
        elif bufferSize > self.maxBufferSize:
            # remove feature from buffer and location map
            self.featureLocations.removeVertex(self.featureBuffer.popleft())
            self.oldestFeatureTimestamp = self.featureBuffer[0].t
            return True
        
        return False


            

        



