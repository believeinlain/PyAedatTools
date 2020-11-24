# PyAedatTools
Tools for manipulating .aedat files (timestamped address-event data from neuromorphic hardware), in Python.

The code for importing aedat files into numpy arrays was borrowed from [simbamford's branch](https://github.com/simbamford/AedatTools), so the readme there will have more details about that particular functionality.

The focus of this repo has been to implement asynchronous optical flow using various algorithms, with the end goal of tracking objects against noisy dynamic backgrounds such as the sea or trees in wind.

## EventPlayback

The central module for displaying and processing data is the [EventPlayback](https://github.com/believeinlain/PyAedatTools/blob/master/PyAedatTools/EventPlayback.py) module which takes eventData in the form of a dict composed of numpy arrays (as returned by the [ImportAedat](https://github.com/believeinlain/PyAedatTools/blob/master/PyAedatTools/ImportAedat.py) function, along with a number of dicts containing parameters for the tracking and data segmentation algorithms that have been implemented so far.

# Algorithms

## Arc*

The corner detection was accomplished using the Arc* algorithm described in reference [1]. This functionality is contained in the [ArcStar](https://github.com/believeinlain/PyAedatTools/blob/master/PyAedatTools/ArcStar.py) module. To summarize, the Arc* algorithm processes each event into a "Surface of Active Events" or SAE. This surface is a 2D array that maps onto the input pixels. Each pixel contains a timestamp corresponding to its "height" on the SAE (**tr**) and the timestamp of the most recent event at this location (**tl**). **tr** will only be updated if a new event occurs more than **k** milliseconds after the last time it was updated, which serves to reduce noise. An event is then considered a corner if the contour of the SAE around it falls in an arc of length between **arcMin** and **arcMax** with radius **radius**. These parameters can be set in the **cornerTrackingArgs** argument to the EventPlayback.playEventData() function. **SAEThreshold** sets the value of **k**, and each event will be run through the Arc* algorithm once for each pass in **passArray**, and will only be considered a corner if it is considered a corner in all passes.

![Surface of Active Events](/images/SAE.png)  
Illustration of the Surface of Active Events (SAE) from reference [1]. The blue line represents the most recent event at each location, while the red line represents the surface with noise filtering.

![ArcStar](/images/ArcStar.png)
Illustration of the Arc* algorithm operating on an event from reference [1]. This image illustrates how the algorithm can detect both inside and outside corners.

## Outstanding issues

Import from aedat2 currently doesn't have a good method for excluding data before any timestamp resets.

ExportAedat2 supports polarity, frames and imu6; it doesn't put xml metadata back into the file header.

In addition, much of the code has not been tested and does not have the correct syntax for Python 3.

# References

[1] Ignacio Alzugaray and Margarita Chli, <em>Asynchronous Corner Detection and Tracking for Event Cameras in Real-Time</em>
