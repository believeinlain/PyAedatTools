
from PyAedatTools import ImportAedat
from PyAedatTools import OpticalFlowPlayback

from math import pi

# Create a dict with which to pass in the input parameters.
aedat = {}
aedat['importParams'] = {}

filename = "Davis346red-2020-06-26T12-26-42-0700-00000195-0_Test_2.aedat"

aedat['importParams']['filePath'] = "C:/Users/saael/OneDrive/Documents/NIWC/NeuroComp/AEDATA_11-12-20/"+filename
# aedat['importParams']['filePath'] = "../../AEDATA_11-12-20/"+filename

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
    'playbackSpeed': 50,
    'fadeRate': 10,
    'frameStep': 30
}

flowGeneratorArgs = {
    'projRes': 10, 
    'projAng': pi
}

# playback the event data
OpticalFlowPlayback.playOpticalFlow(eventData, eventPlaybackArgs, flowGeneratorArgs)
