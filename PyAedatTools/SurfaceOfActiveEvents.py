
from copy import deepcopy
import sys

# initialize 2d array of zero tuples where each tuple is (tr, tl)
def getInitialSAE(width, height):
    return [[(0, 0) for i in range(height)] for j in range(width)]

# Used to pre-process the SAE frames
# get Surface of Active Events using S* : (x,y) in R^2 -> (tr, tl) in R
# where tr is only updated for events after time k since last event on that pixel
# TODO: update this function to use getUpdatedSAE instead of duplicating code
def getSAEFrames(eventData, polarity, width, height, frameStep, k=50):
    print("Building SAE Frames for polarity ", polarity)

    SAE = getInitialSAE(width, height)

    startTime = eventData['timeStamp'][0]

    SAEFrames = []
    frameTime = 0
    framesProcessed = 0

    totalFrames = int( ( eventData['timeStamp'][eventData['numEvents']-1] - startTime ) / frameStep )

    # filter events
    for i in range(eventData['numEvents']):
        timeStamp = eventData['timeStamp'][i]
        x = eventData['x'][i]
        y = eventData['y'][i]
        ePolarity = eventData['polarity'][i]

        # get event time relative to time 0
        t = timeStamp-startTime

        # only filter events that match desired polarity
        if ePolarity == polarity:
            # update tr only if t > tl + k
            if t > SAE[x][y][1]+k:
                SAE[x][y] = (t, SAE[x][y][1])
            # always update tl
            SAE[x][y] = (SAE[x][y][0], t)
        
        # save a copy of SAE every frameStep ms so we can observe how SAE changes
        # over time
        while frameTime < t:
            # print frame status
            sys.stdout.write("\rProcessing frame %i " % framesProcessed)
            sys.stdout.write("of %i" % totalFrames)
            sys.stdout.flush()
            # add the frame
            SAEFrames.append(deepcopy(SAE))
            frameTime = frameTime + frameStep
            framesProcessed = framesProcessed + 1
    
    print("\nDone building SAE Frames for polarity ", polarity)
    
    return SAEFrames

# Used to process SAE dynamically
# updates the SAE with all not yet processed up to updateToTime
# returns the number of eventsProcessed
def getUpdatedSAE(SAE, eventsProcessed, updateToTime, eventData, polarity, width, height, k=50):

    newEventsProcessed = eventsProcessed
    # filter events from events processed to last event
    # we will break after reaching updateToTime
    for i in range(eventsProcessed, eventData['numEvents']):
        timeStamp = eventData['timeStamp'][i]
        x = eventData['x'][i]
        y = eventData['y'][i]
        ePolarity = eventData['polarity'][i]

        startTime = eventData['timeStamp'][0]

        # get event time relative to time 0
        t = timeStamp-startTime

        # we're done if we've exceeded updateToTime
        if t >= updateToTime:
            break

        # only filter events that match desired polarity
        if ePolarity == polarity:
            # update tr only if t > tl + k
            if t > SAE[x][y][1]+k:
                SAE[x][y] = (t, SAE[x][y][1])
            # always update tl
            SAE[x][y] = (SAE[x][y][0], t)
        
        newEventsProcessed = newEventsProcessed + 1
    
    return newEventsProcessed