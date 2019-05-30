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

class pSprite(pygame.sprite.Sprite):
    def __init__(self, infoList, pos, *groups):
        super().__init__(*groups)
        if infoList[0] != 0:
            with open("pkmnBasicInfo.txt", "r") as f:
                info = list(f)[int(infoList[0])].split()
            self.species = info[0]
        else:
            self.species = "UNKNOWN"
        self.image = pygame.image.load("pokemon_sprites/" + self.species + "Mini.png")
        self.rect = self.image.get_rect(topleft = pos)

def main():
    layersC = pygame.sprite.LayeredUpdates()

    background = pygame.sprite.Sprite()
    background.image = pygame.image.load("pcbackground.png")
    background.image = pygame.transform.scale(background.image, (TILE_SIZE*7, TILE_SIZE*7))
    background.rect = background.image.get_rect(topleft = (int(TILE_SIZE*1.5), int(TILE_SIZE*1.5)))
    layersC.add(background)

    selector = pygame.sprite.Sprite()
    selector.image = pygame.image.load("pcselector2.png")
    selector.rect = selector.image.get_rect(topleft = (int(TILE_SIZE*1.5) + 8, int(TILE_SIZE*1.5) + 8))
    layersC.add(selector)
    selectorLocation = [0,0]

    pokemon = []
    for j in range(64):
        pokemon.append([0])
    with open("PCList.txt") as f:
        i = 0
        for data in f:
            pokemon[i]=data.split()
            i += 1
    
    pokeSprites = pygame.sprite.Group()
    for i in range(pokemon.__len__()):
        pokeSprites.add(pSprite(pokemon[i], (80 + 40*(i%8),80 + 40*int(i/8)), pokeSprites))
    layersC.add(pokeSprites)

    infoHolder = pygame.sprite.Sprite()
    infoHolder.image = pygame.image.load("pcinfoholder2.png")
    infoHolder.image = pygame.transform.scale(infoHolder.image, (TILE_SIZE*7, int(TILE_SIZE*1.5)))
    infoHolder.rect = infoHolder.image.get_rect(topleft = (int(TILE_SIZE*1.5), 0))
    layersC.add(infoHolder)

    nameNSpecies = TextImage((TILE_SIZE*2,24), getSpecies(pokemon[0][0]), layersC)
    nameNSpecies.resizeText(8)

    while 1:
        screen.fill((255, 255, 255))
        layersC.draw(screen)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_RIGHT:
                    if selectorLocation[0] < 7:
                        selectorLocation[0] += 1
                        selector.rect.left += 40
                    else:
                        selectorLocation[0] = 0
                        selector.rect.left = 80
                if e.key == K_LEFT:
                    if selectorLocation[0] > 0:
                        selectorLocation[0] -= 1
                        selector.rect.left -= 40
                    else:
                        selectorLocation[0] = 7
                        selector.rect.left = 360
                if e.key == K_DOWN:
                    if selectorLocation[1] < 7:
                        selectorLocation[1] += 1
                        selector.rect.top += 40
                    else:
                        selectorLocation[1] = 0
                        selector.rect.top = 80
                if e.key == K_UP:
                    if selectorLocation[1] > 0:
                        selectorLocation[1] -= 1
                        selector.rect.top -= 40
                    else:
                        selectorLocation[1] = 7
                        selector.rect.top = 360
                if e.key == K_x:
                    print(getSpecies(int(pokemon[selectorLocation[0]+8*selectorLocation[1]][0])))
                if e.key == K_z:
                    return
                if not pokemon[selectorLocation[0]+8*selectorLocation[1]][0] == 0:
                    nameNSpecies.update(getSpecies(int(pokemon[selectorLocation[0]+8*selectorLocation[1]][0])))
                
        timer = pygame.time.Clock()
        timer.tick(30)