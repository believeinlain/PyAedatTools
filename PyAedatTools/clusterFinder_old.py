
from collections import namedtuple
from recordclass import recordclass
from numpy.linalg import norm
from random import randint

Event = namedtuple("Event", "polarity x y timeStamp lifeEnd")
Cluster = recordclass("Cluster", "x y eventArray")

# number of ms before an event is deleted
eventLifetime = 60

# number of clusters for each frame
numClusters = 3

# pick an arbitrary x and y length
# TODO: find a good way to determine these from data
xLength = 345
yLength = 260

# find clusters of events and return an array of clusters for each frame
def findClusters(eventData, frameTime=30):

    startTime = eventData['timeStamp'][0]
    #endTime = eventData['timeStamp'][eventData['numEvents']-1]-startTime
    endTime = 5000 # only do 5 seconds of frames for now

    print('Breaking events into tuples.')

    # process events into tuples
    # TODO: maybe don't
    events = []
    for i in range(eventData['numEvents']):
        events.append(Event(
            eventData['polarity'][i],
            eventData['x'][i],
            eventData['y'][i],
            eventData['timeStamp'][i]-startTime,
            eventData['timeStamp'][i]-startTime+eventLifetime
        ))

    print('Finding clusters for each frame.')

    # iterate through frames
    f = 0
    clusters = []
    for t in range(0, endTime, frameTime):
        # create a new set of clusters for this frame
        clusters.append([])
        for i in range(numClusters):
            if f == 0:
                # add a cluster at a random point
                clusters[f].append(
                    Cluster(
                        randint(0, xLength),
                        randint(0, yLength),
                        []))
            else:
                lastFrameClusters = clusters[f-1]
                for lfc in range(numClusters):
                    clusters[f].append(
                        Cluster(
                            lastFrameClusters[lfc].x,
                            lastFrameClusters[lfc].y,
                            []))

        # consider events up to time t
        for i in range(len(events)):
            currentEvent = events[i]

            # stop if we passed t
            if currentEvent.timeStamp > t:
                break

            # remove event if it's dead
            if t >= currentEvent.lifeEnd:
                events.remove(currentEvent)

            # find the cluster closest to this event
            nearestCluster = clusters[f][0]
            nearestClusterDistSquared = \
                distSquared(nearestCluster.x, nearestCluster.y,
                    currentEvent.x, currentEvent.y)
            for c in clusters[f]:
                thisDistSquared = distSquared(c.x, c.y,
                    currentEvent.x, currentEvent.y)
                if thisDistSquared < nearestClusterDistSquared:
                    nearestClusterDistSquared = thisDistSquared
                    nearestCluster = c
                # c is the cluster closest to currentEvent
                c.eventArray.append(currentEvent)

        # recenter each cluster by taking the mean of all points
        # that it is the nearest cluster to
        for c in clusters[f]:
            xSum = 0
            ySum = 0
            for e in c.eventArray:
                xSum = xSum + e.x
                ySum = ySum + e.y
            c.x = xSum/len(c.eventArray)
            c.y = ySum/len(c.eventArray)

        f = f + 1

    return clusters

def distSquared(x1, y1, x2, y2):
    return (x1-x2)**2 + (y1-y2)**2
