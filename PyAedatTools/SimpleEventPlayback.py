
import sys

from math import pi
from math import exp

import numpy as np
import scipy.io

# for saving screenshots
from datetime import datetime
import os

# ignore spurious pygame-related errors
# pylint: disable=no-member
# pylint: disable=too-many-function-args
import pygame

from PyAedatTools import CorrelativeFilter
from PyAedatTools import SurfaceOfActiveEvents
from PyAedatTools import RegionFinder

import ColorWheel

# frame to capture and save data
captureFrame = 299
# captureFrame = 50

# display event data next to optical flow data
def beginPlayback(eventData, eventPlaybackArgs, SAEArgs, correlativeFilterArgs, regionFinderArgs):

    # initialize pygame
    pygame.init()
    pygame.display.set_caption(eventPlaybackArgs['caption'])

    font = pygame.font.Font('freesansbold.ttf', 12)

    # remember date and time of this run
    startDateTime = datetime.now()

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
    SAE = SurfaceOfActiveEvents.SurfaceOfActiveEvents(width, height, **SAEArgs)
    correlativeFilter = CorrelativeFilter.CorrelativeFilter(width, height, SAE, **correlativeFilterArgs)
    regionFinder = RegionFinder.RegionFinder(width, height, SAE, **regionFinderArgs)

    # enter pygame loop
    # TODO: end when we run out of events
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
                        # update the SAE
                        SAE.processEvent(
                            eventData['x'][i], 
                            eventData['y'][i], 
                            eventData['timeStamp'][i]-startTime)
                        # # only track allowed events
                        assignedRegion = regionFinder.processEvent(
                            eventData['x'][i], 
                            eventData['y'][i], 
                            eventData['timeStamp'][i]-startTime)

                        # choose event color
                        color = pygame.Color(0, 0, 0)
                        color.hsva = (
                            ColorWheel.getHueByIndex(assignedRegion), 
                            100, 
                            75+25*eventData['polarity'][i], 
                            100)

                        # color = pygame.Color(255, 255, 255) if eventData['polarity'][i] else pygame.Color(0, 0, 0)

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

                # sort regions by age
                regionsByBirth = sorted(list(regionFinder.regions.values()), key=lambda r: r.birth)

                # # show the five oldest regions with age in seconds
                for k in range(min(len(regionsByBirth), 5)):
                    focus = regionsByBirth[k]
                    x, y = focus.getCentroid()
                    center = (width-x, height-y)
                    # age = t - focus.birth
                    # text = font.render("%.1f"%(age/1000000), True, (255,255,255))
                    # textRect = text.get_rect()
                    # textRect.center = center
                    color = (255/(k+1), 0, 0)
                    pygame.draw.circle(screen, color, center, radius=15, width=1)
                    # screen.blit(text, textRect)
                
                # update the display
                pygame.display.update()

                if numFramesDrawn == captureFrame:
                    buffer = correlativeFilter.buffer
                    icap, jcap, kcap = np.indices(buffer.shape)
                    np.concatenate([icap.reshape(-1, 1), jcap.reshape(-1, 1), kcap.reshape(-1, 1), buffer.reshape(-1, 1)], axis=1)
                    pbuffer = correlativeFilter.polarity
                    icap, jcap, kcap = np.indices(pbuffer.shape)
                    np.concatenate([icap.reshape(-1, 1), jcap.reshape(-1, 1), kcap.reshape(-1, 1), pbuffer.reshape(-1, 1)], axis=1)
                    SAEBuffer = SAE.tr
                    icap, jcap = np.indices(SAEBuffer.shape)
                    np.concatenate([icap.reshape(-1, 1), jcap.reshape(-1, 1), SAEBuffer.reshape(-1, 1)], axis=1)
                    toHue = lambda index: ColorWheel.getHueByIndex(index)
                    regionHue = toHue(regionFinder.regionIndex)
                    for ihue in range(regionHue.shape[0]):
                        for jhue in range(regionHue.shape[1]):
                            if regionFinder.regionIndex[ihue,jhue]==-1:
                                regionHue[ihue,jhue] = -1
                    icap, jcap = np.indices(regionHue.shape)
                    np.concatenate([icap.reshape(-1, 1), jcap.reshape(-1, 1), regionHue.reshape(-1, 1)], axis=1)

                    scipy.io.savemat('frames/frame%i.mat'%captureFrame, {
                        'eventBuffer': buffer,
                        'polarityBuffer': pbuffer,
                        'SAE': SAEBuffer,
                        'regionHue': regionHue
                        })

                # save the screen as an image
                if eventPlaybackArgs['saveFrames']:
                    framePath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frames'))
                    screenshotName = "run-" + startDateTime.strftime("%H-%M") + "-%04d.png" % numFramesDrawn
                    pygame.image.save(screen, os.path.join(framePath, screenshotName))

                # update time elapsed
                sys.stdout.write("\rTime %i" % t)
                sys.stdout.flush()

                # update events processed
                sys.stdout.write(" - Event %i" % i)
                sys.stdout.flush()

                # update frames drawn
                sys.stdout.write(" - Frame %i" % numFramesDrawn)
                sys.stdout.flush()

                # increment frames drawn
                numFramesDrawn += 1

    pygame.quit()