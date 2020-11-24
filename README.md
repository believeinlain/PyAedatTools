# PyAedatTools
Tools for manipulating .aedat files (timestamped address-event data from neuromorphic hardware), in Python.

The code for importing aedat files into numpy arrays was borrowed from [simbamford's branch](https://github.com/simbamford/AedatTools), so the readme there will have more details about that particular functionality.

The focus of this repo has been to implement asynchronous tracking and segmentation using various algorithms, with the end goal of tracking objects against noisy dynamic backgrounds such as the sea or trees in wind.

## EventPlayback

The central module for displaying and processing data is the [EventPlayback](https://github.com/believeinlain/PyAedatTools/blob/master/PyAedatTools/EventPlayback.py) module which takes **eventData** in the form of a dict composed of numpy arrays (as returned by the [ImportAedat](https://github.com/believeinlain/PyAedatTools/blob/master/PyAedatTools/ImportAedat.py) function, along with a number of dicts containing parameters for the tracking and data segmentation algorithms that have been implemented so far.

The events in **eventData** are processed asynchronously, and the results are cached into frames every **frameStep** milliseconds, in order to avoid updating the display too frequently. The results are displayed using pygame.

# Algorithms

## Arc*

The corner detection was accomplished using the Arc* algorithm described in reference [1]. This functionality is contained in the [ArcStar](https://github.com/believeinlain/PyAedatTools/blob/master/PyAedatTools/ArcStar.py) module. To summarize, the Arc* algorithm processes each event into a "Surface of Active Events" or SAE. This surface is a 2D array that maps onto the input pixels. Each pixel contains a timestamp corresponding to its "height" on the SAE (**tr**) and the timestamp of the most recent event at this location (**tl**). **tr** will only be updated if a new event occurs more than **k** milliseconds after the last time it was updated, which serves to reduce noise. An event is then considered a corner if the contour of the SAE around it falls in an arc of length between **arcMin** and **arcMax** with radius **radius**. These parameters can be set in the **cornerTrackingArgs** argument to the EventPlayback.playEventData() function. **SAEThreshold** sets the value of **k**, and each event will be run through the Arc* algorithm once for each pass in **passArray**, and will only be considered a corner if it is considered a corner in all passes.

![Surface of Active Events](/images/SAE.png)  
Illustration of the Surface of Active Events (SAE) from reference [1]. The blue line represents the most recent event at each location, while the red line represents the surface with noise filtering.

![ArcStar](/images/ArcStar.png)  
Illustration of the Arc* algorithm operating on an event from reference [1]. This image illustrates how the algorithm can detect both inside and outside corners.

![ArcStar Implementation](/images/ArcStar_implementation.png)  
Screenshot from running [testDisplayPedestrian.py](https://github.com/believeinlain/PyAedatTools/blob/master/testDisplayPedestrian.py), which performs corner detection on pedestrian data from reference [2] using recommended Arc* parameters from reference [1] on an SAE constructed from 'on' events (shown in white). The detected corners are shown in red, and the 'off' events are shown in black.

This approach was found to be quite effective at finding corners on a variety of datasets, however we still need to find a means of discriminating between corners from noise, corners from objects, and corners from dynamic scenery. Also, this approach is somewhat expensive in its current implementation, and although it could stand to be optimized somewhat, it may also be replaced by a less accurate but faster algorithm.

## Feature Tracking

Feature tracking is performed as described in reference [3] using corners identified by the Arc* algorithm. This functionality is contained in the [FeatureTracking](https://github.com/believeinlain/PyAedatTools/blob/master/PyAedatTools/FeatureTracking.py) module.

![Feature Tracking](/images/FeatureTracking.png)  
Screenshot from running [testFeatureTracking.py](https://github.com/believeinlain/PyAedatTools/blob/master/testFeatureTracking.py),

# References

[1] Ignacio Alzugaray and Margarita Chli. <em>Asynchronous Corner Detection and Tracking for Event Cameras in Real-Time</em>

[2] Shu Miao, Guang Chen, Xiangyu Ning, Yang Zi, Kejia Ren, Zhenshan Bing and Alois Knoll. <em>Neuromorphic Vision Datasets for Pedestrian Detection, Action Recognition, and Fall Detection</em>

[3] J.P. Rodr´ıguez-G´omez, A. G´omez Egu´ıluz, J.R. Mart´ınez-de Dios and A. Ollero. <em>Asynchronous event-based clustering and tracking for intrusion monitoring in UAS</em>
