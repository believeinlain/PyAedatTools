# PyAedatTools
Tools for manipulating .aedat files (timestamped address-event data from neuromorphic hardware), in Python.

The code for importing aedat files into numpy arrays was borrowed from [simbamford's branch](https://github.com/simbamford/AedatTools), so the readme there will have more details about that particular functionality.

The focus of this repo has been to implement asynchronous optical flow using various algorithms, with the end goal of tracking objects against noisy dynamic backgrounds such as the sea or trees in wind.

## Overview

The central module for displaying and processing data is the [EventPlayback](https://github.com/believeinlain/PyAedatTools/blob/master/PyAedatTools/EventPlayback.py) module which takes eventData in the form of a dict composed of numpy arrays (as returned by the [ImportAedat](https://github.com/believeinlain/PyAedatTools/blob/master/PyAedatTools/ImportAedat.py) function, along with a number of dicts containing parameters for the tracking and data segmentation algorithms that have been implemented so far.

## Outstanding issues

Import from aedat2 currently doesn't have a good method for excluding data before any timestamp resets.

ExportAedat2 supports polarity, frames and imu6; it doesn't put xml metadata back into the file header.

In addition, much of the code has not been tested and does not have the correct syntax for Python 3.

## References

[1] Ignacio Alzugaray and Margarita Chli, <em>Asynchronous Corner Detection and Tracking for Event Cameras in Real-Time</em>
