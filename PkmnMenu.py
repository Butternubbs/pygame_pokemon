import pygame
from pygame import *
import random
import TeamInfo
from TeamInfo import *
import sys
import Overworld
from Overworld import *
import os
import pypokedex
import Battle
from Battle import *

class PkmnSelector(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(layersP)
        self.image = pygame.image.load("pkmnSelector.png")
        self.image = pygame.transform.scale(self.image, (TILE_SIZE*3,int(TILE_SIZE*2.5)))
        self.pos = (int(TILE_SIZE/2), TILE_SIZE*2 - ENLARGE_FACTOR*4)
        self.rect = self.image.get_rect(topleft = self.pos)
        self.gridx = 0
        self.gridy = 0

layersP = pygame.sprite.LayeredUpdates()
pokemonHolders = []
miniSprites = []
names = []
levels = []
hps = []
hpBars = []
colors = []
title = None

def main(pTeam):
    global layersP
    global pokemonHolders
    global miniSprites
    global names
    global levels
    global hps
    global hpBars
    global colors
    global title

    title = Battle.TextImage((TILE_SIZE, TILE_SIZE * 5), "POKEMON", layersP)
    title.rect.center = (TILE_SIZE*5, TILE_SIZE)
    layersP.add(title)

    pokemonHolders.clear()
    for i in range(6):
        pokemonHolders.append(pygame.sprite.Sprite())
        pokemonHolders[i].image = pygame.image.load("pkmnHolder2.png")
        pokemonHolders[i].image = pygame.transform.scale(pokemonHolders[i].image, (int(TILE_SIZE*2.5), TILE_SIZE*2))
        pokemonHolders[i].rect = pokemonHolders[i].image.get_rect(topleft = (int(TILE_SIZE*3/4) + (3*TILE_SIZE * int(i/2)), TILE_SIZE*2 + int(TILE_SIZE*2.5*int(i%2))))
        layersP.add(pokemonHolders[i])

    miniSprites.clear()
    for i in range(6):
        miniSprites.append(pygame.sprite.Sprite())
        miniSprites[i].image = pygame.image.load("pokemon_sprites/" + pTeam.monsters[i].species + "Mini.png")
        miniSprites[i].rect = miniSprites[i].image.get_rect(topleft = (TILE_SIZE - ENLARGE_FACTOR + (3*TILE_SIZE * int(i/2)), int(TILE_SIZE*2.25) + int(TILE_SIZE*2.5*int(i%2))))
        layersP.add(miniSprites[i])
    
    names.clear()
    for i in range(6):
        names.append(Battle.TextImage((TILE_SIZE-ENLARGE_FACTOR + (3*TILE_SIZE * int(i/2)), int(TILE_SIZE*3.625) + int(TILE_SIZE*2.5*int(i%2))), pTeam.monsters[i].name, layersP))
        names[i].resizeText(8)
        layersP.add(names[i])

    levels.clear()
    for i in range(6):
        levels.append(Battle.TextImage((ENLARGE_FACTOR*43+(3*TILE_SIZE * int(i/2)), int(TILE_SIZE*3.625) + int(TILE_SIZE*2.5*int(i%2))), "L:" + str(pTeam.monsters[i].level), layersP))
        levels[i].resizeText(8)
        layersP.add(levels[i])
    
    hps.clear()
    for i in range(6):
        hps.append(Battle.TextImage((TILE_SIZE*2 + (3*TILE_SIZE * int(i/2)), TILE_SIZE*3 + int(TILE_SIZE*2.5*int(i%2))), (str(pTeam.monsters[i].hp) + "/ " + str(pTeam.monsters[i].stats[0])), layersP))
        hps[i].resizeText(8)
        layersP.add(hps[i])

    hpBars.clear()
    colors.clear()
    for i in range(6):
        hpBars.append(pygame.Rect(TILE_SIZE+(3*TILE_SIZE * int(i/2)), TILE_SIZE*2 + ENLARGE_FACTOR*21 + int(TILE_SIZE*2.5*int(i%2)), int(TILE_SIZE*2*(pTeam.monsters[i].hp/pTeam.monsters[i].stats[0])), ENLARGE_FACTOR*2))
        if pTeam.monsters[i].hp>pTeam.monsters[i].stats[0]/2:
            colors.append(Color(0,255,0,0))
        if pTeam.monsters[i].hp<=pTeam.monsters[i].stats[0]/2:
            colors.append(Color(255,255,0,0))
        if pTeam.monsters[i].hp<=pTeam.monsters[i].stats[0]/5:
            colors[i]=Color(255,0,0,0)
            
def battleSwitch(pTeam):
    main(pTeam)
    selector = PkmnSelector()
    layersP.add(selector)
    title.update("Which Pokemon will be sent out?")
    title.rect.center = (TILE_SIZE*5, TILE_SIZE)
    selectedMonster = pTeam.monsters[0]
    while 1:
        screen.fill((255, 255, 255))
        layersP.draw(screen)
        for i in range(6):
            pygame.draw.rect(screen, colors[i], hpBars[i])
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    return
                    layersP.empty()
                if e.key == K_RIGHT:
                    if selector.gridx < 2:
                        selector.gridx += 1
                    else:
                        selector.gridx = 0
                if e.key == K_LEFT:
                    if selector.gridx > 0:
                        selector.gridx -= 1
                    else:
                        selector.gridx = 2
                if e.key == K_DOWN:
                    if selector.gridy < 1:
                        selector.gridy += 1
                    else:
                        selector.gridy = 0
                if e.key == K_UP:
                    if selector.gridy > 0:
                        selector.gridy -= 1
                    else:
                        selector.gridy = 1
                if e.key == K_x:
                    selectedMonster = pTeam.monsters[selector.gridx*2 + selector.gridy]
                    if selectedMonster == pTeam.monsters[0]:
                        title.update("That Pokemon is already in battle!")
                        title.rect.center = (TILE_SIZE*5, TILE_SIZE)
                if e.key == K_z:
                    layersP.empty()
                    return "back"
                selector.pos = (int(TILE_SIZE/2) + TILE_SIZE*3*selector.gridx, TILE_SIZE*2 - ENLARGE_FACTOR*4 + int(TILE_SIZE*2.5*selector.gridy))
                selector.rect = selector.image.get_rect(topleft = selector.pos)
        if selectedMonster != pTeam.monsters[0]:
            temp = pTeam.monsters[0]
            pTeam.monsters[0] = selectedMonster
            pTeam.monsters[selector.gridx*2 + selector.gridy] = temp
            layersP.empty()
            return selectedMonster
        timer = pygame.time.Clock()
        timer.tick(30)