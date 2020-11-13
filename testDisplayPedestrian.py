
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

width = 350
height = 265

featureTrackingArgs = {
    'enable':False,
    'maxBufferSize':100,
    'trackRange':5,
    'noiseThreshold':3,
    'dimWidth':width,
    'dimHeight':height
}

clusterTrackingArgs = {
    'enable':False,
    'maxBufferSize':100,
    'newEventWeight':0.9,
    'clusteringThreshold':5,
    'numClusteringSamples':50
}

# playback the event data
EventPlayback.playEventData(eventData, (width, height), filename, featureTrackingArgs, clusterTrackingArgs)
