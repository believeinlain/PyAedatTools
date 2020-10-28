
from PyAedatTools import QuadTree
from PyAedatTools import VertexTree
from PyAedatTools import DataTypes
from DataTypes import Point

"""
corner tracking algorithm:

init:
Create empty tree to keep track of verts spatially

new event:
find neighbors in quadtree within specified distance and time
if neighbors found, attach to closest one as child (so vert should have ref to temporal root and child)


"""

class ClusterTracker:
    def __init__(self, width, height, quadTreeRes):
        self.vertexTree = None
        self.quadTree = QuadTree(Point)