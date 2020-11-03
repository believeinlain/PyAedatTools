
from PyAedatTools import QuadTree
from PyAedatTools import VertexTree
from PyAedatTools import DataTypes

from math import atan2
from math import pi

# class that tracks corners spatio-temporally to discriminate noise from objects
class CornerTracker:
    def __init__(self, width, height, quadTreeRes, trackRange, trackDeltaT, maxAge, threshold):
        self.vertexTreeRoots = []
        self.quadTree = QuadTree.QuadTree(DataTypes.Point(int(width/2), int(height/2)), width, height, quadTreeRes)
        self.trackRange = trackRange
        self.trackDeltaT = trackDeltaT
        self.maxAge = maxAge
        self.threshold = threshold
    
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
        root = newVert.prune(self.vertexTreeRoots, self.quadTree, self.maxAge, self.threshold, t)

        if root is not None:
            # now we can compare the root to the new event to get velocity
            dt = float(t)-float(root.t)
            dx = float(x)-float(root.x)
            dy = float(y)-float(root.y)

            # find and return the angle of trajectory (from 0 to 1)
            return ( atan2(dx/dt, dy/dt)+pi ) / (2*pi)
        else:
            return None
        

        