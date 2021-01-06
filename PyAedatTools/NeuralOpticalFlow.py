
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
import nengo

# DS (Direction Sensitive) unit
# first, next, output neurons
# output neuron corresponds to the pixel of concern
# first neuron is at output neuron location
# next neuron is offset by 1 pixel in the direction of concern
# output produces spikes until next neuron fires, which
# inhibits it
# then first neuron can turn in back on again
# timing between being turned on and off determines the
# velocity component in that direction
#
# output spikes should be integrated until next neuron fires
# then integrator should be reset
# so we need one integrator per direction
# can we use a single neuron integrator?

# import nengo

# import numpy as np

# def dvs_input(t):
#     if (1*t)%1 == 0:
#         return np.array([10])
#     else:
#         return np.array([0])

# def dvs_input2(t):
#     if (1*t)%1 == 0.5:
#         return np.array([10])
#     else:
#         return np.array([0])
        
# n_neurons = 1

# model = nengo.Network(label="Bistable System")
# with model:
#     on = nengo.Ensemble(n_neurons, dimensions=1)
#     off = nengo.Ensemble(n_neurons, dimensions=1)
    
#     dvs = nengo.Node(dvs_input)
#     dvs2 = nengo.Node(dvs_input2)
    
#     nengo.Connection(dvs, on)
#     nengo.Connection(dvs2, off)
#     nengo.Connection(on, on, transform=[[1.1]]);
#     nengo.Connection(off, off, transform=[[1.1]]);
#     nengo.Connection(off, on.neurons, transform=[[-0.5]] * n_neurons)
#     nengo.Connection(on, off.neurons, transform=[[-0.5]] * n_neurons)

class NeuralOpticalFlow:
    def __init__(self, eventData, width, height):
        self.eventData = eventData
        self.width = width
        self.height = height
        self.lastIndex = 0 # index last used by dvs_input

        net = nengo.Network()

        with net:
            input_node = nengo.Node(self.dvs_input)

    
    # function to give to nengo node to produce input
    # since timeStamp is an int assume t represents usec
    def dvs_input(self, t):
        eventsAtTimeT = np.zeros((self.width, self.height))

        # go through events sequentially until we get to the current timestamp
        for i in range(self.lastIndex, len(self.eventData['timeStamp'])):
            # mark each event that occured at time t with a 1 in the output
            if self.eventData['timeStamp'][i] == t:
                eventsAtTimeT[self.eventData['x'][i], self.eventData['y'][i]] = 1
                self.lastIndex = i

        # return the array as a 1D vector
        return np.reshape(eventsAtTimeT, self.width*self.height)

