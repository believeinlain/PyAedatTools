
from collections import deque
from collections import namedtuple

from random import sample

from heapq import merge

event = namedtuple('event', 'x y t')

class Cluster:
    def __init__(self, firstEvent):
        self.events = [firstEvent]
        self.x = firstEvent.x
        self.y = firstEvent.y

    # add a new event to this cluster
    def addEvent(self, e, eventWeight):
        self.events.append(e)
        self.updateCentroid(e, eventWeight)
    
    # update centroid weighted average
    def updateCentroid(self, e, eventWeight):
        self.x = int((eventWeight*float(e.x) + (1-eventWeight)*float(self.x)))
        self.y = int((eventWeight*float(e.y) + (1-eventWeight)*float(self.y)))

    # remove events with timestamp <= oldestEventTimestamp
    # return True iff there are any events left
    def removeOldEvents(self, oldestEventTimestamp):
        self.events = list(filter(lambda e: e.t > oldestEventTimestamp, self.events))
        return len(self.events)>0
    
    # sample numClusteringSamples from self.events and if any are
    # closer than clusteringThreshold by manhattan distance return True
    def isCloseToEvent(self, x, y, clusteringThreshold, numClusteringSamples):
        # compare proximity to the centroid
        if ( abs(x - self.x) + abs(y - self.y) ) <= clusteringThreshold:
            return True
        
        for e in ( sample(self.events, numClusteringSamples) if len(self.events)>numClusteringSamples else self.events ):
            # compare proximity to a sample of events
            if ( abs(x - e.x) + abs(y - e.y) ) <= clusteringThreshold:
                return True
        
        return False
    
    # merge this cluster with other together
    def mergeClusters(self, other):
        # merge event list while keeping sorted by timestamp
        self.events = list(merge(self.events, other.events, key=lambda e: e.t))

        # merge the clusters together with even weight
        self.x = int( (float(other.x) + float(self.x)) / 2)
        self.y = int( (float(other.y) + float(self.y)) / 2)


# maxBufferSize: max number of events to keep in eventBuffer
# newEventWeight[0-1]: weight to give new event when adjusting centroid of cluster
# clusteringThreshold: proximity required between an event and cluster to merge
# numClusteringSamples: number of events to sample when measuring dist from event to cluster
class ClusterTracker:
    def __init__(self, maxBufferSize, newEventWeight, clusteringThreshold, numClusteringSamples):
        self.clusters = []
        self.eventBuffer = deque()
        self.oldestEventTimestamp = 0
        self.maxBufferSize = maxBufferSize
        self.newEventWeight = newEventWeight
        self.clusteringThreshold = clusteringThreshold
        self.numClusteringSamples = numClusteringSamples

    # process a new event
    def processEvent(self, x, y, t):
        # create a new event tuple to store in buffer and reference elsewhere
        e = event(x, y, t)

        self.updateEventBuffer(e)

        proximityList = []
        
        # TODO: redo using list comprehension?
        for c in self.clusters:
            # remove old events from clusters
            # if no events left, we don't have a cluster
            if not c.removeOldEvents(self.oldestEventTimestamp):
                self.clusters.remove(c)

            # evaluate cluster proximity
            if c.isCloseToEvent(x, y, self.clusteringThreshold, self.numClusteringSamples):
                # add to proximity list if this event is close
                proximityList.append(c)

        if len(proximityList) == 0:
            # create a new cluster
            self.clusters.append(Cluster(e))

        else:
            # merge clusters in proximityList together if there's more than one
            while len(proximityList)>1:
                clusterToMerge = proximityList.pop()
                proximityList[0].mergeClusters(clusterToMerge)
                self.clusters.remove(clusterToMerge)
            
            # then add the event to the merged cluster
            proximityList[0].addEvent(e, self.newEventWeight)
    
    # add a new event to the buffer and update the oldestEventTimestamp
    # return True iff self.oldestEventTimestamp was updated
    def updateEventBuffer(self, e):
        # add new event to the queue
        self.eventBuffer.append(e)

        # get the eventBufferSize
        bufferSize = len(self.eventBuffer)

        # if it's the first event, then it is the oldest event
        if bufferSize == 0:
            self.oldestEventTimestamp = e.t
            return True
        # if there are less than maxBufferSize events in queue then the oldest event won't change
        # otherwise we return the age of the oldest event (technically not the oldest in buffer
        # since we remove it but should be fine)
        elif bufferSize > self.maxBufferSize:
            self.oldestEventTimestamp = self.eventBuffer.popleft().t
            return True
        
        return False
        