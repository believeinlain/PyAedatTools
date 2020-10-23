
import pygame
import pygame.gfxdraw as gfx

from PyAedatTools import ClusterFinder
from PyAedatTools import SurfaceOfActiveEvents
from PyAedatTools import ArcStar

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
    speed = 200

    # how fast events fade
    blendRate = 20

    # milliseconds to update frame
    desired_dt = 30

    # find clusters from data
    #print('Filtering data for clusters')
    #clusters = ClusterFinder.findClusters(eventData, desired_dt)
    #print('Done filtering data for clusters')

    # initialize the surface of active events
    SAE = SurfaceOfActiveEvents.getInitialSAE(xLength, yLength)
    eventsProcessed = 0

    # initialize pygame
    pygame.init()

    pygame.display.set_caption(caption)

    # update every set time
    UPDATE = pygame.USEREVENT+1
    pygame.time.set_timer(UPDATE, desired_dt)

    # size assuming uint8 address
    screen = pygame.display.set_mode((xLength, yLength))
    fade = pygame.Surface((xLength, yLength), pygame.SRCALPHA)
    fade.fill((127,127,127,blendRate))

    # keep track of events displayed
    i = 0

    # keep track of elapsed simulation time
    t = 0

    # keep track of frames drawn
    f = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == UPDATE:
                # fill screen with grey
                screen.blit(fade, (0,0))

                # assume we update at the desired rate so we don't
                # get bogged down with events
                t = t + desired_dt
                
                eventsProcessed = SurfaceOfActiveEvents.getUpdatedSAE(
                    SAE, 
                    eventsProcessed, 
                    t, 
                    eventData,
                    1, 
                    xLength, 
                    yLength
                )
                
                # add events until timeStamp > time since init
                while i < eventData['numEvents'] and (timeStamps[0]+speed*t) > timeStamps[i]:
                    # draw event to screen
                    #color = (0,0,0)
                    if polarityArray[i] == 1:
                        if ArcStar.isEventCorner(SAE, xArray[i], yArray[i]):
                            pygame.draw.circle(screen, (255, 0, 0), (xLength-xArray[i], yLength-yArray[i]), 5)
                            #print("Found corner at ", xArray[i], yArray[i])
                        else:
                            color = (255,255,255)
                            gfx.pixel(screen, xLength-xArray[i], yLength-yArray[i], color)

                    # increment events added
                    i = i + 1
                
                """
                # quit if we run out of frames
                if f >= len(SAEFrames):
                    running = False
                    break
                """
                """
                # draw SAE to screen
                for x in range(xLength):
                    for y in range(yLength):
                        frameTime = f*desired_dt
                        age = abs(SAE[x][y][0] - frameTime)*0.01
                        brightness = max(255-age, 0)
                        color = (brightness, brightness, brightness)
                        gfx.pixel(screen, xLength-x, yLength-y, color)
                """
                """
                # draw clusters for current frame
                if (f < len(clusters)):
                    for c in clusters[f]:
                        pygame.draw.circle(screen, (255,0,0), (int(xLength-c.x), int(yLength-c.y)), 5)
                """
                # update the display
                pygame.display.update()

                # increment frames drawn
                f = f + 1

    pygame.quit()
