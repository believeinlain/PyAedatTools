
import sys

import pygame

from PyAedatTools import ArcStar
from PyAedatTools import ClusterTracking
from PyAedatTools import FeatureTracking

# playback event data using pygame
def playEventData(eventData, caption="Event Data Playback"):

    # read event data
    timeStamps = eventData['timeStamp'] # should be in ms
    xArray = eventData['x']
    yArray = eventData['y']
    polarityArray = eventData['polarity']

    # pick an arbitrary x and y length
    xLength = 350
    yLength = 265

    # speed to playback events
    speed = 100

    # how fast events fade
    blendRate = 100

    # milliseconds to update frame
    desired_dt = 10

    # initialize the surface of active events
    SAE = ArcStar.getInitialSAE(xLength, yLength)

    # initialize pygame
    pygame.init()

    pygame.display.set_caption(caption)

    # update every set time
    UPDATE = pygame.USEREVENT+1
    pygame.time.set_timer(UPDATE, desired_dt)

    # size assuming uint8 address
    screen = pygame.display.set_mode((xLength, yLength))
    events = pygame.Surface((xLength, yLength))
    events.fill((127,127,127,255))
    fade = pygame.Surface((xLength, yLength), pygame.SRCALPHA)
    fade.fill((127,127,127,blendRate))
    clusterDots = pygame.Surface((xLength, yLength), pygame.SRCALPHA)
    clusterDots.fill((0,0,0,0))

    # keep track of events displayed
    i = 0

    # keep track of elapsed simulation time
    t = 0

    # keep track of frames drawn
    frames = 0

    # cluster tracking parameters
    clusterTracker = ClusterTracking.ClusterTracker(
        maxBufferSize=100,
        newEventWeight=0.9,
        clusteringThreshold=5,
        numClusteringSamples=50
    )

    # track features
    featureTracker = FeatureTracking.FeatureTracker(
        maxBufferSize=1000,
        trackRange=10,
        noiseThreshold=3,
        dimWidth=xLength,
        dimHeight=yLength
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == UPDATE:
                # fill screen with grey
                events.blit(fade, (0,0))

                # assume we update at the desired rate so we don't
                # get bogged down with events
                t = t + desired_dt

                # get reference to screen pixels as 3d array [x][y][color]
                pixels = pygame.surfarray.pixels3d(events)
                
                # add events until timeStamp > time since init
                while i < eventData['numEvents'] and (timeStamps[0]+speed*t) > timeStamps[i]:
                    

                    # draw event to screen
                    color = (0,0,0)
                    if polarityArray[i] == 1:
                        # update the SAE for the current event
                        ArcStar.updateSAE(SAE, eventData, i, xLength, yLength)

                        # use Arc* to determine if the event is a corner
                        # checking circle masks of radius 3 and 4
                        if ArcStar.isEventCorner(SAE, xArray[i], yArray[i], 3) \
                            and ArcStar.isEventCorner(SAE, xArray[i], yArray[i], 4):

                            # track corner event as feature
                            featureTracker.processFeature(int(xArray[i]), int(yArray[i]), int(timeStamps[i]))

                            # process event through cluster tracking
                            clusterTracker.processEvent(int(xArray[i]), int(yArray[i]), int(timeStamps[i]))

                            color = (255,0,0)
                        else:
                            color = (255,255,255)
                        
                    
                    for j in range(3):
                        pixels[ xLength-xArray[i]-1 ][ yLength-yArray[i]-1 ][j] = color[j]

                    # increment events added
                    i = i + 1

                del pixels

                screen.fill((0,0,0,255))
                screen.blit(events, (0,0))

                clusterDots.fill((0,0,0,0))

                # draw clusters being tracked
                for (x, y) in clusterTracker.getClusterCentroids():
                    pygame.draw.circle(clusterDots, (255, 255, 0), (xLength-x-1, yLength-y-1), 1)

                for f in featureTracker.featureList:
                    pygame.draw.circle(clusterDots, (255, 0, 0), (xLength-f.x-1, yLength-f.y-1), 3)

                screen.blit(clusterDots, (0,0))
                
                # update the display
                pygame.display.update()

                # update time elapsed
                sys.stdout.write("\rTime %i" % t)
                sys.stdout.flush()

                # update events processed
                sys.stdout.write("\Event %i" % i)
                sys.stdout.flush()

                # increment frames drawn
                frames = frames + 1

    pygame.quit()
