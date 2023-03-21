import pygame, pygame.gfxdraw, random, math, os
from pygame.math import Vector2
from pygame.transform import rotozoom
import importlib
import pox_module, pfx_module
import intro_module
from util_module import *
import hs_module
import anim_module

xRES = 1024
yRES = 768
HOME_DIR = os.getcwd()
ASSET_DIR = f'{HOME_DIR}/assets'
NOW_MS = 0
timer = pygame.time.Clock()
pygame.init()
running = True
font = pygame.font.Font(f'{ASSET_DIR}/msgothic.ttc', 18)
die_font = pygame.font.Font(f'{ASSET_DIR}/mingliub.ttc', 100)
msg_font = pygame.font.Font(f'{ASSET_DIR}/msgothic.ttc', 36)
base_font = pygame.font.Font(None, 32)
screen = pygame.display.set_mode([xRES, yRES], pygame.SHOWN)
FULLSCREEN = False
startTime = pygame.time.get_ticks()
size = 20
collidetime = 0
input_text = ''
color_active = (75, 75, 75)
color_passive = (40, 40, 40)
color = color_passive
active = False
SCORE = 0
SHIP_IMAGE = pygame.Surface((size, size), pygame.SRCALPHA)
pygame.gfxdraw.filled_polygon(SHIP_IMAGE, [(1, 1), (size-1, size/2-1), (1, size-1)], (255, 255, 0))
SHIP_IMAGE = pygame.transform.rotate(SHIP_IMAGE, 90)
ROCK1 = pygame.image.load(f'{ASSET_DIR}/rock_3_2.png').convert_alpha()
ROCK2 = pygame.image.load(f'{ASSET_DIR}/rock_4_2.png').convert_alpha()
ROCK3 = pygame.image.load(f'{ASSET_DIR}/rock_5_2.png').convert_alpha()
ROCK4 = pygame.image.load(f'{ASSET_DIR}/rock_6_2.png').convert_alpha()
ROCK_IMAGES = [ROCK1, ROCK2, ROCK3, ROCK4]
LASER_IMAGE = pygame.image.load(f'{ASSET_DIR}/laser_2.png').convert_alpha()
LASER_IMAGE = pygame.transform.rotate(LASER_IMAGE, 145)
LASER2_IMAGE = pygame.image.load(f'{ASSET_DIR}/laser_3.png').convert_alpha()
LASER2_IMAGE = pygame.transform.rotate(LASER2_IMAGE, 145)
def bg_load():
    global BG_IMAGE, xRES, yRES
    BG_IMAGE = pygame.image.load(f'{ASSET_DIR}/space_background_2.jpg').convert_alpha()
    BG_IMAGE = pygame.transform.smoothscale(BG_IMAGE, (xRES, yRES))
bg_load()
UP = Vector2(0, -1)
EXHAUST_INTERVAL = 100
ASTEROID_COUNT = 5
MAX_ASTEROIDS = 10
MIN_ASTEROID_DISTANCE = 200
LEVELCHANGE = pygame.USEREVENT + 5
LEVEL = pygame.USEREVENT + 7
GAME = pygame.USEREVENT + 6
HIGHSCORES = pygame.USEREVENT + 4
DIED = pygame.USEREVENT + 3
NEWHIGHSCORE = pygame.USEREVENT + 2
HS_DELAY = 10000

class Level():
    def __init__(self):
        self.stage = 1
        self.asteroids = 7
        self.asteroid_speed = 1
        self.asteroid_hp = 1

    def up(self):
        self.stage += 1
        self.asteroids += 1
        self.asteroid_speed += 0.20
        self.asteroid_hp += 0.20

def wrap_position(position, surface):
    x, y = position
    w, h = surface.get_size()
    return Vector2(x % (w + size), y % (h + size))

def get_random_position(surface):
    return Vector2(
        random.randrange(surface.get_width()),
        random.randrange(surface.get_height()),
    )

def get_random_velocity(min_speed, max_speed):
    speed = random.randint(min_speed, max_speed)
    angle = random.randrange(0, 360)
    return Vector2(speed, 0).rotate(angle)

class GameObject:
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = Vector2(velocity)

    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

    def move(self, surface):
        self.position = wrap_position(self.position + self.velocity, surface)

    def collides_with(self, other_obj):
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius

    def collides_with_tolerance(self, other_obj, tolerance):
        distance = self.position.distance_to(other_obj.position)
        return distance < self.radius + other_obj.radius + tolerance

    def collides_with_any(self, other_obj_list):
        colliders = False
        for obj in other_obj_list:
            distance = self.position.distance_to(obj.position)
            if distance < self.radius + obj.radius:
                colliders = True
        return colliders

class Spaceship(GameObject):
    MANEUVERABILITY = 15
    ACCELERATION = 0.15
    BULLET_SPEED = 5

    def __init__(self, position, create_bullet_callback):
        self.create_bullet_callback = create_bullet_callback
        self.direction = Vector2(UP)
        self.last = 0
        self.actual_angle = 0
        self.visible = False
        super().__init__(position, SHIP_IMAGE, Vector2(0))

    def rotate(self, clockwise=True):
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.actual_angle += angle
        self.direction.rotate_ip(angle)

    def accelerate(self):
        now = pygame.time.get_ticks()
        if now > self.last + EXHAUST_INTERVAL:
            self.last = now
            x, y = self.position            
            pfx_module.add_stream(x, y, 10, (255, 0, 0), self.actual_angle + 180, 5, 2, 5, False, (255, 0, 0))
        self.velocity += self.direction * self.ACCELERATION

    def draw(self, surface):
        angle = self.direction.angle_to(UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def shoot(self):
        bullet_velocity = self.direction * self.BULLET_SPEED
        bullet = Bullet(self.position, bullet_velocity)
        self.create_bullet_callback(bullet)

class Asteroid(GameObject):
    def __init__(self, position, create_asteroid_callback, size=4):
        self.create_asteroid_callback = create_asteroid_callback
        self.size = size
        self.hp = size * level.asteroid_hp
        self.hit = False
        self.rotation = 0
        size_to_scale = {5: 0.7, 4: 0.6, 3: 0.5, 2: 0.4, 1: 0.3}
        self.scale = size_to_scale[size]
        self.ASTEROID_IMAGE = random.choice(ROCK_IMAGES)
        self.sprite = rotozoom(self.ASTEROID_IMAGE, 0, self.scale).convert_alpha()
        self.rotdelta = random.randint(-100, 100) / 100
        super().__init__(position, self.sprite, get_random_velocity(2, 10) / 8 * level.asteroid_speed)

    def draw(self, surface):
        if self.hit:
            blit_position = self.position - Vector2(self.radius)
            self.sprite.fill((255, 255, 255, 255), None, pygame.BLEND_ADD)
            surface.blit(self.sprite, blit_position)
            self.hit -= 1
        else:
            blit_position = self.position - Vector2(self.radius)
            surface.blit(self.sprite, blit_position)

    def rotate_in_place(self):
        self.rotated_image = pygame.transform.rotate(rotozoom(self.ASTEROID_IMAGE, 0, self.scale), self.rotation)
        self.rotation += self.rotdelta
        self.sprite = self.rotated_image
        self.radius = self.sprite.get_width() / 2

class Bullet(GameObject):
    def __init__(self, position, velocity):
        #ang_delta = position.angle_to(ship.direction)
        self.angle = -ship.actual_angle
        self.damage = 1
        super().__init__(position, pygame.transform.rotate(LASER_IMAGE, self.angle + 125), velocity)

    def move(self, surface):
        self.position = self.position + self.velocity

class Bullet2(GameObject):
    def __init__(self, position, ang):
        self.angle = ang
        self.damage = 0.5
        super().__init__(position, pygame.transform.rotate(LASER2_IMAGE, math.degrees(self.angle) + 125), self.angle)

    def move(self, surface):
        x, y = self.position
        x += math.sin(self.angle) * 5
        y += math.cos(self.angle) * 5
        self.position = (x, y)

def spawn_enemy(amount, new=False):
    if amount > MAX_ASTEROIDS:
        amount = MAX_ASTEROIDS
    while len(asteroids) < amount or new:
        for _ in range(amount):
            while True:
                position = get_random_position(screen)

                if new:
                    position = Vector2(-100, -100)
                    new = False

                if (
                    position.distance_to(ship.position)
                    > MIN_ASTEROID_DISTANCE
                ):
                    break
            asteroids.append(Asteroid(position, asteroids.append, random.randint(1,5)))

        if len(asteroids) > 0:
            for a in asteroids:
                for c in range(0, len(asteroids)):
                    if a == asteroids[c]:
                        continue
                    if a.position.distance_to(asteroids[c].position) < MIN_ASTEROID_DISTANCE:
                        del asteroids[c]
                        break

def add_one_charge(x, y, amount, last):
    now = pygame.time.get_ticks()
    if now > last + blastinterval:
        pox_module.add_charge(x, y, amount, (255, 255, 255), False)
        last = now
    return last

def _get_game_objects():
    game_objects = [*asteroids, *bullets]
    if ship and ship.visible:
        game_objects.append(ship)
    return game_objects

def zoom_text(msg, color, opacity, rot=1.00, sca=1.00, zoomfont=msg_font):
    fs = zoomfont.render(msg, True, color)
    rotated = pygame.transform.rotozoom(fs, rot, sca)
    rotated.set_alpha(opacity)
    xd = rotated.get_width()
    yd = rotated.get_height()
    screen.blit(rotated, (xRES/2-xd/2, yRES/2-yd/2))

def draw_screen_objects():
    #screen.fill((0, 0, 0))
    screen.blit(BG_IMAGE, (0, 0))
    screen.blit(font.render(f'LEVEL: {level.stage}', True, 'white'), (30, 30))
    screen.blit(font.render(f'POINTS: {SCORE}', True, 'white'), (30, 50))
    screen.blit(font.render(f'{message}', True, 'red'), (30, 70))

    # explosions, particles and sprites blit

    pox_module.spriteGroup.update(screen)
    pox_module.spriteGroup.draw(screen)
    pfx_module.spriteGroup.update(screen)
    pfx_module.spriteGroup.draw(screen)
    anim_module.spriteGroup.update(screen)
    anim_module.spriteGroup.draw(screen)

    for game_object in _get_game_objects():

        if hasattr(game_object, 'rotate_in_place'):
            game_object.rotate_in_place()
        game_object.move(screen)
        game_object.draw(screen)

def draw_input(screen):
    if active:
        color = color_active
    else:
        color = color_passive
    input_rect = pygame.Rect(xRES/2-90, yRES-200, 180, 32)
    pygame.draw.rect(screen, color, input_rect)
    text_surface = base_font.render(input_text, True, (255, 255, 255))
    screen.blit(text_surface, (input_rect.x+5, input_rect.y+5))

def new_game():
    global SCORE, level, message, last, ship, lvl_timer, text_flash_timer, once, checked, scores, in_typing, in_hs, laserinterval, laserkey, keyinterval, keypress, blastinterval, bullets, asteroids, space_pressed
    SCORE = 0
    once = True
    checked = False
    scores = False
    in_typing = False
    in_hs = False
    space_pressed = False
    message = ''
    last = 0
    laserinterval = 15
    laserkey = 0
    keyinterval = 50
    keypress = 0
    blastinterval = 1000
    level = Level()
    lvl_timer = pygame.time.get_ticks()
    text_flash_timer = 0
    bullets = []
    asteroids = []
    ship = Spaceship((xRES/2, yRES/2), bullets.append)
    pygame.event.clear()
    pygame.event.post(pygame.event.Event(LEVELCHANGE))

def switch_fullscreen():
    global xRES, yRES, FULLSCREEN
    if not FULLSCREEN:
        old_x = xRES
        old_y = yRES
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        xRES = screen.get_width()
        yRES = screen.get_height()
        ## reposition all game objects
        res_x_delta = xRES - old_x
        res_y_delta = yRES - old_y
        if ship:
            ship.position.x += res_x_delta/2
            ship.position.y += res_y_delta/2
        for a in asteroids:
            a.position.x += res_x_delta/2
            a.position.y += res_y_delta/2
        bg_load()
        FULLSCREEN = True
    else:
        old_x = xRES
        old_y = yRES
        xRES = 1024
        yRES = 768
        screen = pygame.display.set_mode((xRES, yRES), pygame.SHOWN)
        res_x_delta = xRES - old_x
        res_y_delta = yRES - old_y
        if ship:
            ship.position.x += res_x_delta/2
            ship.position.y += res_y_delta/2
        for a in asteroids:
            a.position.x += res_x_delta/2
            a.position.y += res_y_delta/2
        bg_load()
        FULLSCREEN = False

def msg_reset():
    global msg_opacity, msg_rot, msg_sca
    msg_opacity = 255
    msg_rot = 1
    msg_sca = 1

def msg_fx(opa, rot, sca):
    global msg_opacity, msg_rot, msg_sca
    msg_opacity += opa
    msg_rot += rot
    msg_sca += sca

fullscreen_is_true = intro_module.begin_intro(screen, xRES, yRES)
msg_reset()
new_game()
if fullscreen_is_true == 9:
    running = False
if fullscreen_is_true != FULLSCREEN and fullscreen_is_true != 9:
    switch_fullscreen()

while running:
    NOW_MS = pygame.time.get_ticks()
    draw_screen_objects()

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_F10:
            switch_fullscreen()

        if event.type == pygame.KEYDOWN and in_typing:

            if event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]
            elif event.key == pygame.K_RETURN:
                if input_text != '':
                    scores = hs_module.fix_scores(new, input_text, SCORE)
                    result = hs_module.save_scores(scores)
                in_typing = False
                high_timer = pygame.time.get_ticks()
                pygame.event.clear()
                pygame.event.post(pygame.event.Event(HIGHSCORES))
            else:
                active = True
                if len(input_text) < 10:
                    input_text += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and ship and ship.visible:
            mx, my = pygame.mouse.get_pos()
            x, y = ship.position
            dx = mx - x
            dy = my - y
            angle = math.atan2(dx, dy)
            bullet = Bullet2(ship.position, angle)
            ship.create_bullet_callback(bullet)

        if event.type == pygame.KEYDOWN and in_hs and not in_typing:

            if event.key == pygame.K_SPACE:
                in_hs = False
                new_game()

        if event.type == LEVELCHANGE:
            TEXT = f'LEVEL {level.stage}'
            if msg_opacity > 1:
                zoom_text(TEXT, (255, 0, 0), msg_opacity, msg_rot, msg_sca)
                msg_fx(-1.5, 0.15, 0.01)
                pygame.event.post(pygame.event.Event(LEVELCHANGE))
            else:
                msg_reset()
                pygame.event.clear()
                pygame.event.post(pygame.event.Event(LEVEL + level.stage))

        if event.type == LEVEL + level.stage:
            TEXT = 'START'
            if msg_opacity > 1:
                zoom_text(TEXT, (0, 255, 0), msg_opacity, msg_rot, msg_sca)
                msg_fx(-4, 0, 0.05)
                pygame.event.post(pygame.event.Event(LEVEL + level.stage))
            else:
                spawn_enemy(ASTEROID_COUNT + level.stage)
                pygame.event.post(pygame.event.Event(GAME))

        if event.type == NEWHIGHSCORE:
            in_typing = True
            screen.fill((100, 100, 100), special_flags=pygame.BLEND_RGBA_SUB)
            center_text(screen, font, yRES-230, 'Enter your name, pilot!', 'white', xRES)
            draw_input(screen)
            pygame.event.post(pygame.event.Event(NEWHIGHSCORE))

        if event.type == HIGHSCORES:
            if in_hs:
                if once:
                    if not in_typing:
                        high_timer = pygame.time.get_ticks()
                    once = False
                now = pygame.time.get_ticks()
                if now > high_timer + 1000 and not checked:
                    new = hs_module.check_score(SCORE)
                    if new != 'NO':
                        pygame.event.clear()
                        pygame.event.post(pygame.event.Event(NEWHIGHSCORE))
                    scores = hs_module.load_scores()
                    checked = True
                if scores != False:
                    if not in_typing:
                        if text_flash_timer > 200:
                            text_flash_timer = 0
                        elif text_flash_timer > 100:
                            center_text(screen, font, yRES-100, 'press space for new game...', 'white', xRES)
                        text_flash_timer += 1
                    hs_module.scores(screen, scores, 'notoserifcondensed.ttf', 24, xRES, yRES)
                if now > high_timer + HS_DELAY and not in_typing:
                    in_hs = False
                    pygame.event.clear()
                    fullscreen_is_true = intro_module.begin_intro(screen, xRES, yRES)
                    if fullscreen_is_true != FULLSCREEN:
                        switch_fullscreen()
                    new_game()
                pygame.event.post(pygame.event.Event(HIGHSCORES))

        if event.type == DIED:
            TODO = event.type
            if once:
                die_timer = pygame.time.get_ticks()
                once = False
                msg_reset()
            now = pygame.time.get_ticks()
            if now > die_timer + 1000:
                zoom_text('YOU DIED', (255, 0, 0), msg_opacity, msg_rot, msg_sca, zoomfont=die_font)
                msg_fx(-1, 0, 0.01)
                if msg_opacity > 1:
                    TODO = DIED
                else:
                    high_timer = 0
                    msg_reset()
                    once = True
                    in_hs = True
                    TODO = HIGHSCORES
                    pygame.event.clear()
            pygame.event.post(pygame.event.Event(TODO))

        if event.type == GAME:
            ship.visible = True
            pygame.event.clear()

    if ship and ship.visible:

        keys = pygame.key.get_pressed()

        if NOW_MS > keypress + keyinterval:
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                keypress = pygame.time.get_ticks()
                ship.accelerate()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                keypress = pygame.time.get_ticks()
                ship.rotate(clockwise=False)
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                keypress = pygame.time.get_ticks()
                ship.rotate(clockwise=True)
            if keys[pygame.K_SPACE]:
                keypress = pygame.time.get_ticks()
                space_pressed = True
                if laserkey > laserinterval:
                    ship.shoot()
                    laserkey = 0
                    space_pressed = False

        if space_pressed:
            laserkey += 1

        for asteroid in asteroids:
                if asteroid.collides_with(ship):
                    pox_module.add_charge(ship.position[0], ship.position[1], 2000, (255, 0, 0), False)
                    anim_module.new_explosion(ship.position, 256, 25, 225)
                    ship = None
                    once = True
                    message = 'YOU DIED'
                    break

                rocks = asteroids.copy()
                rocks.remove(asteroid)

                # introduce collision delay
                collision_delay = 150
                now = pygame.time.get_ticks()
                if now > collidetime + collision_delay:
                    for rock in rocks:
                        if rock.collides_with_tolerance(asteroid, -15):
                            temp = asteroid.velocity
                            asteroid.velocity = rock.velocity
                            asteroid.rotdelta = -asteroid.rotdelta
                            asteroid.position = wrap_position(asteroid.position + asteroid.velocity * 2, screen)
                            rock.velocity = temp
                            rock.position = wrap_position(rock.position + rock.velocity * 2, screen)
                            collidetime = pygame.time.get_ticks()
                            break

        for bullet in bullets[:]:
            for asteroid in asteroids[:]:
                if asteroid.collides_with(bullet):
                    asteroid.hp -= bullet.damage
                    if bullet.damage == 1:
                        pfx_module.add_stream(bullet.position[0], bullet.position[1], 50, (100, 255, 100), int(-bullet.angle+180), 100, 4, 10, False, (255, 255, 255))
                    else:
                        pfx_module.add_stream(bullet.position[0], bullet.position[1], 50, (100, 100, 255), int(math.degrees(-bullet.angle)), 100, 4, 10, False, (255, 255, 255))
                    bullets.remove(bullet)
                    asteroid.hit = 4
                    
                    if asteroid.hp < 1:
                        SCORE += 1
                        pox_module.add_charge(asteroid.position[0], asteroid.position[1], 300 * asteroid.size, (255, 255, 0), False)
                        anim_module.new_explosion(asteroid.position, 150 * (asteroid.size * 0.5), 25, 225)
                        asteroids.remove(asteroid)
                    break

        for bullet in bullets[:]:
            if not screen.get_rect().collidepoint(bullet.position):
                bullets.remove(bullet)

        if not ship and message == 'YOU DIED':
            once = True
            pygame.event.clear()
            pygame.event.post(pygame.event.Event(DIED))

        if not asteroids and ship and ship.visible:
            if once:
                lvl_timer = pygame.time.get_ticks()
            once = False
            message = 'ENEMIES FELLED'
            msg_reset()
            now = pygame.time.get_ticks()
            if now > lvl_timer + 2000:
                message = ''
                once = True
                ship.visible = False
                level.up()
                pygame.event.clear()
                pygame.event.post(pygame.event.Event(LEVELCHANGE))

    pygame.display.flip()
    timer.tick(120)