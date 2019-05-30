import pygame
import sys
import random
from pygame import *
import os

ENLARGE_FACTOR = 3 #USE 3!!!
SCREEN_SIZE = pygame.Rect((0, 0, 480, 480))
TILE_SIZE = 16 * ENLARGE_FACTOR
READY_TO_SWITCH = False
NEXT_NAME = None
NEXT_DEF_POS = None
CONTINUE_MUSIC = "t"
TIME_UNTIL_ENCOUNTER = 0
screen = pygame.display.set_mode(SCREEN_SIZE.size)
entities = None
mapname = None
pTeam = None
playerLost = False
RESPAWN_POINT = ("00", 6, 6)
doneLoading = True
sound_library = {}
timer = pygame.time.Clock()

import Battle, TeamInfo, Bag, PkmnMenu, PC

class CameraAwareLayeredUpdates(pygame.sprite.LayeredUpdates):
    def __init__(self, target, world_size):
        super().__init__()
        self.target = target
        self.cam = pygame.Vector2(0, 0)
        self.world_size = world_size
        if self.target:
            self.add(target)

    def update(self, *args):
        super().update(*args)
        if self.target:
            x = -self.target.rect.center[0] + SCREEN_SIZE.width/2
            y = -self.target.rect.center[1] + SCREEN_SIZE.height/2
            self.cam += (pygame.Vector2((x, y)) - self.cam) * 1
            self.cam.x = max(-(self.world_size.width-SCREEN_SIZE.width), min(0, self.cam.x))
            self.cam.y = max(-(self.world_size.height-SCREEN_SIZE.height), min(0, self.cam.y))
        self.change_layer(self.target, self.get_top_layer())
        
    def draw(self, surface):
        spritedict = self.spritedict
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        init_rect = self._init_rect
        for spr in self.sprites():
            rec = spritedict[spr]
            newrect = surface_blit(spr.image, spr.rect.move(self.cam))
            if rec is init_rect:
                dirty_append(newrect)
            else:
                if newrect.colliderect(rec):
                    dirty_append(newrect.union(rec))
                else:
                    dirty_append(newrect)
                    dirty_append(rec)
            spritedict[spr] = newrect
            
        return dirty            

class YAwareGroup(pygame.sprite.Group):
    def by_y(self, spr):
        return spr.pos[1]
    def draw(self, surface):
        sprites = self.sprites()
        surface_blit = surface.blit
        for spr in sorted(sprites, key=self.by_y):
            entities.change_layer(spr, entities.get_top_layer())
            entities.draw(screen)
        self.lostsprites = []

def main(name, default_position, continue_music, team):
    global mapname
    mapname = name
    
    global screen
    global entities

    global pTeam
    pTeam = team
    pygame.display.set_caption("Pokémon?")

    global READY_TO_SWITCH
    READY_TO_SWITCH = False

    level = open("collision_maps/collisionMap" + mapname + ".txt", "r").readlines()
    xTiles = yTiles = 0
    for line in level:
        words = line.split()
        xTiles = words.__len__()
        yTiles += 1
    collidables = pygame.sprite.Group()
    noncollidables = pygame.sprite.Group()
    npcs = YAwareGroup()
    player = Player(mapname, collidables, (TILE_SIZE * int(default_position[0]), TILE_SIZE * int(default_position[1])))
    npcs.add(player)
    level_width = xTiles*TILE_SIZE
    level_height = yTiles*TILE_SIZE
    entities = CameraAwareLayeredUpdates(player, pygame.Rect(0, 0, level_width, level_height))
    dbox = DialogBox("Sample Text", (TILE_SIZE,TILE_SIZE * 5), entities)

    with open("sprite_maps/spriteMap" + mapname + ".txt", "r") as f:
        data = f.readlines()
    spriteNames = []
    for line in data:
        words = line.split()
        spriteNames.append(words)
        # build the level
    x = y = 0
    i = j = 0
    for line in level:
        types = line.split()
        for col in types:
            if col == "t":
                Collidable(spriteNames[j][i], (x, y), collidables, entities)
            elif col == "l":
                Ledge(spriteNames[j][i], (x, y), collidables, entities)
            elif col == "f":
                Noncollidable(spriteNames[j][i], (x, y), noncollidables, entities)
            elif col == "u":
                Noncollidable_Under(spriteNames[j][i], (x, y), noncollidables, entities)
            elif col == "e":
                ExitBlock(spriteNames[j][i], (x, y), collidables, entities)
            elif col == "b":
                EncounterBlock(spriteNames[j][i], (x, y), collidables, entities)
            elif col.split(":")[0] == "d":
                db = DBlock(spriteNames[j][i], (x, y), collidables, entities)
                db.textnum = col.split(":")[1]

            x += TILE_SIZE
            i += 1
        y += TILE_SIZE
        j += 1
        x = i = 0
    
    with open("npc_maps/npcMap" + mapname + ".txt", "r") as f:
        data = f.readlines()
    for line in data:
        things = line.strip().split(":")
        npc = NPC(things[0], (int(things[1])*TILE_SIZE, int(things[2])*TILE_SIZE - 16), collidables, npcs, entities)
        npc.textnum = things[3]
    
    if continue_music != "t":
        pygame.mixer.music.load("music/" + mapname + ".ogg")
        pygame.mixer.music.play(-1)

    global doneLoading
    fade = pygame.sprite.Sprite()
    fade.rect = pygame.Rect(0,0,TILE_SIZE*10,TILE_SIZE*10)
    fade.image = pygame.Surface((TILE_SIZE*10,TILE_SIZE*10), flags=pygame.SRCALPHA)
    fade.alpha = 255
    fadeg = pygame.sprite.Group(fade)
    doneLoading = False
    for i in range(16):
        fade.alpha = 255-(i*16)
        fade.image.fill((0,0,0,fade.alpha))
        entities.update()
        entities.draw(screen)
        fadeg.draw(screen)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return
        timer.tick(30)
    doneLoading = True

    while 1:
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    return
                if e.key == K_x:
                    dbox.checkInFront(player, level, collidables, noncollidables, npcs)
                if e.key == K_a:
                    openMenu(level, collidables, noncollidables, npcs)
        
        entities.update()
        global CONTINUE_MUSIC
        global NEXT_NAME
        global NEXT_DEF_POS
        if READY_TO_SWITCH:
            entities.empty()
            if CONTINUE_MUSIC != "t":
                pygame.mixer.music.stop()
            return NEXT_NAME, NEXT_DEF_POS, CONTINUE_MUSIC
        entities.draw(screen)
        npcs.draw(screen)
        pygame.display.update()
        timer.tick(60)
        pygame.display.flip()
        global playerLost
        if playerLost:
            playerLost = False
            READY_TO_SWITCH = True
            CONTINUE_MUSIC = "f"
            NEXT_NAME = RESPAWN_POINT[0]
            NEXT_DEF_POS = (RESPAWN_POINT[1], RESPAWN_POINT[2])
        global TIME_UNTIL_ENCOUNTER
        if TIME_UNTIL_ENCOUNTER > 0:
            TIME_UNTIL_ENCOUNTER -= 1

def redrawSprites(level, collidables, noncollidables, npcs):
    global entities
    for collidable in collidables:
        entities.change_layer(collidable, entities.get_top_layer())
        screen.blit(collidable.image, collidable.pos)
    for noncollidable in noncollidables:
        entities.change_layer(noncollidable, entities.get_top_layer())
        screen.blit(noncollidable.image, noncollidable.pos)
    for npc in npcs:
        entities.change_layer(npc, entities.get_top_layer())
        screen.blit(npc.image, npc.pos)
    entities.draw(screen)
    npcs.draw(screen)

def openMenu(level, collidables, noncollidables, npcs):
    menu = pygame.sprite.Sprite()
    menu.image = pygame.image.load("menu3.png")
    menu.image = pygame.transform.scale(menu.image, (TILE_SIZE*4, int(TILE_SIZE*7.5)))
    menu.pos = (TILE_SIZE*5.5, TILE_SIZE*0.5)
    menu.rect = menu.image.get_rect(topleft=menu.pos)
    options = pygame.sprite.Group()
    bag = MenuButton((TILE_SIZE*6,TILE_SIZE*1.5), "BAG", options)
    pokemon = MenuButton((TILE_SIZE*6,TILE_SIZE*2.5), "$%", options)
    save = MenuButton((TILE_SIZE*6,TILE_SIZE*3.5), "SAVE", options)
    dex = MenuButton((TILE_SIZE*6,TILE_SIZE*4.5), "POKEDEX", options)
    gear = MenuButton((TILE_SIZE*6,TILE_SIZE*5.5), "OPTIONS", options)
    player = MenuButton((TILE_SIZE*6,TILE_SIZE*6.5), "PLAYER", options)
    menuselect = pygame.sprite.Sprite()
    menuselect.image = pygame.image.load("menuselect.png")
    menuselect.image = pygame.transform.scale(menuselect.image, (TILE_SIZE*3, TILE_SIZE))
    menuselect.pos = (TILE_SIZE*6, TILE_SIZE*1.5)
    menuselect.rect = menuselect.image.get_rect(topleft=menuselect.pos)
    position = 0
    screen.blit(menu.image, menu.pos)
    while 1:
        for sprite in options:
            screen.blit(sprite.image, sprite.pos)
            screen.blit(sprite.label, sprite.labelrect)
        screen.blit(menuselect.image, menuselect.pos)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT: 
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_a or e.key == K_z:
                    return
                elif e.key == K_DOWN:
                    if position < 5:
                        position += 1
                elif e.key == K_UP:
                    if position > 0:
                        position -= 1
                elif e.key == K_x:
                    if position == 0:
                        print(Bag.requestItem().name)
                        redrawSprites(level, collidables, noncollidables, npcs)
                        screen.blit(menu.image, menu.pos)
                    elif position == 1:
                        PkmnMenu.battleSwitch(pTeam)
                        redrawSprites(level, collidables, noncollidables, npcs)
                        screen.blit(menu.image, menu.pos)
                menuselect.pos = menuselect.pos = (TILE_SIZE*6, TILE_SIZE*1.5 + TILE_SIZE*position)
                menuselect.rect = menuselect.image.get_rect(topleft=menuselect.pos)

def battleTransition(number):
    if number == 1:
        slide1 = pygame.sprite.Sprite()
        slide1.image = pygame.image.load("sweepTransition1.png")
        slide1.image = pygame.transform.scale(slide1.image, (TILE_SIZE*20,TILE_SIZE*10))
        slide1.rect = slide1.image.get_rect(topleft = (int(TILE_SIZE*(-20)),0))
        slide2 = pygame.sprite.Sprite()
        slide2.image = pygame.image.load("sweepTransition2.png")
        slide2.image = pygame.transform.scale(slide2.image, (TILE_SIZE*20,TILE_SIZE*10))
        slide2.rect = slide2.image.get_rect(topleft = (int(TILE_SIZE*10),0))
        for i in range(54):
            slide1.rect.left += ENLARGE_FACTOR*8
            slide2.rect.left -= ENLARGE_FACTOR*8
            screen.blit(slide1.image, slide1.rect)
            screen.blit(slide2.image, slide2.rect)
            pygame.display.flip()
            timer.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
        ball = pygame.sprite.Sprite()
        ball.image = pygame.image.load("ballanimation.png")
        ball.image = pygame.transform.scale(ball.image, (TILE_SIZE*5,TILE_SIZE*5))
        ball.rect = ball.image.get_rect(topleft = (int(TILE_SIZE*2.5),int(TILE_SIZE*2.5)))
        for i in range(45):
            screen.blit(ball.image, ball.rect)
            screen.blit(ball.image, ball.rect)
            pygame.display.flip()
            timer.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

class Entity(pygame.sprite.Sprite):
    def __init__(self, image, pos, *groups):
        super().__init__(*groups)
        self.image = pygame.image.load(image)
        self.rect = self.image.get_rect(topleft=pos)
        self.rect.inflate(TILE_SIZE*4, TILE_SIZE*4) #I'm not sure if this does anything
        self.pos = pos

class Player(Entity):
    def __init__(self, mapname, collidables, pos, *groups):
        super().__init__("character_sprites/char00.png", pos, *groups)
        self.pos = pos
        self.vel = pygame.Vector2((0, 0))
        self.collidables = collidables
        self.mapname = mapname
        self.rect = pygame.Rect((self.pos[0], self.pos[1] - 12),(47,60))
        self.speed = 6
        self.ticks = 0
        n = "character_sprites/char"
        self.walkDown = [n+"01x3.png", n+"00x3.png", n+"02x3.png", n+"00x3.png"]
        self.walkUp = [n+"11x3.png", n+"10x3.png", n+"12x3.png", n+"10x3.png"]
        self.walkLeft = [n+"21x3.png", n+"20x3.png", n+"22x3.png", n+"20x3.png"]
        self.walkRight = [n+"31x3.png", n+"30x3.png", n+"32x3.png", n+"30x3.png"]
        self.runDown = [n+"41x3.png", n+"40x3.png", n+"42x3.png", n+"40x3.png"]
        self.runUp = [n+"51x3.png", n+"50x3.png", n+"52x3.png", n+"50x3.png"]
        self.runLeft = [n+"61x3.png", n+"60x3.png", n+"62x3.png", n+"60x3.png"]
        self.runRight = [n+"71x3.png", n+"70x3.png", n+"72x3.png", n+"70x3.png"]
        self.facing = "down"
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, int(TILE_SIZE*1.25)))
        self.running = False

    def update(self):
        if doneLoading == False:
            return
        pressed = pygame.key.get_pressed()
        up = pressed[K_UP]
        down = pressed[K_DOWN]
        left = pressed[K_LEFT]
        right = pressed[K_RIGHT]
        running = pressed[K_SPACE]
        if not running:
            if up:
                self.vel.y = -self.speed/2
                img = self.walkUp[int(self.ticks/12)]
                self.image = pygame.image.load(img)
                self.facing = "up"
            if down:
                self.vel.y = self.speed/2
                img = self.walkDown[int(self.ticks/12)]
                self.image = pygame.image.load(img)
                self.facing = "down"
            if left:
                self.vel.x = -self.speed/2
                img = self.walkLeft[int(self.ticks/12)]
                self.image = pygame.image.load(img)
                self.facing = "left"
            if right:
                self.vel.x = self.speed/2
                img = self.walkRight[int(self.ticks/12)]
                self.image = pygame.image.load(img)
                self.facing = "right"
        else:
            if up:
                self.vel.y = -self.speed/2
                img = self.runUp[int(self.ticks/12)]
                self.image = pygame.image.load(img)
                self.facing = "up"
            if down:
                self.vel.y = self.speed/2
                img = self.runDown[int(self.ticks/12)]
                self.image = pygame.image.load(img)
                self.facing = "down"
            if left:
                self.vel.x = -self.speed/2
                img = self.runLeft[int(self.ticks/12)]
                self.image = pygame.image.load(img)
                self.facing = "left"
            if right:
                self.vel.x = self.speed/2
                img = self.runRight[int(self.ticks/12)]
                self.image = pygame.image.load(img)
                self.facing = "right"
            self.vel.x *= 1.5
            self.vel.y *= 1.5
            
        if not(left or right):
            self.vel.x = 0
        if not(up or down):
            self.vel.y = 0
        if self.vel.x == 0 and self.vel.y == 0:
            if self.facing == "down":
                self.image = pygame.image.load("character_sprites/char00x3.png")
            if self.facing == "up":
                self.image = pygame.image.load("character_sprites/char10x3.png")
            if self.facing == "left":
                self.image = pygame.image.load("character_sprites/char20x3.png")
            if self.facing == "right":
                self.image = pygame.image.load("character_sprites/char30x3.png")
        # increment in x direction
        self.rect.left += self.vel.x
        # do x-axis collisions
        self.collide(self.vel.x, 0, self.collidables)
        # increment in y direction
        self.rect.top += self.vel.y
        # do y-axis collisions
        self.collide(0, self.vel.y, self.collidables)
        self.ticks += 1 # this value determines the animation speed
        if self.ticks == 48: self.ticks = 0
        self.pos = (self.rect.topleft)

    def collide(self, xvel, yvel, collidables):
        for p in collidables:
            if pygame.Rect.colliderect(self.rect, p.collisionRect):
                if isinstance(p, ExitBlock):
                    if self.rect.top < p.collisionRect.bottom - 12:
                        with open("exit_maps/eMap" + self.mapname + ".txt", "r") as f:
                            data = f.readlines()
                        eNames = []
                        for line in data:
                            words = line.split()
                            eNames.append(words)
                        global READY_TO_SWITCH
                        global NEXT_NAME
                        global NEXT_DEF_POS
                        global CONTINUE_MUSIC
                        global entities
                        NEXT_DEF_POS = (0, 0)
                        READY_TO_SWITCH = True
                        nextData = eNames[int(p.pos[1] / TILE_SIZE)][int(p.pos[0] / TILE_SIZE)].split(":")
                        NEXT_NAME = nextData[0]
                        NEXT_DEF_POS = (nextData[1], int(nextData[2]))
                        CONTINUE_MUSIC = nextData[3]
                        fade = pygame.sprite.Sprite()
                        fade.rect = pygame.Rect(0,0,TILE_SIZE*10,TILE_SIZE*10)
                        fade.image = pygame.Surface((TILE_SIZE*10,TILE_SIZE*10), flags=pygame.SRCALPHA)
                        fade.alpha = 0
                        fadeg = pygame.sprite.Group(fade)
                        for i in range(16):
                            fade.alpha = i*16
                            fade.image.fill((0,0,0,fade.alpha))
                            fadeg.draw(screen)
                            pygame.display.update()
                            for e in pygame.event.get():
                                if e.type == pygame.QUIT:
                                    return
                            timer.tick(30)
                elif isinstance(p, EncounterBlock):
                    global TIME_UNTIL_ENCOUNTER
                    if TIME_UNTIL_ENCOUNTER == 0:
                        if random.randint(1, 180) == 1:
                            pygame.mixer.music.load("music/wildbattle.ogg")
                            pygame.mixer.music.play(-1)
                            battleTransition(1)
                            if Battle.main(None) == "loss":
                                pTeam.monsters[0].hp = pTeam.monsters[0].stats[0] #NEEDS TO BE REPLACED
                                global playerLost
                                playerLost = True
                            TIME_UNTIL_ENCOUNTER = 180
                            pygame.mixer.music.load("music/" + mapname + ".ogg")
                            pygame.mixer.music.play(-1)

                elif xvel > 0:
                    if self.rect.top < p.collisionRect.bottom - 12:
                        self.rect.right = p.collisionRect.left
                elif xvel < 0:
                    if self.rect.top < p.collisionRect.bottom - 12:
                        self.rect.left = p.collisionRect.right
                elif yvel > 0:
                    if self.rect.top < p.collisionRect.bottom - 12:
                        if isinstance(p, Ledge):
                            self.rect.top = p.collisionRect.bottom
                        else:
                            self.rect.bottom = p.collisionRect.top
                elif yvel < 0:
                    if self.rect.top < p.collisionRect.bottom - 12:
                        self.rect.top = p.collisionRect.bottom - 12
    
    def getsprite(self):
        return self.sprite

class Collidable(Entity):
    def __init__(self, image, pos, *groups):
        super().__init__("map_sprites/" + image + ".png", pos, *groups)
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft = pos)
        self.collisionRect = self.rect

class Ledge(Entity):
    def __init__(self, image, pos, *groups):
        super().__init__("map_sprites/" + image + ".png", pos, *groups)
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft = pos)
        self.collisionRect = pygame.Rect(self.rect.left, int(self.rect.top + TILE_SIZE/2), TILE_SIZE, int(TILE_SIZE/2))

class Noncollidable(Entity):
    def __init__(self, image, pos, *groups):
        super().__init__("map_sprites/" + image + ".png", pos, *groups)
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

class Noncollidable_Under(Entity):
    def __init__(self, image, pos, *groups):
        super().__init__("map_sprites/" + image + ".png", pos, *groups)
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

class ExitBlock(Entity):
    def __init__(self, image, pos, *groups):
        super().__init__("map_sprites/" + image + ".png", pos, *groups)
        self.pos = pos
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft = pos)
        self.collisionRect = self.rect

class EncounterBlock(Entity):
    def __init__(self, image, pos, *groups):
        super().__init__("map_sprites/" + image + ".png", pos, *groups)
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.collisionRect = self.rect

class DBlock(Entity):
    def __init__(self, image, pos, *groups):
        super().__init__("map_sprites/" + image + ".png", pos, *groups)
        self.pos = pos
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.textnum = "FAILURE: NO INPUT"
        self.rect = self.image.get_rect(topleft = pos)
        self.collisionRect = self.rect

class NPC(pygame.sprite.Sprite):
    def __init__(self, name, pos, *groups):
        super().__init__(*groups)
        self.image = pygame.image.load("character_sprites/" + name + "00.png")
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, 64))
        self.rect = self.image.get_rect(topleft = pos)
        self.textnum = "OH NO"
        self.name = name
        self.pos = pos
        self.collisionRect = pygame.Rect(self.rect.left, self.rect.top + 16, TILE_SIZE, TILE_SIZE)
    def update(self):
        self.collisionRect = pygame.Rect(self.rect.left, self.rect.top + 16, TILE_SIZE, TILE_SIZE)
        self.pos = (self.rect.topleft)
    def turnToFace(self, player, level, collidables, noncollidables, npcs):
        screen.blit(player.image, player.pos)
        if player.facing == "up":
            self.image = pygame.image.load("character_sprites/" + self.name + "00.png")
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, 64))
        if player.facing == "down":
            self.image = pygame.image.load("character_sprites/" + self.name + "01.png")
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, 64))
        if player.facing == "right":
            self.image = pygame.image.load("character_sprites/" + self.name + "02.png")
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, 64))
        if player.facing == "left":
            self.image = pygame.image.load("character_sprites/" + self.name + "03.png")
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, 64))
        screen.blit(self.image, self.pos)
        redrawSprites(level, collidables, noncollidables, npcs)
        
class DialogBox(Entity):
    def __init__(self, text, pos, *groups):
        super().__init__("dialogboxx3.png", pos, *groups)
        self.myfont = pygame.font.Font("pokemon_font.ttf", 16)
        self.label = self.myfont.render(text, 1, (0,0,0))
        self.label2 = self.myfont.render("", 1, (0,0,0))
        self.text = "FAILURE: NO INPUT"
        self.lines = []
        self.arrow = pygame.image.load("arrow2.png")
        self.arrowRect = self.arrow.get_rect()
        self.commandString = "None"
    def checkInFront(self, player, level, collidables, noncollidables, npcs):
        for p in collidables:
            if isinstance(p, DBlock) or isinstance(p, NPC):
                if player.rect.collidepoint(p.collisionRect.midbottom) and player.facing == "up":
                    self.open(p, entities, player, level, collidables, noncollidables, npcs)
                elif player.rect.collidepoint((p.collisionRect.midtop[0], p.collisionRect.midtop[1]-1)) and player.facing == "down":
                    self.open(p, entities, player, level, collidables, noncollidables, npcs)
                elif player.rect.collidepoint((p.collisionRect.midleft[0] - 1, p.collisionRect.midleft[1])) and player.facing == "right":
                    self.open(p, entities, player, level, collidables, noncollidables, npcs)
                elif player.rect.collidepoint(p.collisionRect.midright) and player.facing == "left":
                    self.open(p, entities, player, level, collidables, noncollidables, npcs)
                redrawSprites(level, collidables, noncollidables, npcs)
    def open(self, dblock, entities, player, level, collidables, noncollidables, npcs): #Used in overworld --SHOULD REPLACE ALL GROUP PARAMETERS WITH *groups--
        play_sound("sounds/selection.wav")
        with open("textList.txt", "r") as f:
            data = f.readlines()
            line = data[int(dblock.textnum)]
            cutInfo = line.strip().split("*")
            self.text = cutInfo[1]
            self.commandString = cutInfo[2]
        if isinstance(dblock, NPC):
            dblock.turnToFace(player, level, collidables, noncollidables, npcs)

        self.label2 = self.myfont.render("", 1, (0,0,0))
        self.fragmentWords(self.text, entities)
        screen.blit(self.image, (TILE_SIZE, TILE_SIZE * 5))

        doneWriting = False
        self.fragmentText(self.lines[0], entities, self.label, 6)
        self.label = self.myfont.render(self.lines[0], 1, (0,0,0))
        screen.blit(self.label, (TILE_SIZE * 2, TILE_SIZE * 6))
        self.lines = self.lines[1:]
        if len(self.lines) <= 0:
            doneWriting = True
        else:
            self.fragmentText(self.lines[0], entities, self.label2, 7)
            self.label2 = self.myfont.render(self.lines[0], 1, (0,0,0))

            if len(self.lines) <= 1:
                doneWriting = True
            
        while 1:
            entities.change_layer(self, entities.get_top_layer())
            screen.blit(self.image, (TILE_SIZE, TILE_SIZE * 5))
            screen.blit(self.label, (TILE_SIZE * 2, TILE_SIZE * 6))
            screen.blit(self.label2, (TILE_SIZE * 2, TILE_SIZE * 7))
            screen.blit(self.arrow, (TILE_SIZE * 7, TILE_SIZE * 8))
            pygame.display.flip()
            done = False
            for e in pygame.event.get():
                if e.type == QUIT: 
                    pygame.quit()
                    sys.exit()
                if e.type == KEYDOWN and e.key == K_x:
                    play_sound("sounds/selection.wav")
                    if not doneWriting:
                        self.printLines(entities)
                        if len(self.lines) <= 1:
                            doneWriting = True
                    else:
                        done = True
            if done:
                break    
            timer.tick(60)
        print(self.commandString)
        self.processCString()
        
    def processCString(self):
        if self.commandString == "heal":
            for monster in pTeam.monsters:
                monster.hp = monster.stats[0]
        if self.commandString == "pc":
            PC.main()
    def openBattle(self, text, entities): #Used in battles
        self.text = text
        self.label2 = self.myfont.render("", 1, (0,0,0))
        self.fragmentWords(self.text, entities)
        screen.blit(self.image, (TILE_SIZE, TILE_SIZE * 5))

        doneWriting = False
        self.fragmentText(self.lines[0], entities, self.label, 6)
        self.label = self.myfont.render(self.lines[0], 1, (0,0,0))
        screen.blit(self.label, (TILE_SIZE * 2, TILE_SIZE * 6))
        self.lines = self.lines[1:]
        if len(self.lines) <= 0:
            doneWriting = True
        else:
            self.fragmentText(self.lines[0], entities, self.label2, 7)
            self.label2 = self.myfont.render(self.lines[0], 1, (0,0,0))

            if len(self.lines) <= 1:
                doneWriting = True
            
        while 1:
            entities.change_layer(self, entities.get_top_layer())
            screen.blit(self.image, (TILE_SIZE, TILE_SIZE * 5))
            screen.blit(self.label, (TILE_SIZE * 2, TILE_SIZE * 6))
            screen.blit(self.label2, (TILE_SIZE * 2, TILE_SIZE * 7))
            screen.blit(self.arrow, (TILE_SIZE * 7, TILE_SIZE * 8))
            pygame.display.flip()
            for e in pygame.event.get():
                if e.type == QUIT: 
                    pygame.quit()
                    sys.exit()
                if e.type == KEYDOWN and e.key == K_x:
                    play_sound("sounds/selection.wav")
                    if not doneWriting:
                        self.printLines(entities)
                        if len(self.lines) <= 1:
                            doneWriting = True
                    else:
                        screen.blit(self.image, (TILE_SIZE, TILE_SIZE * 5))
                        screen.blit(self.label, (TILE_SIZE * 2, TILE_SIZE * 6))
                        screen.blit(self.label2, (TILE_SIZE * 2, TILE_SIZE * 7))
                        return
                    
            timer.tick(60)
    def fragmentWords(self, ftext, entities):
        words = ftext.split()
        fragmentedWords = ""
        self.lines = []
        for word in words:
            if word == "é":
                self.lines.append(fragmentedWords)
                fragmentedWords = ""
            elif word == "ń":
                self.lines.append(fragmentedWords)
                self.lines.append("")
                fragmentedWords = ""
            elif self.myfont.size(fragmentedWords + " " + word)[0] <= TILE_SIZE * 6:
                fragmentedWords += (word + " ")
                words = words[1:]
            else:
                self.lines.append(fragmentedWords)
                fragmentedWords = word + " "
        self.lines.append(fragmentedWords)
    
    def printLines(self, entities):
        self.label = self.myfont.render(self.lines[0], 1, (0,0,0))

        rect = pygame.Rect((TILE_SIZE * 2, TILE_SIZE * 6), (TILE_SIZE * 6, TILE_SIZE))
        screen.fill((255, 255, 255), rect, 0)
        screen.blit(self.label, (TILE_SIZE * 2, TILE_SIZE * 6))
        arrowrect = pygame.Rect((TILE_SIZE * 7, TILE_SIZE * 8), (int(TILE_SIZE/2), int(TILE_SIZE/2)))
        screen.fill((255, 255, 255), arrowrect, 0)
        self.lines = self.lines[1:]
        if len(self.lines) >= 1:
            self.fragmentText(self.lines[0], entities, self.label2, 7)
            self.label2 = self.myfont.render(self.lines[0], 1, (0,0,0))
            
    def fragmentText(self, ftext, entities, label, y):
        fragmentedText = ""
        for i in range(len(ftext) - 1):
            fragmentedText += ftext[i]
            if self.myfont.size(fragmentedText)[0] > TILE_SIZE * 6:
                self.text = fragmentedText[:len(fragmentedText) - 1]
                return
            label = self.myfont.render(fragmentedText, 1, (0,0,0))
            entities.change_layer(self, entities.get_top_layer())

            rect = pygame.Rect((TILE_SIZE * 2, TILE_SIZE * y), (TILE_SIZE * 6, TILE_SIZE))
            screen.fill((255, 255, 255), rect, 0)
            screen.blit(label, (TILE_SIZE * 2, TILE_SIZE * y))
            
            pygame.display.update()
            pygame.display.flip()
            pygame.time.wait(10)
            for e in pygame.event.get():
                if e.type == QUIT: 
                    pygame.quit()
                    sys.exit()
                if e.type == KEYDOWN and e.key == K_x:
                    return

class MenuButton(pygame.sprite.Sprite):
    def __init__(self, pos, text, *groups):
        super().__init__(*groups)
        self.myfont = pygame.font.Font("pokemon_font.ttf", 16)
        self.image = pygame.image.load("menubutton2.png")
        self.image = pygame.transform.scale(self.image, (TILE_SIZE * 3, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos
        self.label = self.myfont.render(text, 1, (0,0,0))
        self.labelrect = self.label.get_rect()
        self.labelrect.center = self.rect.center

def yesNo(*groups):
    box = pygame.sprite.Sprite()
    box.image = pygame.image.load("yesno.png")
    box.image = pygame.transform.scale(box.image, (TILE_SIZE*3, int(TILE_SIZE*1.5)))
    box.rect = box.image.get_rect(topleft = (TILE_SIZE*6,int(TILE_SIZE*7.5)))
    for group in groups:
        group.add(box)
    yes = Battle.TextImage((int(TILE_SIZE*6.5),TILE_SIZE*8), "YES", *groups)
    no = Battle.TextImage((int(TILE_SIZE*7.5),TILE_SIZE*8), "NO", *groups)
    arrow = pygame.sprite.Sprite()
    arrow.image = pygame.image.load("selectarrow.png")
    arrow.image = pygame.transform.scale(arrow.image, (int(TILE_SIZE/2), int(TILE_SIZE/2)))
    arrow.rect = arrow.image.get_rect(topleft = (int(TILE_SIZE*6.125),TILE_SIZE*8))
    location = True
    while 1:
        groups.draw(screen)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                return
            if e.type == KEYDOWN:
                if e.key == K_x:
                    return location
                if e.key == K_LEFT or e.key == K_RIGHT:
                    if location == True:
                        location = False
                        arrow.rect.left += TILE_SIZE
                    else:
                        location = True
                        arrow.rect.left -= TILE_SIZE
        timer.tick(30)

def play_sound(path):
  global sound_library
  sound = sound_library.get(path)
  if sound == None:
    canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
    sound = pygame.mixer.Sound(canonicalized_path)
    sound_library[path] = sound
  sound.play()

def stop_sound(path):
  global sound_library
  sound = sound_library.get(path)
  sound.stop()

if __name__ == "__main__":
    main(NEXT_NAME)