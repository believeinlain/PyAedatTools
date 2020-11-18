
import sys

# ignore spurious pygame-related errors
# pylint: disable=no-member
# pylint: disable=too-many-function-args
import pygame

from random import random

from PyAedatTools import AttentionPriorityMap
from PyAedatTools import ArcStar
from PyAedatTools import ClusterTracking
from PyAedatTools import FeatureTracking
from PyAedatTools import EventBuffer

# playback event data using pygame
def playEventData(
    eventData, 
    eventPlaybackArgs, 
    featureTrackingArgs = {
        'enable':True,
        'maxBufferSize':1000,
        'trackRange':5,
        'noiseThreshold':4
    }, 
    clusterTrackingArgs = {
        'enable':False,
        'maxBufferSize':100,
        'newEventWeight':0.9,
        'clusteringThreshold':5,
        'numClusteringSamples':50
    }, 
    cornerTrackingArgs = {
        # for a corner to be counted it has to count for all passes
        'passArray': [
            {'radius':3,'arcMin':3,'arcMax':6},
            {'radius':4,'arcMin':4,'arcMax':8}
        ],
        'SAEThreshold':50
    }
    ):

    width = eventPlaybackArgs['width']
    height = eventPlaybackArgs['height']

    featureTrackingArgs['dimWidth'] = width
    featureTrackingArgs['dimHeight'] = height

    # read event data
    timeStamps = eventData['timeStamp'] # should be in ms
    xArray = eventData['x']
    yArray = eventData['y']
    polarityArray = eventData['polarity']

    # get width and height from input
    xLength = width
    yLength = height

    # speed to playback events
    speed = eventPlaybackArgs['playbackSpeed']

    # how fast events fade
    blendRate = eventPlaybackArgs['blendRate']

    # milliseconds to update frame
    desired_dt = eventPlaybackArgs['frameStep']

    # initialize the surface of active events
    SAE = ArcStar.getInitialSAE(xLength, yLength)

    # initialize the APM
    eventBuffer = EventBuffer.EventBuffer(eventPlaybackArgs['maxBufferSize'])
    attentionThreshold = eventPlaybackArgs['attentionThreshold'] # must be less than this intensity to care about
    APM = AttentionPriorityMap.AttentionPriorityMap(width, height, eventPlaybackArgs['APMRadius'], eventBuffer)

    # initialize pygame
    pygame.init()

    pygame.display.set_caption(eventPlaybackArgs['caption'])

    # update every set time
    UPDATE = pygame.USEREVENT+1
    pygame.time.set_timer(UPDATE, desired_dt)

    # size assuming uint8 address
    screen = pygame.display.set_mode((xLength, yLength))
    events = pygame.Surface((xLength, yLength))
    events.fill((127,127,127,255))
    fade = pygame.Surface((xLength, yLength), pygame.SRCALPHA)
    fade.fill((127,127,127,blendRate))
    overlay = pygame.Surface((xLength, yLength), pygame.SRCALPHA)
    overlay.fill((0,0,0,0))

    # keep track of events displayed
    i = 0

    # keep track of elapsed simulation time
    t = 0

    # keep track of frames drawn
    frames = 0

    # track clusters (unpacking arg dictionary w/o enable argument)
    if clusterTrackingArgs['enable']:
        argsToPass = clusterTrackingArgs.copy()
        argsToPass.pop('enable')
        clusterTracker = ClusterTracking.ClusterTracker(**argsToPass)

    # track features (unpacking arg dictionary w/o enable argument)
    if featureTrackingArgs['enable']:
        argsToPass = featureTrackingArgs.copy()
        argsToPass.pop('enable')
        featureTracker = FeatureTracking.FeatureTracker(**argsToPass)

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
                        ArcStar.updateSAE(SAE, eventData, i, xLength, yLength, cornerTrackingArgs['SAEThreshold'])

                        # create a new event tuple and update event buffer
                        newEvent = EventBuffer.event(xArray[i], yArray[i], timeStamps[i])
                        eventBuffer.update(newEvent)

                        # update the APM (only for on events)
                        # randomly sample a fraction of events
                        if eventPlaybackArgs['APMEnable'] and random() < eventPlaybackArgs['APMSampleFraction']:
                            APM.processEvent(newEvent)

                        # use Arc* to determine if the event is a corner
                        # checking circle masks from the pass array in cornerTrackingArgs
                        eventIsCorner = False
                        # only care about events based on attention threshold
                        if APM.getNormalizedIntensity(xArray[i], yArray[i]) < attentionThreshold or not eventPlaybackArgs['APMEnable']:
                            for p in cornerTrackingArgs['passArray']:
                                if ArcStar.isEventCorner(SAE, xArray[i], yArray[i], p):
                                    eventIsCorner = True
                        
                        if eventIsCorner:
                            # track corner event as feature
                            if featureTrackingArgs['enable']:
                                featureTracker.processFeature(int(xArray[i]), int(yArray[i]), int(timeStamps[i]))

                            # process event through cluster tracking
                            if clusterTrackingArgs['enable']:
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

                overlay.fill((0,0,0,0))

                # draw clusters being tracked
                if clusterTrackingArgs['enable']:
                    for c in clusterTracker.clusters:
                        pygame.draw.circle(overlay, (255, 255, 0), (xLength-c.x-1, yLength-c.y-1), 1)

                # draw features being tracked
                if featureTrackingArgs['enable']:
                    for f in featureTracker.featureList:
                        pygame.draw.circle(overlay, (255, 0, 0), (xLength-f.x-1, yLength-f.y-1), 3)

                screen.blit(overlay, (0,0))
                
                # update the display
                pygame.display.update()

                # update time elapsed
                sys.stdout.write("\rTime %i" % t)
                sys.stdout.flush()

                # update events processed
                sys.stdout.write(" - Event %i" % i)
                sys.stdout.flush()

                # increment frames drawn
                frames = frames + 1

    pygame.quit()
