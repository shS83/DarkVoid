import pygame, pygame.gfxdraw, os

xRES = 1024
yRES = 768
HOME_DIR = os.getcwd()
ASSET_DIR = f'{HOME_DIR}/assets'
NOW_MS = 0
timer = pygame.time.Clock()
pygame.init()
startTime = pygame.time.get_ticks()
running = True
#font = pygame.font.SysFont('msgothic', 18)
font = pygame.font.Font(f'{ASSET_DIR}/msgothic.ttc', 18)
screen = pygame.display.set_mode([xRES, yRES], pygame.SHOWN)
LEVELCHANGE = pygame.USEREVENT + 5
expl = []
current_frame = 1
last = 0

def loadsprite():
    container = []
    frames = 32
    for i in range(1, frames+1):
         img = pygame.image.load(f'{ASSET_DIR}/exp_{i}.png').convert_alpha()
         container.append(img)
    return container

expl = loadsprite()

class Animation(pygame.sprite.Sprite):

    def __init__(self, anim, pos, set_size, interval, opacity=255, repeat=False):
        super().__init__()
        self.pos = pos
        self.anim = anim
        self.opacity = opacity
        self.image = pygame.transform.smoothscale(anim[0], (set_size, set_size))
        self.image.set_alpha(self.opacity)
        self.size = self.image.get_width()
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] - self.size/2
        self.rect.y = pos[1] - self.size/2
        self.interval = interval
        self.repeat = repeat
        self.curr_frame = 1
        self.anim_length = len(self.anim)
        self.last = 0

    def update(self, screen):
        NOW = pygame.time.get_ticks()
        if not self.repeat and self.curr_frame >= self.anim_length:
            self.kill()
        if self.repeat and self.curr_frame >= self.anim_length:
            self.curr_frame = 1
        if NOW > self.last + self.interval:
            self.last = NOW
            self.image = pygame.transform.smoothscale(self.anim[self.curr_frame], (self.size, self.size))
            self.image.set_alpha(self.opacity)
            self.curr_frame += 1

def new_explosion(pos, size, interval, opacity):
    explosion = Animation(expl, pos, size, interval, opacity, False)
    spriteGroup.add(explosion)

spriteGroup = pygame.sprite.Group()
