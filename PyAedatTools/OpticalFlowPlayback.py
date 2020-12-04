
import sys

from math import pi

# ignore spurious pygame-related errors
# pylint: disable=no-member
# pylint: disable=too-many-function-args
import pygame

from PyAedatTools import FlowGenerator

# display event data next to optical flow data
def playOpticalFlow(
    eventData,
    eventPlaybackArgs = {
        'caption': "Optical Flow Analysis",
        'width': 350,
        'height': 265,
        'fadeRate': 10,
        'frameStep': 30
    },
    flowGeneratorArgs = {
        'projRes': 10, 
        'projAng': pi
    }
    ):

    flowGeneratorArgs['screenWidth'] = eventPlaybackArgs['width']
    flowGeneratorArgs['screenHeight'] = eventPlaybackArgs['height']
    
    # initialize pygame
    pygame.init()
    pygame.display.set_caption(eventPlaybackArgs['caption'])

    # update every frameStep
    UPDATE = pygame.USEREVENT+1
    frameStep = eventPlaybackArgs['frameStep']
    pygame.time.set_timer(UPDATE, frameStep)

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

    # keep track of total events processed
    i = 0

    # keep track of elapsed simulation time
    t = 0

    # keep track of total frames drawn
    numFramesDrawn = 0

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
                t = t + frameStep

                # get reference to event surface pixels as 3d array [x][y][color]
                pixels = pygame.surfarray.pixels3d(events)
                
                # add events until timeStamp > time since init
                while i < eventData['numEvents'] \
                    and (eventData['timeStamp'][0] + eventPlaybackArgs['playbackSpeed'] * t) > eventData['timeStamp'][i]:

                    # pick event value from {-1, 1}
                    if eventData['polarity'][i] == True:
                        polarity = 1
                    else:
                        polarity = -1

                    # choose event color
                    if eventData['polarity'][i] == True:
                        color = (255,255,255)
                    else:
                        color = (0,0,0)

                    # update pixel array to draw event
                    for j in range(3):
                        pixels[ width-eventData['x'][i]-1 ][ height-eventData['y'][i]-1 ][j] = color[j]

                    # increment total events
                    i += 1

                # free event surface pixel array
                del pixels

                # draw the event surface onto the screen
                screen.fill((0,0,0,255))
                screen.blit(events, (0,0))

                # draw the optical flow metric display onto the screen
                screen.blit(flowPlaneSurface, (width,0))
                
                # update the display
                pygame.display.update()

                # update time elapsed
                sys.stdout.write("\rTime %i" % t)
                sys.stdout.flush()

                # update events processed
                sys.stdout.write(" - Event %i" % i)
                sys.stdout.flush()

                # increment frames drawn
                numFramesDrawn += 1

    pygame.quit()