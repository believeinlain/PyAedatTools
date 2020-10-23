# Arc* algorithm uses SurfaceOfActiveEvents to determine
# if an incoming event is a corner

radius = 3 # 4
Lmin = 3 # 4
Lmax = 6 # 8

# define relative pixel positions for a circle mask
# of radius 3
CircleMask3 = [
    (0, 3),
    (1, 3),
    (2, 2),
    (3, 1),
    (3, 0),
    (3, -1),
    (2, -2),
    (1, -3),
    (0, -3),
    (-1, -3),
    (-2, -2),
    (-3, -1),
    (-3, 0),
    (-3, 1),
    (-2, 1),
    (-1, 3)
]

# initialize 2d array of zero tuples where each tuple is (tr, tl)
def getInitialSAE(width, height):
    return [[(0, 0) for i in range(height)] for j in range(width)]

# update the SAE for a single event
def updateSAE(SAE, eventData, i, polarity, width, height, k=50):
    timeStamp = eventData['timeStamp'][i]
    x = eventData['x'][i]
    y = eventData['y'][i]
    ePolarity = eventData['polarity'][i]

    startTime = eventData['timeStamp'][0]

    # get event time relative to time 0
    t = timeStamp-startTime

    # only filter events that match desired polarity
    if ePolarity == polarity:
        # update tr only if t > tl + k
        if t > SAE[x][y][1]+k:
            SAE[x][y] = (t, SAE[x][y][1])
        # always update tl
        SAE[x][y] = (SAE[x][y][0], t)

def isEventCorner(SAE, eX, eY):
    #print("Evaluating event at ", eX, eY)
    # get circle coordinates
    Circle = [(eX+m[0], eY+m[1]) for m in CircleMask3]

    # get SAE dimensions
    width = len(SAE)
    height = len(SAE[0])

    # if circle is off the edge just quit
    # TODO: maybe handle this better?
    for c in Circle:
        if c[0] < 0 or c[0] > width:
            return False
        if c[1] < 0 or c[1] > height:
            return False

    # Initialize Anew to the newest event on the circle (by tr)
    newestIndex = 0
    newestTime = 0
    for i in range(len(Circle)):
        t = getAgeOfCircleElement(SAE, Circle, i)
        if t > newestTime:
            newestIndex = i
            newestTime = t
    
    Anew = [newestIndex]
    AnewOldestElement = newestIndex
    
    # initialize CW and CCW points
    CWIndex = newestIndex+1
    CCWIndex = newestIndex-1
    # wrap indices
    if CWIndex == len(Circle):
        CWIndex = 0
    if CCWIndex < 0:
        CCWIndex = len(Circle)-1
    
    while CCWIndex != CWIndex:
        if getAgeOfCircleElement(SAE, Circle, CWIndex) \
            > getAgeOfCircleElement(SAE, Circle, CCWIndex):
            if getAgeOfCircleElement(SAE, Circle, AnewOldestElement) \
                <= getAgeOfCircleElement(SAE, Circle, CWIndex) \
                or len(Anew) < Lmin:
                    ExpandUntilElementCW(Anew, Circle, CWIndex)
                    AnewOldestElement = GetOldestElement(SAE, Anew, Circle)
                    
            CWIndex = NextElementCW(Circle, CWIndex)
        else:
            if getAgeOfCircleElement(SAE, Circle, AnewOldestElement) \
                <= getAgeOfCircleElement(SAE, Circle, CCWIndex) \
                or len(Anew) < Lmin:
                    ExpandUntilElementCCW(Anew, Circle, CCWIndex)
                    AnewOldestElement = GetOldestElement(SAE, Anew, Circle)

            CCWIndex = NextElementCCW(Circle, CCWIndex)
    
    # if len(Anew) is between Lmin and Lmax
    # or its complementary arc is between Lmin and Lmax
    # return true, else return false
    if (len(Anew) >= Lmin and len(Anew) <= Lmax) or \
        (len(Circle)-len(Anew) >= Lmin and len(Circle)-len(Anew) <=Lmax):
        return True
    else:
        return False

# get next clockwise element
def NextElementCW(Circle, Index):
    next = Index + 1
    if next == len(Circle):
        next = 0
    return next

# get next counterclockwise element
def NextElementCCW(Circle, Index):
    next = Index - 1
    if next < 0:
        next = len(Circle)-1
    return next

# helper function to make code more readable
def getAgeOfCircleElement(SAE, Circle, Index):
    #print(Circle[Index][0], Circle[Index][1])
    return SAE[Circle[Index][0]][Circle[Index][1]][0]

# expand Anew to Index
def ExpandUntilElementCW(Anew, Circle, Index):
    end = Anew[len(Anew)-1]
    while end != Index:
        end = NextElementCW(Circle, end)
        Anew.append(end)

def ExpandUntilElementCCW(Anew, Circle, Index):
    end = Anew[0]
    while end != Index:
        end = NextElementCCW(Circle, end)
        Anew.append(end)

# return new oldest element in Anew
def GetOldestElement(SAE, Anew, Circle):
    oldestIndex = 0
    oldestTime = 0
    for i in Anew:
        t = getAgeOfCircleElement(SAE, Circle, i)
        if t < oldestTime:
            oldestIndex = i
            oldestTime = t
    return oldestIndex
