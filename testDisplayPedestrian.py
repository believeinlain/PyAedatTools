
import sys
import numpy as np
from PyAedatTools import ImportAedat
from PyAedatTools import EventPlayback

# Create a dict with which to pass in the input parameters.
aedat = {}
aedat['importParams'] = {}

# Put the filename, including full path, in the 'filePath' field.

filename = "3.aedat"

aedat['importParams']['filePath'] = "./example_data/"+filename

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
    'caption': filename,
    'maxBufferSize': 1000,
    'APMEnable': False,
    'APMSampleFraction': 0.5,
    'APMRadius': 5,
    'attentionThreshold': 0.05,
    'width': 350,
    'height': 265,
    'filename': filename,
    'playbackSpeed': 100,
    'blendRate': 10,
    'frameStep': 30
}

cornerTrackingArgs = {
    'passArray': [
        {'radius':3,'arcMin':3,'arcMax':6},
        {'radius':4,'arcMin':4,'arcMax':8}
    ],
    'SAEThreshold':50
}

featureTrackingArgs = {
    'enable':False,
    'maxBufferSize':100,
    'trackRange':5,
    'noiseThreshold':3
}

clusterTrackingArgs = {
    'enable':False,
    'maxBufferSize':100,
    'newEventWeight':0.9,
    'clusteringThreshold':5,
    'numClusteringSamples':50
}

# playback the event data
EventPlayback.playEventData(eventData, eventPlaybackArgs, featureTrackingArgs, clusterTrackingArgs, cornerTrackingArgs)
