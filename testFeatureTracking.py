
import sys
import numpy as np
from PyAedatTools import ImportAedat
from PyAedatTools import EventPlayback

# Create a dict with which to pass in the input parameters.
aedat = {}
aedat['importParams'] = {}

# Put the filename, including full path, in the 'filePath' field.

#filename = "Davis346red-2020-06-12T12-15-01-0700-00000195-0_Test_3_NIWC_Boat_and_SailBoat.aedat"
filename = "Davis346red-2020-06-26T12-26-42-0700-00000195-0_Test_2.aedat"

aedat['importParams']['filePath'] = "C:/Users/saael/OneDrive/Documents/NIWC/NeuroComp/AEDATA_11-12-20/"+filename
# aedat['importParams']['filePath'] = "../../AEDATA_11-12-20/"+filename

filename = 'boat_filtered.aedat'

aedat['importParams']['filePath'] = './example_data/'+filename

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
    'maxBufferSize': 10000,
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
        {'radius':3,'arcMin':3,'arcMax':5},
        # {'radius':4,'arcMin':4,'arcMax':6}
    ],
    'SAEThreshold':50
}

featureTrackingArgs = {
    'enable':True,
    'maxBufferSize':5000,
    'trackRange':10,
    'noiseThreshold':5
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
