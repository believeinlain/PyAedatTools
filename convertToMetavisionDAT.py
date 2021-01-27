
import sys
import numpy as np
from PyAedatTools import ImportAedat

import datetime

# Create a dict with which to pass in the input parameters.
aedat = {}
aedat['importParams'] = {}

# Put the filename, including full path, in the 'filePath' field.
filename = "example_data/Davis346red-2020-06-12T12-31-10-0700-0_Test_7.aedat"

aedat['importParams']['filePath'] = "./"+filename

# Invoke the function
aedat = ImportAedat.ImportAedat(aedat)

polarityData = aedat['data']['polarity']
numEvents = aedat['info']['numEventsInFile']

# write the imported data to a file
# in metavision DAT format
with open(filename[:-5]+'dat', 'wb') as f:
    # print header text
    f.write('% Data file containing CD events\n'.encode('ascii'))
    f.write(('% Date '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'\n').encode('ascii'))
    f.write('% Version 2\n'.encode('ascii'))
    f.write('% Width 350\n'.encode('ascii'))
    f.write('% Height 265\n'.encode('ascii'))

    # write binary data
    f.write(bytes(0x0C)) # event type: EventCd
    f.write(bytes(0x08)) # event size: 8

    data = np.zeros(numEvents, dtype=np.uint64)
    # timestamp: bits 63-32 (32 bit signed int)
    timeStamp = np.bitwise_and(
        np.full(numEvents, 0xFFFFFFFF00000000, dtype=np.uint64),
        np.left_shift(
            np.subtract(np.array(polarityData['timeStamp'], dtype=np.uint64), polarityData['timeStamp'][0]), 32))
    np.bitwise_or(data, timeStamp, out=data)

    # x = np.bitwise_and(
    #     np.full(numEvents, 0x0000000000003FFF, dtype=np.uint64),
    #     np.left_shift(
    #         np.array(polarityData['x'], dtype=np.uint64), 0))
    # np.bitwise_or(data, x, out=data)

    # y = np.bitwise_and(
    #     np.full(numEvents, 0x000000000FFFC000, dtype=np.uint64),
    #     np.left_shift(
    #         np.array(polarityData['y'], dtype=np.uint64), 14))
    # np.bitwise_or(data, y, out=data)
    
    # polarity = np.bitwise_and(
    #     np.full(numEvents, 0x00000000F0000000, dtype=np.uint64),
    #     np.left_shift(
    #         np.array(polarityData['polarity'], dtype=np.uint64), 28))
    # np.bitwise_or(data, polarity, out=data)
    
    x = np.bitwise_and(
        np.full(numEvents, 0x00000000FFFC0000, dtype=np.uint64),
        np.left_shift(
            np.array(polarityData['x'], dtype=np.uint64), 18))
    np.bitwise_or(data, x, out=data)

    y = np.bitwise_and(
        np.full(numEvents, 0x000000000003FFF0, dtype=np.uint64),
        np.left_shift(
            np.array(polarityData['y'], dtype=np.uint64), 4))
    np.bitwise_or(data, y, out=data)
    
    polarity = np.bitwise_and(
        np.full(numEvents, 0x000000000000000F, dtype=np.uint64),
        np.array(polarityData['polarity'], dtype=np.uint64))
    np.bitwise_or(data, polarity, out=data)

    print(data[0])
    #print('{0:b}'.format(polarityData['timeStamp'][0] << 32))

    f.write(data.tobytes())

        