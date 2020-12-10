
from PyAedatTools import ImportAedat
from PyAedatTools import OpticalFlowPlayback

from math import pi

# Create a dict with which to pass in the input parameters.
aedat = {}
aedat['importParams'] = {}

filename = "IMU_translBoxes.aedat"

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
    'caption': "Optical Flow Analysis",
    'width': 350,
    'height': 265,
    'playbackSpeed': 100,
    'fadeRate': 10,
    'frameStep': 30
}

flowGeneratorArgs = {
    'projRes': 11, 
    'projAng': pi,
    'maxConvergenceThreshold': 1000,
    'eventAssociationThreshold': 1,
    'successiveProjectionScale': 0.1,
    'numSuccessiveProjections': 3
}

# playback the event data
OpticalFlowPlayback.playOpticalFlow(eventData, eventPlaybackArgs, flowGeneratorArgs)
