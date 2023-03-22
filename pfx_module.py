import pygame, pygame.gfxdraw, random, math

xRES = 1024
yRES = 768
NOW_MS = 0
timer = pygame.time.Clock()
pygame.init()

class Particle(pygame.sprite.Sprite):
    GRAVITY = -7.8

    def __init__(self, x, y, color, direction, tolerance, psizemax, opacitydelta, gravity):
        super(Particle, self).__init__()
        self.gravity = gravity
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(1, psizemax)
        self.circle = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.gfxdraw.aacircle(self.circle, int(self.size/2), int(self.size/2), int(self.size/2-1), self.color)
        pygame.gfxdraw.filled_circle(self.circle, int(self.size/2), int(self.size/2), int(self.size/2-1), self.color)
        self.poly = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.gfxdraw.aapolygon(self.poly, [(0, self.size), (self.size/2, 0), (self.size, self.size)], self.color)
        pygame.gfxdraw.filled_polygon(self.poly, [(0, self.size), (self.size/2, 0), (self.size, self.size)], self.color)
        #self.surface = random.choice([self.poly, self.circle])
        self.surface = self.poly
        if self.color == (255, 255, 255):
            self.surface = self.circle
        if self.surface == self.circle:
            self.rotdelta = 0
            self.rotdeltach = 0
        else:
            self.rotdelta = random.randint(-360, 360)
            self.rotdeltach = random.randint(1, 10)
        self.image = self.surface
        self.opacity = 255
        self.opacitydelta = random.randint(5, 20) / 10 * opacitydelta
        #self.opacitydelta = opacitydelta
        self.opacitych = random.randint(2, 5)
        self.rect = self.image.get_rect()
        #self.ang = math.radians(random.randint(1, 360))
        self.ang = math.radians(random.randint(direction-tolerance, direction+tolerance))
        self.power = random.randint(1,100)
        self.start_time = pygame.time.get_ticks()

    def update(self, screen):
        time_now = pygame.time.get_ticks()
        if (self.power > 0):
            time_change = (time_now - self.start_time)
            if (time_change > 0):
                time_change /= 200.0
                self.image = pygame.transform.rotate(self.surface, self.rotdelta)
                self.image.set_alpha(self.opacity)
                if self.rotdelta < 0:
                    self.rotdelta -= self.rotdeltach
                else:
                    self.rotdelta += self.rotdeltach
                if self.color == (255, 255, 255):
                    self.opacity += self.opacitych
                    if self.opacity < 1 or self.opacity > 255:
                        self.opacitych = -self.opacitych
                else:
                   self.opacity -= self.opacitydelta
                gravitydelta = self.GRAVITY * time_change * time_change / 2.0
                deltax = self.power * time_change * math.sin(self.ang)
                if self.gravity:
                    deltay = self.power * time_change * math.cos(self.ang) + gravitydelta
                else:
                    deltay = self.power * time_change * math.cos(self.ang)

                self.rect.center = ( self.x + int(deltax), self.y - int(deltay))
                if self.opacity < 1:
                    particles.remove(self)
                    self.kill()

                if not screen.get_rect().colliderect(self.rect) or (self.gravity and self.rect.y > 0 and not screen.get_rect().colliderect(self.rect)):
                    #particles.remove(self)
                    self.kill()

def add_stream(x, y, amount, color, direction, tolerance, psizemax, opacitydelta, gravity=True, secondcolor=(255,255,255)):
    for i in range(1, amount):
        if not i % 2:
            particles.append(Particle(x, y, secondcolor, direction, tolerance, psizemax, opacitydelta, gravity))
        else:
            particles.append(Particle(x, y, color, direction, tolerance, psizemax, opacitydelta, gravity))
    spriteGroup.add(particles)

particles = []
spriteGroup = pygame.sprite.Group()
startTime = pygame.time.get_ticks()