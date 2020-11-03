
from PyAedatTools import QuadTree
from PyAedatTools import VertexTree
from PyAedatTools import DataTypes

from math import atan2
from math import pi

# class that tracks corners spatio-temporally to discriminate noise from objects
# width, height: dimensions of region in pixels
# quadTreeRes: how small to divide the quadTree (smaller res = more memory usage but faster search)
# trackRange: range around each event to search for vertices to attach to
# trackDeltaT: timeframe to search before each event for vertices to attach to
# maxAge: how old should we need a root to be before tracking a corner
# threshold: branches in which the youngest vertex is older than threshold will be pruned
# maxAge: roots older than this will just be removed if they haven't been pruned yet
class CornerTracker:
    def __init__(self, width, height, quadTreeRes, trackRange, trackDeltaT, minAge, threshold, maxAge):
        self.vertexTreeRoots = []
        self.quadTree = QuadTree.QuadTree(DataTypes.Point(int(width/2), int(height/2)), width, height, quadTreeRes)
        self.trackRange = trackRange
        self.trackDeltaT = trackDeltaT
        self.minAge = minAge
        self.threshold = threshold
        self.maxAge = maxAge
    
    # process and track a new event that we know is a corner
    def processCornerEvent(self, t, x, y):
        # get neighbors within trackRange of x,y and within trackDeltaT of t
        neighbors = [v for v in self.quadTree.getVerticesWithinDistance(DataTypes.Point(x, y), self.trackRange) \
            if (t-v.t) < self.trackDeltaT]
        
        # if no valid neighbors
        if len(neighbors)==0:
            # create a new root
            newVert = VertexTree.VertexTree(t, x, y)
            self.vertexTreeRoots.append(newVert)
        else:
            # attach to the closest neighbor
            newVert = min({(int(n.x)-x)**2+(int(n.y)-y)**2:n for n in neighbors}.items())[1].birth(t, x, y)
        
        # add new vert to quadTree
        self.quadTree.addVertex(newVert)

        # prune the tree and get the oldest root if it was older than maxAge
        root = newVert.prune(self.vertexTreeRoots, self.quadTree, self.minAge, self.threshold, t)

        if root is not None:
            # now we can compare the root to the new event to get velocity
            dt = float(t)-float(root.t)
            dx = float(x)-float(root.x)
            dy = float(y)-float(root.y)

            # find and return the angle of trajectory (from 0 to 1)
            return ( atan2(dx/dt, dy/dt)+pi ) / (2*pi)
        else:
            return None
    
    # remove stray roots
    def cleanRoots(self, currentTime):
        for root in self.vertexTreeRoots:
            if currentTime - root.t > self.maxAge:
                root.delete(self.vertexTreeRoots, self.quadTree)
        