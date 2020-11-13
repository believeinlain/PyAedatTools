
import sys
import numpy as np
from PyAedatTools import ImportAedat
from PyAedatTools import EventPlayback

# Create a dict with which to pass in the input parameters.
aedat = {}
aedat['importParams'] = {}

# Put the filename, including full path, in the 'filePath' field.

filename = "Davis346red-2020-06-12T12-15-01-0700-00000195-0_Test_3_NIWC_Boat_and_SailBoat.aedat"

aedat['importParams']['filePath'] = "../../AEDATA_11-12-20/"+filename

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
    'enable':True,
    'maxBufferSize':1000,
    'trackRange':10,
    'noiseThreshold':5,
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
