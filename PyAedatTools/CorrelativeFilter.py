
import numpy as np

class CorrelativeFilter:
    def __init__(self, width, height, SAE, dt, n):
        self.width = width
        self.height = height
        self.SAE = SAE
        self.dt = dt
        self.n = n
        # for now just set bufferdepth to n
        self.bufferDepth = n
        # buffer of timestamps of the most recent events for each location
        self.buffer = np.zeros((width, height, self.bufferDepth), np.uint32)
        # index of the height above the most recent event for a location
        self.bufferTop = np.zeros((width, height), np.uint8)
        # keep a reference of the polarity of received events
        self.polarity = np.zeros((width, height, self.bufferDepth), np.uint8)

    def addEventToBuffer(self, x, y, t, p):
        top = self.bufferTop[x, y]
        self.buffer[x, y, top] = t
        self.polarity[x, y, top] = p
        top = ( top+1 )%self.bufferDepth
        self.bufferTop[x, y] = top

    # get the number of past events within dt from t at location x, y
    def countBufferHeight(self, x, y, t, dt):
        top = self.bufferTop[x, y]
        count = 0
        # start from the current top (self.bufferTop[x, y]) and go backwards
        # until the events are not within dt from t
        # don't count zeros
        # for i in reversed(range(top, top+self.bufferDepth)):
        #     b = self.buffer[x, y, i%self.bufferDepth]
        #     if b!=0 and b+dt >= t:
        #         count+=1
        #     else:
        #         break
        for i in range(0, self.bufferDepth):
            b = self.buffer[x, y, i]
            if b!=0 and b+dt >= t:
                count+=1
        
        return count
    
    def processEvent(self, x, y, t, p):
        # start count at -1 to cancel current event
        count = -1
        self.addEventToBuffer(x, y, t, p)
        # localDensity = self.SAE.getLocalDensity(x, y, t, 5, 50000)
        n = self.n
        dt = self.dt

        # get the buffer height at each location
        for i in range(x-1, x+2):
            if i>=0 and i<self.width:
                for j in range(y-1, y+2):
                    if j>=0 and j<self.height:
                        loc = self.countBufferHeight(i, j, t, dt)
                        count += loc
                        # if 300<x<320 and 145<y<165:
                        #     print(x, y, i, j, loc, count)
                        # if we've reached n we can stop counting
                        if count >= n:
                            return True
        
        return False