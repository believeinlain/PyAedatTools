
from PyAedatTools import ImportAedat
from PyAedatTools import OpticalFlowPlayback

from math import pi

# Create a dict with which to pass in the input parameters.
aedat = {}
aedat['importParams'] = {}

filename = "TranslatingSquare.aedat"

aedat['importParams']['filePath'] = "./example_data/synthesized samples/"+filename

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
    'width': 250,
    'height': 190,
    'playbackSpeed': 1,
    'fadeRate': 10,
    'frameStep': 30
}

flowGeneratorArgs = {
    'projRes': 11, 
    'projAng': pi,
    'maxConvergenceThreshold': 5000,
    'eventAssociationThreshold': 1,
    'successiveProjectionScale': 0.5,
    'numSuccessiveProjections': 1,
    'projResTrackPlane': 3,
    'projAngTrackPlane': pi/8,
    'newCellThreshold': 100,
    'pixelLifetime': 3
}

# playback the event data
OpticalFlowPlayback.playOpticalFlow(eventData, eventPlaybackArgs, flowGeneratorArgs)
