
# Expected event data structure
# each element of the dict is a np array
# eventData = {
#     'timeStamp': polarityData['timeStamp'],
#     'x': polarityData['x'],
#     'y': polarityData['y'],
#     'polarity': polarityData['polarity'],
#     'numEvents': polarityData['numEvents']
# }

import numpy as np

class NeuralOpticalFlow:
    def __init__(self, eventData, width, height):
        self.eventData = eventData
        self.width = width
        self.height = height
    
    # function to give to nengo node to produce input
    # since timeStamp is an int assume t represents usec
    def dvs_input(self, t):
        eventsAtTimeT = np.zeros((self.width, self.height))

