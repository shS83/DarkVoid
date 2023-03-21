import pygame, random, os

pygame.init()

VERSION = 0.8
FULLSCREEN = False
HOME_DIR = os.getcwd()
xRES = 1024
yRES = 768

def switch_fullscreen():
    global xRES, yRES, FULLSCREEN
    if not FULLSCREEN:
        old_x = xRES
        old_y = yRES
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        xRES = screen.get_width()
        yRES = screen.get_height()
        FULLSCREEN = True
    else:
        old_x = xRES
        old_y = yRES
        xRES = 1024
        yRES = 768
        screen = pygame.display.set_mode((xRES, yRES), pygame.SHOWN)
        FULLSCREEN = False

def begin_intro(screen, x_resolution, y_resolution):
    global xRES, yRES
    xRES = x_resolution
    yRES = y_resolution

    timer = pygame.time.Clock()
    font = pygame.font.Font(f'{HOME_DIR}/assets/prceltic.ttf', 72)
    font2 = pygame.font.Font(f'{HOME_DIR}/assets/msgothic.ttc', 18)
    running = True
    cooldown = 10
    switch = False
    i = 0
    last = 0
    logointerval = 1000
    #pygame.display.set_caption('DARK VOID')
    xd, yd = font.size('DARK VOID')
    xd2, yd2 = font2.size('press space to continue')
    xd3, yd3 = font2.size('F1 for controls')
    f = 0
    finished = True
    in_logo = False
    in_controls = False
    begin = False
    INITEVENT = pygame.USEREVENT + 1
    LOGOEVENT = pygame.USEREVENT + 2
    FADEOUTEVENT = pygame.USEREVENT + 3
    INITGAME = pygame.USEREVENT + 4
    CONTROLEVENT = pygame.USEREVENT + 5

    def center_text(screen, font, ypos, text, color):
        xdelta, ydelta = font.size(text)
        screen.blit(font.render(text, True, color), (xRES/2-xdelta/2, ypos-ydelta/2))

    def version(screen, version, font, color):
        screen.blit(font.render(str(version), True, color), (xRES-(font.size(str(version))[0])-2, yRES-font.size(str(version))[1]-2))

    pygame.event.post(pygame.event.Event(INITEVENT))

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE and not in_controls:
                    running = False
                    return 9

                if event.key == pygame.K_SPACE:
                    pygame.event.clear()
                    in_logo = False
                    pygame.event.post(pygame.event.Event(FADEOUTEVENT))

                if in_logo and event.key == pygame.K_F1:
                    pygame.event.clear()
                    in_logo = False
                    in_controls = True
                    pygame.event.post(pygame.event.Event(CONTROLEVENT))

                if in_controls and event.key == pygame.K_ESCAPE:
                    pygame.event.clear()
                    in_controls = False
                    in_logo = True
                    pygame.event.post(pygame.event.Event(LOGOEVENT))

                if event.key == pygame.K_F10:
                    switch_fullscreen()

                #if in_logo and event.key == pygame.K_RIGHT:
                #    print(f"next font {fonts[f+1]}")
                #    if f < len(fonts):
                #        f += 1
                #        font = pygame.font.SysFont(fonts[f], 72)

            if event.type == INITEVENT and i < 255:
                now = pygame.time.get_ticks()
                if now - last >= cooldown:
                    last = now
                    screen.fill((0, 0, 0))
                    center_text(screen, font, yRES/2, 'DARK VOID', (i, 0, 0))
                    i += 1
                    if i > 254:
                        i = 255
                        pygame.event.clear()
                        in_logo = True
                        last = 0
                        pygame.event.post(pygame.event.Event(LOGOEVENT))
                pygame.event.post(pygame.event.Event(INITEVENT))

            if event.type == LOGOEVENT:
                if in_logo:
                    now = pygame.time.get_ticks()
                    if now - last >= logointerval:
                        last = now
                        switch = not switch
                        screen.fill((0, 0, 0))
                        if switch:
                            center_text(screen, font2, 20, 'F1 for controls', (255, 0, 0))
                            center_text(screen, font, yRES/2, 'DARK VOID', (i, 0, 0))
                            center_text(screen, font2, yRES-20, 'press space to continue', (255, 0, 0))
                            version(screen, VERSION, font2, (255, 0, 0))
                        else:
                            center_text(screen, font, yRES/2, 'DARK VOID', (i, 0, 0))
                            version(screen, VERSION, font2, (255, 0, 0))
                    pygame.event.post(pygame.event.Event(LOGOEVENT))

            if event.type == CONTROLEVENT:
                if in_controls:
                    screen.fill((0, 0, 0))
                    center_text(screen, font2, 100, ':: CONTROLS ::', (255, 0, 0))
                    center_text(screen, font2, 250, 'W or UP - Accelerate', (255, 0, 0))
                    center_text(screen, font2, 280, 'A or LEFT - Turn left', (255, 0, 0))
                    center_text(screen, font2, 310, 'D or RIGHT - Turn right', (255, 0, 0))
                    center_text(screen, font2, 340, 'SPACE - Fire strong cannon', (255, 0, 0))
                    center_text(screen, font2, 370, 'LEFT MOUSE BUTTON - Fire weak cannon', (255, 0, 0))
                    center_text(screen, font2, 400, '(in direction of mouse pointer)', (255, 0, 0))
                    center_text(screen, font2, 450, 'F10 for fullscreen', (255, 0, 0))
                    center_text(screen, font2, 700, 'ESC to return to logo', (255, 0, 0))
                pygame.event.post(pygame.event.Event(CONTROLEVENT))

            if event.type == FADEOUTEVENT:
                in_logo = False
                if i > 1:
                    now = pygame.time.get_ticks()
                    if now - last >= cooldown:
                        screen.fill((0, 0, 0))
                        center_text(screen, font, yRES/2, 'DARK VOID', (i, 0, 0))
                        i -= 2
                        if i < 2:
                            pygame.event.clear()
                            pygame.event.post(pygame.event.Event(INITGAME))
                    pygame.event.post(pygame.event.Event(FADEOUTEVENT))

            if event.type == INITGAME:
                finished = True
                running = False

        pygame.display.flip()
        timer.tick(120)

    return FULLSCREEN

#xRES = 1024
#yRES = 768
#screen = pygame.display.set_mode([xRES, yRES], pygame.SHOWN)
#begin_intro(screen, xRES, yRES)