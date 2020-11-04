
class VertexTree:
    def __init__(self, t, x, y, parent=None):
        self.t = t
        self.x = x
        self.y = y
        self.parent = parent
        self.children = []
        # link on init if necessary
        if self.parent is not None:
            self.parent.children.append(self)
    
    # delete this vertex and all its children and remove them
    # from the QuadTree as well
    def strip(self, quadTree):
        # remove reference to self from quadTree
        quadTree.removeVertex(self)
        # recursively delete all children
        for child in self.children:
            child.strip(quadTree)
        self.children.clear()

        # delete reference to self by parent
        if self.parent is not None:
            self.parent.children.remove(self)
    
    # find oldest root, and strip all branches that don't have
    # leaves younger than threshold. If the oldest root is 
    # older than maxAge, kill it
    # returns oldest root we just killed
    def prune(self, rootList, quadTree, minAge, maxAge, threshold, currentTime):
        # strip branches if they don't have young enough children
        for child in self.children:
            if (currentTime - child.getYoungestChild().t) > threshold:
                child.strip(quadTree)
                self.children.remove(child)
        # recursively find oldest root
        if self.parent is not None:
            return self.parent.prune(rootList, quadTree, minAge, maxAge, threshold, currentTime)
        # this must be the oldest root
        else:
            # if it's old enough return it, delete if too old
            age = currentTime - self.t
            if age > maxAge:
                return self.delete(rootList, quadTree)
            elif age > minAge:
                return self
        
        return None
    
    # produce and return a new child
    def birth(self, t, x, y):
        newVert = VertexTree(t, x, y, self)
        self.children.append(newVert)
        return newVert
    
    # delete this tree node and all references to it
    def delete(self, rootList, quadTree):
        # remove all references to this root
        # but don't strip
        for child in self.children:
            child.parent = None
            # add each child to rootList since they will be roots now
            rootList.append(child)
        # remove the old root from rootList and quadTree since it's dead
        quadTree.removeVertex(self)
        rootList.remove(self)
        return self
    
    # recursively find the youngest child in all the branches
    def getYoungestChild(self):
        youngestChild = self # if no children it will be this
        maxT = 0
        for child in self.children:
            youngestChildInBranch = child.getYoungestChild()
            if youngestChildInBranch.t > maxT:
                youngestChild = youngestChildInBranch
                maxT = youngestChild.t
        
        return youngestChild
    
