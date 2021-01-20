import nengo
import numpy as np
from nengo import Process

def dvs_input(t):
    if (1*t)%1 == 0:
        return np.array([10])
    else:
        return np.array([0])

def dvs_input2(t):
    if (1*t)%1 == 0.5:
        return np.array([10])
    else:
        return np.array([0])

class SpikeTrain(Process):
    def __init__(self, data, **kwargs):
        # data is a sorted array of timestamps for spikes
        self.data = data
        super().__init__(default_size_in=0, default_size_out=self.size_out, **kwargs)

    @property
    def size_out(self):
        return 1

    def make_step(self, shape_in, shape_out, dt, rng, state):
        assert shape_in == (0,)
        assert shape_out == (self.size_out,)

        def step_piecewise(t):
            spike_index = np.searchsorted(self.data, t)
            if spike_index >= len(self.data):
                return np.zeros(shape_out)
            elif t <= self.data[spike_index] and self.data[spike_index] < (t+dt):
                return np.full(shape_out, 0.01/dt)
            else:
                return np.zeros(shape_out)

        return step_piecewise
    
n_neurons = 200
input_gain = 10
filter_gain = 1.5
positive_fb = 2
inverse_fb = -1
filter_suppress = -1.5
max_rates = 100

n_type = nengo.neurons.LIF()
model = nengo.Network(label="Tristate")

with model:
    # create two 2D bistables
    # state 0 is when dim[0] is high, state 1 is when dim[1] is high
    A = nengo.Ensemble(
        n_neurons, 
        dimensions=2, 
        neuron_type=n_type, 
        radius=0.5, 
        normalize_encoders=True,
        intercepts=[0]*n_neurons,
        max_rates=[max_rates]*n_neurons,
        noise=None
        )
    B = nengo.Ensemble(
        n_neurons, 
        dimensions=2, 
        neuron_type=n_type, 
        radius=0.5, 
        normalize_encoders=True,
        intercepts=[0]*n_neurons,
        max_rates=[max_rates]*n_neurons,
        noise=None
        )
 
    # Create inhibitory and excitatory input streams
    exc = nengo.Node(SpikeTrain([1, 2, 4, 6, 9, 11, 12]))
    inh = nengo.Node(SpikeTrain([3, 5, 7, 8, 10]))
 
    # create input filters to be inhibited
    exc_filter = nengo.Ensemble(n_neurons, dimensions=1, neuron_type=n_type)
    inh_filter = nengo.Ensemble(n_neurons, dimensions=1, neuron_type=n_type)

    nengo.Connection(exc, exc_filter, transform=[[filter_gain]], synapse=0.01)
    nengo.Connection(inh, inh_filter, transform=[[filter_gain]], synapse=0.01)
   
    # Connect input streams to bistables A and B with gain
    nengo.Connection(exc_filter, A[0], transform=[[input_gain]], synapse=0.001)
    nengo.Connection(inh, A[1], transform=[[input_gain]], synapse=0.001)
 
    nengo.Connection(inh_filter, B[0], transform=[[input_gain]], synapse=0.001)
    nengo.Connection(exc, B[1], transform=[[input_gain]], synapse=0.001)
 
    # Connect each bistable to itself with feedback
    nengo.Connection(A, A, transform=[[positive_fb, inverse_fb], [inverse_fb, positive_fb]], synapse=0.001)
    nengo.Connection(B, B, transform=[[positive_fb, inverse_fb], [inverse_fb, positive_fb]], synapse=0.001)
  
    # when A[0] is high, inhibit B, and when B[0] is high, inihibit A
    nengo.Connection(A[0], inh_filter.neurons, transform=[[filter_suppress]]*n_neurons, synapse=0.1)
    nengo.Connection(B[0], exc_filter.neurons, transform=[[filter_suppress]]*n_neurons, synapse=0.1)
