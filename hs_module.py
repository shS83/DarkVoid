import pygame, pygame.gfxdraw, random, math, os

xRES = 1024
yRES = 768
NOW_MS = 0
timer = pygame.time.Clock()
pygame.init()
#screen = pygame.display.set_mode([xRES, yRES], pygame.SHOWN)
startTime = pygame.time.get_ticks()
running = True
font = pygame.font.SysFont('msgothic', 18)
HOME_DIR = os.getcwd()
FADE = pygame.USEREVENT + 5

def load_scores():
    scores = []
    handle = open(f'{HOME_DIR}/darkvoid_highscores.txt', 'r')
    for line in handle:
        scores.append(line.rstrip())
    return scores

def check_score(highscore):
    scores = load_scores()
    for e in range(0, len(scores)-1):
        user, score = scores[e].split(' ')
        if highscore >= int(score):
            return e
    return 'NO'

def fix_scores(index, user, highscore):
    scores = load_scores()
    for e in range(0, len(scores)-1):
        if e == index:
            scores.insert(index, f'{user} {highscore}')
            scores.pop()
    return scores

def save_scores(scores):
    try:
        handle = open(f'{HOME_DIR}/darkvoid_highscores.txt', 'w')
        for score in scores:
            handle.write(score + '\n')
        return True
    except:
        return False

    
def blend_fill(screen, fade_to):
    
    c = fade_to
    screen.fill((c, c, c), None, special_flags=pygame.BLEND_RGBA_SUB)
   
def scores(screen, scores, fontname, fsize, xRES, yRES):

    hs_font = pygame.font.Font(f'{HOME_DIR}/assets/{fontname}', int(round(fsize*1.2)))
    score_font = pygame.font.Font(f'{HOME_DIR}/assets/{fontname}', fsize)
    #hs_font = pygame.font.SysFont(fontname, int(round(fsize*1.2)))
    #score_font = pygame.font.SysFont(fontname, fsize)
    blend_fill(screen, 30)
    hstext = 'HALL OF FAME'
    hsblit = hs_font.render(hstext, True, (255, 255, 255))
    hsize = hs_font.size(hstext)
    screen.blit(hsblit, (xRES/2-hsize[0]/2, yRES/10))
    maxlen = len(scores)
    if maxlen > 10:
        maxlen = 10
    for i in range(0, maxlen):
        user, score = scores[i].split(' ')
        usize = score_font.size(user)
        ssize = score_font.size(score)
        userblit = score_font.render(user, True, (255, 255, 255))
        scoreblit = score_font.render(score, True, (255, 255, 255))     
        screen.blit(userblit, (xRES/2-(175), yRES/10+50+(usize[1]+30*i)))
        screen.blit(scoreblit, (xRES/2+(175-ssize[0]), yRES/10+50+(ssize[1]+30*i)))
                    

    #for s in range(0, len(scores)-1):
    #    to_blit = font.render(scores[s], True, (255, 255, 255))
    #    screen.blit(to_blit, (100, 100+s*50))

#while running:

#    for event in pygame.event.get():    
#        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
#                running = False
#        if event.type == pygame.QUIT:
#            running = False
        
    
    