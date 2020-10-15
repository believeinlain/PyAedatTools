# -*- coding: utf-8 -*-
"""
Example script for how to invoke the ImportAedat function
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from ImportAedat import ImportAedat


# Create a dict with which to pass in the input parameters.
aedat = {}
aedat['importParams'] = {}

# Put the filename, including full path, in the 'filePath' field.

filename = "3.aedat"

# aedat['importParams']['filePath'] = '/home/steph/aedata/Pedestrian Detection/Raw pedestrian data/'+filename
aedat['importParams']['filePath'] = "C:/Users/saael/OneDrive/Documents/NIWC/NeuroComp/Miao_data/Pedestrian Detection/Raw pedestrian data/"+filename
# aedat['importParams']['fileFormat'] = 'DAVIS'

# Invoke the function
aedat = ImportAedat(aedat)

# create data structure to give to eventPlayback module
polarityData = aedat['data']['polarity']
eventData = {
    'timeStamp': polarityData['timeStamp'],
    'x': polarityData['x'],
    'y': polarityData['y'],
    'polarity': polarityData['polarity'],
    'numEvents': polarityData['numEvents']
}

# playback the event data
from eventPlayback import playEventData

playEventData(eventData, filename)
