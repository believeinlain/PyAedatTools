
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

from PyAedatTools import FlowGenerator

# display event data next to optical flow data
def playOpticalFlow(eventData, eventPlaybackArgs, flowGeneratorArgs):

    flowGeneratorArgs['screenWidth'] = eventPlaybackArgs['width']
    flowGeneratorArgs['screenHeight'] = eventPlaybackArgs['height']
    
    # initialize pygame
    pygame.init()
    pygame.display.set_caption(eventPlaybackArgs['caption'])

    # remember date and time of this run
    startDateTime = datetime.now()

    # update every frameStep
    UPDATE = pygame.USEREVENT+1
    frameStep = eventPlaybackArgs['frameStep']
    pygame.time.set_timer(UPDATE, int(frameStep/eventPlaybackArgs['playbackSpeed']))

    # draw the optical flow plane metrics to the right of the events
    width = eventPlaybackArgs['width']
    height = eventPlaybackArgs['height']
    totalWidth = eventPlaybackArgs['width'] + height
    # screen is a surface representing the whole display
    screen = pygame.display.set_mode((totalWidth, height))
    # draw events onto their own surface
    events = pygame.Surface((width, height))
    events.fill((127, 127, 127, 255))
    # surface to fade the events over time
    fade = pygame.Surface((width, height), pygame.SRCALPHA)
    fade.fill((127, 127, 127, eventPlaybackArgs['fadeRate']))
    # surface to draw optical flow metrics onto
    flowPlaneSurface = pygame.Surface((height, height))
    flowPlaneSurface.fill((255, 255, 255, eventPlaybackArgs['fadeRate']))
    # surface to draw trackplane projection cells onto
#    trackPlaneSurface = pygame.Surface((width, height), pygame.SRCALPHA)
#    trackPlaneSurface.fill((0, 0, 0, 0))

    # keep track of total events processed
    i = 0

    # keep track of elapsed simulation time (in microseconds)
    t = 0

    # keep track of total frames drawn
    numFramesDrawn = 0

    # initialize FlowGenerator
    flowGenerator = FlowGenerator.FlowGenerator(**flowGeneratorArgs)

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

                    # pick event value from {-1, 1}
                    if eventData['polarity'][i] == True:
                        polarity = 1
                    else:
                        polarity = -1

                    # process the event for optical flow analysis
                    eHue = flowGenerator.processNewEvent(
                        eventData['x'][i], 
                        eventData['y'][i], 
                        eventData['timeStamp'][i]-startTime,
                        polarity)

                    # choose event color
                    color = pygame.Color(255,255,255) if eventData['polarity'][i] else pygame.Color(0,0,0)
                    # color event to match trackplane
                    if eHue is not None:
                        color.hsva = (eHue, 100, 75+25*polarity, 100)

                    # update pixel array to draw event
                    for j in range(3):
                        pixels[ width-eventData['x'][i]-1 ][ height-eventData['y'][i]-1 ][j] = color[j]

                    # increment total events
                    i += 1

                # free event surface pixel array
                del pixels

                # update the metrics in the flow plane module and find new track planes if applicable
                flowGenerator.updateFlowPlaneMetrics()

                # draw the optical flow metric array
                metricArray = flowGenerator.flowPlaneModule.getNormalizedMetricArray()

                n = flowGeneratorArgs['projRes']
                gridSize = height/n
                for ni in range(n):
                    for nj in range(n):
                        # draw a rect corresponding to the value of the metric for each angle
                        metric = metricArray[n-ni-1][n-nj-1]
                        brightness = 255-255*metric
                        color = (brightness, brightness, brightness)
                        rect = pygame.Rect(ni*gridSize, nj*gridSize, gridSize, gridSize)
                        pygame.draw.rect(flowPlaneSurface, color, rect)

                # get reference to trackplane surface pixels as 3d array [x][y][color]
#                pixels = pygame.surfarray.pixels3d(trackPlaneSurface)
#                pixels_alpha = pygame.surfarray.pixels_alpha(trackPlaneSurface)

                # draw track planes onto the flow metric array as colored circles
                maxSize = height*0.1
                scaleRate = 1 # bigger means it takes more events to reach maxSize
                for (hue, size, normal, cells) in flowGenerator.getTrackPlaneDisplayData():
                    tpx = height-height*(normal[0]+pi/2)/pi
                    tpy = height-height*(normal[1]+pi/2)/pi
                    color = pygame.Color(0, 0, 0)
                    color.hsva = (hue, 100, 100, 50)
                    radius = maxSize*(1-exp(-size/scaleRate))
                    pygame.draw.circle(flowPlaneSurface, color, (tpx, tpy), radius)
#                    for (x, y) in cells:
#                        # update pixel array to draw event
#                        for j in range(3):
#                            pixels[ width-x-1 ][ height-y-1 ][j] = color[j]
#                        pixels_alpha[ width-x-1 ][ height-y-1 ] = 100
                
                # free trackplane surface pixel array
#                del pixels
#                del pixels_alpha

                # draw the event surface onto the screen
                screen.fill((0,0,0,255))
                screen.blit(events, (0,0))

                # draw the optical flow metric display onto the screen
                screen.blit(flowPlaneSurface, (width,0))

                # draw the track plane surface onto the screen
                # TODO: make the alpha actually work
#                screen.blit(trackPlaneSurface, (0,0))
                
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