
# TODO: put these types into a different file
from collections import namedtuple
Point = namedtuple('Point', 'x y')
Vertex = namedtuple('Vertex', 't x y')

# QuadTree divides a 2d array of pixels into subquadrants no larger than minSize
# when a vertex is added new branches will be added until the size of a quadrant
# is smaller than minSize
# the tree can then be traversed to find a verts within range of a query
class QuadTree:
    def __init__(self, center, width, height, minSize=50, depth=0):
        # quadrants are indexed by self.leaf[x][y]
        self.leaf = [[None, None], [None, None]]
        self.vertices = []
        self.depth = depth
        self.width = width
        self.height = height
        self.center = center
        self.minSize = minSize
    
    # vertex should be a named tuple with fields (t, x, y)
    # recursively adds subquadrants until we've reached minSize
    def addVertex(self, vertex):
        # if we're at the min size for quadrants, just add the vertex
        if self.width < self.minSize and self.height < self.minSize:
            print("Added vertex at", vertex.x, vertex.y, "to depth", self.depth)
            self.vertices.append(vertex)
        # otherwise keep subdividing
        else:
            (subX, subY) = self.getSubQuadrant(vertex.x, vertex.y)
            # create new subtree if necessary
            if (self.leaf[subX][subY] is None):
                newCenter = self.getSubQuadrantCenter(subX, subY)
                self.leaf[subX][subY] = QuadTree(newCenter, int(self.width/2), int(self.height/2), self.minSize, self.depth+1)
            # add the vertex to the subtree
            self.leaf[subX][subY].addVertex(vertex)

    # traverse quadtree to find all vertices within distance of loc
    def getVerticesWithinDistance(self, loc, dist):
        # initialize results array
        results = []

        # if this leaf is storing vertices, then it has no subQuads
        # so just return those vertices within distance
        if len(self.vertices) > 0:
            for v in self.vertices:
                # add vertices within range (taxicab distance)
                if ( abs(loc.x - v.x) + abs(loc.y - v.y) ) <= dist:
                    results.append(v)

            return results

        # search subQuadrants within range of dist
        searchBothX = abs(self.center.x-loc.x) < dist
        searchBothY = abs(self.center.y-loc.y) < dist
        placeLoc = self.getSubQuadrant(loc.x, loc.y)
        quadrantsToSearch = [placeLoc]
        if searchBothX:
            quadrantsToSearch.append( ( int(not placeLoc[0]), placeLoc[1] ) )
        if searchBothY:
            quadrantsToSearch.append( ( placeLoc[0], int(not placeLoc[1]) ) )
        for subQuad in quadrantsToSearch:
            leaf = self.leaf[subQuad[0]][subQuad[1]]
            if leaf is not None:
                results.extend(leaf.getVerticesWithinDistance(loc, dist))
        
        return results
    
    # print the tree structure for debugging
    def printTreeStructure(self):
        if len(self.vertices) > 0:
            print("Vertices at depth: ", self.depth)
            print(self.vertices)
        
        print("Subtrees at depth: ", self.depth)
        for x in [0, 1]:
            for y in [0, 1]:
                if self.leaf[x][y]:
                    print("leaf ", x, y)
                    self.leaf[x][y].printTreeStructure()

    # find which subquadrant a given point will fall in (as tuple)
    def getSubQuadrant(self, x, y):
        xQuad = int(x > self.center.x)
        yQuad = int(y > self.center.y)
        return (xQuad, yQuad)

    # find the new center of a new subquadrant
    def getSubQuadrantCenter(self, subX, subY):
        halfX = int(self.center.x/2)
        halfY = int(self.center.y/2)
        offsetX = subX-0.5
        offsetY = subY-0.5
        return Point(x=self.center.x+offsetX*halfX, y=self.center.y+offsetY*halfY)
        