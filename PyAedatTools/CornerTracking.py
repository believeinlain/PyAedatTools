
from PyAedatTools import QuadTree
from QuadTree import QuadTree
from PyAedatTools import VertexTree
from VertexTree import VertexTree
from PyAedatTools import DataTypes
from DataTypes import Point

# class that tracks corners spatio-temporally to discriminate noise from objects
class CornerTracker:
    def __init__(self, width, height, quadTreeRes, trackRange, trackDeltaT):
        self.vertexTreeRoots = []
        self.quadTree = QuadTree(Point(int(width/2), int(height/2)), width, height, quadTreeRes)
        self.trackRange = trackRange
        self.trackDeltaT = trackDeltaT
    
    # process and track a new event that we know is a corner
    def processCornerEvent(self, t, x, y):
        # get neighbors within trackRange of x,y and within trackDeltaT of t
        neighbors = filter(lambda v: (t-v.t) < self.trackDeltaT, \
            self.quadTree.getVerticesWithinDistance(Point(x, y), self.trackRange) )
        
        # if no valid neighbors
        if len(neighbors)==0:
            # create a new root
            newVert = VertexTree(t, x, y)
            self.vertexTreeRoots.append(newVert)
            self.quadTree.addVertex(newVert)
        