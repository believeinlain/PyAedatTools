
from PyAedatTools import ImportAedat
from PyAedatTools import OpticalFlowPlayback

from math import pi

# Create a dict with which to pass in the input parameters.
aedat = {}
aedat['importParams'] = {}

filename = "Davis346red-2020-06-12T12-31-10-0700-0_Test_7.aedat"

aedat['importParams']['filePath'] = "./example_data/"+filename

# Invoke the function
aedat = ImportAedat.ImportAedat(aedat)

# create data structure to give to eventPlayback module
polarityData = aedat['data']['polarity']
eventData = {
    'timeStamp': polarityData['timeStamp'], # time is in microseconds
    'x': polarityData['x'],
    'y': polarityData['y'],
    'polarity': polarityData['polarity'],
    'numEvents': polarityData['numEvents']
}

eventPlaybackArgs = {
    'caption': "Optical Flow Analysis",
    'width': 346,
    'height': 260,
    'playbackSpeed': 0.1,
    'fadeRate': 10,
    'frameStep': 30
}

flowGeneratorArgs = {
    'projRes': 5,
    'projAng': pi,
    'maxConvergenceThreshold': 10000,
    'eventAssociationThreshold': 1,
    'numSuccessiveProjections': 2,
    'projResTrackPlane': 3,
    'projAngTrackPlane': pi/8,
    'newCellThreshold': 100,
    'pixelLifetime': 3
}

# playback the event data
OpticalFlowPlayback.playOpticalFlow(eventData, eventPlaybackArgs, flowGeneratorArgs)
