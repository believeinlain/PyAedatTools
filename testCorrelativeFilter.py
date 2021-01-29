
import sys
import numpy as np
from PyAedatTools import ImportAedat
from PyAedatTools import CorrelativeFilter
from PyAedatTools import SimpleEventPlayback

# Create a dict with which to pass in the input parameters.
aedat = {}
aedat['importParams'] = {}

# Put the filename, including full path, in the 'filePath' field.

# works well
correlativeFilterArgs = {
    'dt': 100000,
    'minCorrelated': 4
}
regionFinderArgs = {
    'regionLifespan': 100000,
    'SAEThreshold': 50000
}
filename = './example_data/Davis346red-2020-06-12T12-31-10-0700-0_Test_7.aedat'
# kinda works
correlativeFilterArgs = {
    'dt': 100000,
    'minCorrelated': 4
}
regionFinderArgs = {
    'regionLifespan': 100000,
    'SAEThreshold': 50000
}
filename = "C:/Users/steph/OneDrive/Documents/NIWC/NeuroComp/AEDATA_11-12-20/Davis346red-2020-06-12T12-15-01-0700-00000195-0_Test_3_NIWC_Boat_and_SailBoat.aedat"
# also works pretty decently
# correlativeFilterArgs = {
#     'dt': 100000,
#     'minCorrelated': 3
# }
# regionFinderArgs = {
#     'regionLifespan': 100000,
#     'SAEThreshold': 50000
# }
# filename = "C:/Users/steph/OneDrive/Documents/NIWC/NeuroComp/AEDATA_11-12-20/Davis346red-2020-06-12T12-24-03-0700-0_Test_5.aedat"
# really needs localized filter
# correlativeFilterArgs = {
#     'dt': 50000,
#     'minCorrelated': 3
# }
# regionFinderArgs = {
#     'regionLifespan': 50000,
#     'SAEThreshold': 50000
# }
# filename = "C:/Users/steph/OneDrive/Documents/NIWC/NeuroComp/AEDATA_11-12-20/Davis346red-2020-06-26T12-26-42-0700-00000195-0_Test_2.aedat"


aedat['importParams']['filePath'] = filename

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
    'caption': 'Boat detection',
    'width': 350,
    'height': 265,
    'playbackSpeed': 1,
    'fadeAlpha': 1,
    'frameStep': 30,
    'saveFrames': False
}

# playback the event data
SimpleEventPlayback.beginPlayback(eventData, eventPlaybackArgs, correlativeFilterArgs, regionFinderArgs)
