
from copy import deepcopy
import sys

# get Surface of Active Events using S* : (x,y) in R^2 -> (tr, tl) in R
# where tr is only updated for events after time k since last event on that pixel
def getSAEFrames(eventData, polarity, width, height, frameStep, k=50):
    print("Building SAE Frames for polarity ", polarity)

    # initialize 2d array of zero tuples where each tuple is (tr, tl)
    SAE = [[(0, 0) for i in range(height)] for j in range(width)]

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
