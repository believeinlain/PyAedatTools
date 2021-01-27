
from collections import namedtuple
from math import sqrt

class TightCluster:
    def __init__(self, x, y, t):
        self.x = x
        self.y = y
        self.t = t
        self.tightness = 1.0

    def isInRangeSq(self, x, y, rangeSq):
        return ( (self.x-x)**2 + (self.y-y)**2 ) <= rangeSq
    
    def getDistTo(self, x, y):
        return sqrt( (self.x-x)**2 + (self.y-y)**2 ) 

class TightClusterTracker:
    def __init__(self, clusterRange, shiftSensitivity, tightSensitivity):
        self.range = clusterRange # should be a decent sized integer
        self.rangeSq = clusterRange**2
        self.shiftSens = shiftSensitivity # should be a small fraction
        self.tightSens = tightSensitivity # should be a small fraction
        self.clusters = []
    
    def processEvent(self, x, y, t, p):
        # TODO: expire old clusters
        clustersInRange = [c for c in self.clusters if c.isInRangeSq(x, y, self.rangeSq)]

        if len(clustersInRange) == 0:
            # create new cluster
            self.clusters.append(TightCluster(x, y, t))

        elif len(clustersInRange) == 1:
            # assign to the one cluster
            self.assignEventToCluster(x, y, clustersInRange[0])
        else:
            # merge the multiple clusters by assigning the event to the tightest one and removing the others
            tightestCluster = clustersInRange[0]
            for c in clustersInRange[1:]:
                if c.tightness > tightestCluster.tightness:
                    tightestCluster = c
            
            # remove all but the tightest cluster from self.clusters
            clustersInRange.remove(tightestCluster)
            self.clusters = [c for c in self.clusters if c not in clustersInRange]

            self.assignEventToCluster(x, y, tightestCluster)
            

    def assignEventToCluster(self, x, y, cluster):
        dist = cluster.getDistTo(x, y)
        # compute new tightness as the weighted average between current tightness and the inverse
        # of the relative distance as a fraction of range
        tightnessChangeFactor = 100 if dist==0 else (self.range/dist)
        cluster.tightness = (1-self.tightSens)*cluster.tightness + tightnessChangeFactor*self.tightSens
        cluster.x += int( (x-cluster.x) * self.shiftSens )
        cluster.y += int( (y-cluster.y) * self.shiftSens )
    
    def getClusterCenters(self):
        return [(c.x, c.y) for c in self.clusters]