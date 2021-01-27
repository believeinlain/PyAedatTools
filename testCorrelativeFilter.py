
import sys
import numpy as np
from PyAedatTools import ImportAedat
from PyAedatTools import CorrelativeFilter
from PyAedatTools import SimpleEventPlayback

# Create a dict with which to pass in the input parameters.
aedat = {}
aedat['importParams'] = {}

# Put the filename, including full path, in the 'filePath' field.

# filename = "Davis346red-2020-06-12T12-15-01-0700-00000195-0_Test_3_NIWC_Boat_and_SailBoat.aedat"
filename = 'Davis346red-2020-06-12T12-31-10-0700-0_Test_7.aedat'
aedat['importParams']['filePath'] = './example_data/'+filename

# filename = 'boat_filtered.aedat'
# aedat['importParams']['filePath'] = './example_data/'+filename

# Invoke the function
aedat = ImportAedat.ImportAedat(aedat)

# create data structure to give to eventPlayback module
polarityData = aedat['data']['polarity']
eventData = {
    'timeStamp': polarityData['timeStamp'],
    'x': polarityData['x'],
    'y': polarityData['y'],
    'polarity': polarityData['polarity'],
    'numEvents': polarityData['numEvents']
}

eventPlaybackArgs = {
    'caption': 'Correlative filter',
    'width': 350,
    'height': 265,
    'playbackSpeed': 2,
    'fadeAlpha': 1,
    'frameStep': 60
}

correlativeFilterArgs = {
    'dt': 100000,
    'numMustBeCorrelated': 3
}

# playback the event data
SimpleEventPlayback.beginPlayback(eventData, eventPlaybackArgs, correlativeFilterArgs)
