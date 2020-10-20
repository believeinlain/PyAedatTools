
import pygame
import pygame.gfxdraw as gfx

from PyAedatTools import ClusterFinder

# playback event data using pygame
def playEventData(eventData, caption="Event Data Playback"):

    # read event data
    timeStamps = eventData['timeStamp'] # should be in ms
    xArray = eventData['x']
    yArray = eventData['y']
    polarityArray = eventData['polarity']

    # pick an arbitrary x and y length
    xLength = 345
    yLength = 260

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

                # add events until timeStamp > time since init
                while i < eventData['numEvents'] and (timeStamps[0]+speed*t) > timeStamps[i]:
                    # draw event to screen
                    color = (0,0,0)
                    if polarityArray[i] == 1:
                        color = (255,255,255)
                    gfx.pixel(screen, xLength-xArray[i], yLength-yArray[i], color)

                    # increment events added
                    i = i + 1

                # draw clusters for current frame
                #if (f < len(clusters)):
                #    for c in clusters[f]:
                #        pygame.draw.circle(screen, (255,0,0), (int(xLength-c.x), int(yLength-c.y)), 5)

                # update the display
                pygame.display.update()

                # increment frames drawn
                f = f + 1

    pygame.quit()
