
import pygame
import pygame.gfxdraw as gfx

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
    speed = 100

    # how fast events fade
    blendRate = 20

    # milliseconds to update frame
    desired_dt = 30

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

                # get reference to screen pixels as 3d array [x][y][color]
                pixels = pygame.surfarray.pixels3d(screen)
                
                # add events until timeStamp > time since init
                while i < eventData['numEvents'] and (timeStamps[0]+speed*t) > timeStamps[i]:
                    # update the SAE for the current event
                    ArcStar.updateSAE(SAE, eventData, i, 1, xLength, yLength)

                    # draw event to screen
                    color = (0,0,0)
                    if polarityArray[i] == 1:
                        # use Arc* to determine if the event is a corner
                        # checking circle masks of radius 3 and 4
                        if ArcStar.isEventCorner(SAE, xArray[i], yArray[i], 3) \
                            and ArcStar.isEventCorner(SAE, xArray[i], yArray[i], 3):
                            color = (255,0,0)
                        else:
                            color = (255,255,255)
                    
                    for j in range(3):
                        pixels[ xLength-xArray[i]-1 ][ yLength-yArray[i]-1 ][j] = color[j]

                    # increment events added
                    i = i + 1

                del pixels
                
                # update the display
                pygame.display.update()

                # increment frames drawn
                f = f + 1

    pygame.quit()
