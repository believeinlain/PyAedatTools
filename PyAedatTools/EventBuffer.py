
from collections import deque
from collections import namedtuple

event = namedtuple('event', 'x y t')

class EventBuffer:
    def __init__(self, maxSize):
        self.queue = deque()
        self.maxSize = maxSize
        self.oldestTimestamp = 0
    
    # add a new event to the buffer and update the oldestTimestamp
    # return True iff self.oldestTimestamp was updated
    def update(self, e):
        # add new event to the queue
        self.queue.append(e)

        # get the eventBufferSize
        bufferSize = len(self.queue)

        # if it's the first event, then it is the oldest event
        if bufferSize == 0:
            self.oldestTimestamp = e.t
            return True
        # if there are less than maxBufferSize events in queue then the oldest event won't change
        # otherwise we return the age of the oldest event (technically not the oldest in buffer
        # since we remove it but should be fine)
        elif bufferSize > self.maxSize:
            self.oldestTimestamp = self.queue.popleft().t
            return True
        
        return False
