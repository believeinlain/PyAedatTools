
from collections import namedtuple

event = namedtuple('event', 't p')

class CorrelativeFilter:
    def __init__(self, width, height, dt, minCorrelated):
        self.width = width
        self.height = height
        self.dt = dt
        self.minCorrelated = minCorrelated
        self.buffer = [[[] for y in range(height)] for x in range(width)]
    
    # p should be 0 for off event, 1 for on event
    # x, y should be in range width, height
    # return True if we let event through, False if event should be filtered out
    def processEvent(self, x, y, t, p):
        # count events in neighborhood
        count = 0
        for i in range(x-1, x+1):
            for j in range(y-1, y+1):
                if i>=0 and j>=0 and i<self.width and j<self.height:
                    for e in self.buffer[i][j]:
                        # remove expired events
                        if e.t+self.dt < t:
                            self.buffer[i][j].remove(e)
                        # count non-expired events
                        else:
                            count += 1
        
        # add event to buffer
        self.buffer[x][y].append(event(t, p))

        # return result
        return count>=self.minCorrelated