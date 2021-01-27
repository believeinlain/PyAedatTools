
import sys

from math import pi
from math import exp

# for saving screenshots
from datetime import datetime
import os

# ignore spurious pygame-related errors
# pylint: disable=no-member
# pylint: disable=too-many-function-args
import pygame

from PyAedatTools import CorrelativeFilter
# from PyAedatTools import TightClusterTracking
from PyAedatTools import RegionFinder

import ColorWheel

# display event data next to optical flow data
def beginPlayback(eventData, eventPlaybackArgs, correlativeFilterArgs):

    correlativeFilterArgs['width'] = eventPlaybackArgs['width']
    correlativeFilterArgs['height'] = eventPlaybackArgs['height']
    
    # initialize pygame
    pygame.init()
    pygame.display.set_caption(eventPlaybackArgs['caption'])

    # remember date and time of this run
    #startDateTime = datetime.now()

    # update every frameStep
    UPDATE = pygame.USEREVENT+1
    frameStep = eventPlaybackArgs['frameStep']
    pygame.time.set_timer(UPDATE, int(frameStep/eventPlaybackArgs['playbackSpeed']))

    # draw the optical flow plane metrics to the right of the events
    width = eventPlaybackArgs['width']
    height = eventPlaybackArgs['height']
    # screen is a surface representing the whole display
    screen = pygame.display.set_mode((width, height))
    # draw events onto their own surface
    events = pygame.Surface((width, height))
    events.fill((127, 127, 127, 255))
    # surface to fade the events over time
    fade = pygame.Surface((width, height), pygame.SRCALPHA)
    fade.fill((127, 127, 127, eventPlaybackArgs['fadeAlpha']*255))

    # keep track of total events processed
    i = 0

    # keep track of elapsed simulation time (in microseconds)
    t = 0

    # keep track of total frames drawn
    numFramesDrawn = 0

    # initialize CorrelativeFilter
    correlativeFilter = CorrelativeFilter.CorrelativeFilter(**correlativeFilterArgs)

    # initialize cluster tracker
    # clusterTracker = TightClusterTracking.TightClusterTracker(
    #     clusterRange=10, 
    #     shiftSensitivity=.1, 
    #     tightSensitivity=.1)

    regionFinder = RegionFinder.RegionFinder(width, height)

    # featureTracker = FeatureTracking.FeatureTracker(
    #     maxBufferSize=1000,
    #     trackRange=5,
    #     noiseThreshold=0,
    #     dimWidth=width,
    #     dimHeight=height
    # )

    # enter pygame loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # this code runs every frameStep
            elif event.type == UPDATE:
                # fade out events that have already been drawn
                events.blit(fade, (0,0))

                # each frame a set amount of simulation time passes
                # therefore t may not reflect real time
                # frameStep is in milliseconds but events are recorded in microseconds
                t = t + frameStep*1000

                # get reference to event surface pixels as 3d array [x][y][color]
                pixels = pygame.surfarray.pixels3d(events)
            
                # get the time of the first event so events can be processed starting from time 0
                startTime = eventData['timeStamp'][0]
                
                # add events until timeStamp > time since init
                while i < eventData['numEvents'] \
                    and (eventData['timeStamp'][0] + t) > eventData['timeStamp'][i]:

                    # filterEvents
                    allowEvent = correlativeFilter.processEvent(
                        eventData['x'][i], 
                        eventData['y'][i], 
                        eventData['timeStamp'][i]-startTime,
                        eventData['polarity'][i])

                    # update pixel array to draw event (if not filtered)
                    if allowEvent:
                        # only track allowed events
                        # clusterTracker.processEvent(
                        #     int(eventData['x'][i]), 
                        #     int(eventData['y'][i]), 
                        #     eventData['timeStamp'][i]-startTime,
                        #     eventData['polarity'][i])

                        assignedRegion = regionFinder.processEvent(
                            eventData['x'][i], 
                            eventData['y'][i], 
                            eventData['timeStamp'][i]-startTime)

                        # featureTracker.processFeature(
                        #     int(eventData['x'][i]), 
                        #     int(eventData['y'][i]), 
                        #     int(eventData['timeStamp'][i]-startTime))

                        # choose event color
                        # color = pygame.Color(255,255,255) if eventData['polarity'][i] else pygame.Color(0,0,0)
                        color = pygame.Color(0, 0, 0)
                        color.hsva = (
                            ColorWheel.getHueByIndex(assignedRegion), 
                            100, 
                            75+25*eventData['polarity'][i], 
                            100)

                        for j in range(3):
                            pixels[ width-eventData['x'][i]-1 ][ height-eventData['y'][i]-1 ][j] = color[j]

                    # increment total events
                    i += 1

                regionFinder.updateRegions(eventData['timeStamp'][i]-startTime)

                # free event surface pixel array
                del pixels

                # draw the event surface onto the screen
                screen.fill((0,0,0,255))
                screen.blit(events, (0,0))

                focus = regionFinder.getOldestRegion()
                center = (width-focus.locations[0][0], height-focus.locations[0][1])
                color = (100, 0, 0)
                pygame.draw.circle(screen, color, center, radius=10, width=1)

                # draw clusters onto the screen
                # for c in clusterTracker.clusters:
                #     center = (width-c.x, height-c.y)
                #     color = (c.tightness, 0, 0)
                #     pygame.draw.circle(screen, color, center, clusterTracker.range, width=1)

                 # draw features being tracked
                # for f in featureTracker.featureList:
                #     pygame.draw.circle(screen, (255, 0, 0), (width-f.x-1, height-f.y-1), 3)
                
                # update the display
                pygame.display.update()

                # save the screen as an image
                #framePath = os.path.join(os.path.dirname(__file__), '../frames')
                #screenshotName = "run-" + startDateTime.strftime("%H-%M-%S") + "-%04d.png" % numFramesDrawn
                #pygame.image.save(screen, os.path.join(framePath, screenshotName))

                # update time elapsed
                sys.stdout.write("\rTime %i" % t)
                sys.stdout.flush()

                # update events processed
                sys.stdout.write(" - Event %i" % i)
                sys.stdout.flush()

                # increment frames drawn
                numFramesDrawn += 1

    pygame.quit()