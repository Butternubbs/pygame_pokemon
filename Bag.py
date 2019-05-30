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

class Item():
    def __init__(self):
        self.id = 0
        self.name = "UNKNOWN ITEM"
        self.infoString = "None"
        self.pocket = "Items"
        self.description = "UNKNOWN ITEM"
    def identify(self, id):
        self.id = id
        with open("itemIDs.txt", "r") as f:
            info = f.readlines()[int(id)].split("|")
        self.name = info[1]
        self.infoString = info[2]
        self.pocket = info[3]
        self.description = info[4]

layersB = pygame.sprite.LayeredUpdates()
listHolder = None
bagSprite = None
bagSprites = ["bagItems.png", "bagBalls.png", "bagTMs.png", "bagKeyItems.png"]
bagLabel = None
bagLabels = ["ITEMS", "BALLS", "TMs/HMs", "KEY ITEMS"]
itemList = [[],[],[],[]]
itemListAmounts = [[],[],[],[]]
itemListGraphics = []

def main():
    global listHolder
    listHolder = pygame.sprite.Sprite()
    listHolder.image = pygame.image.load("bagListHolder2.png")
    listHolder.image = pygame.transform.scale(listHolder.image, (TILE_SIZE * 4, TILE_SIZE * 8))
    listHolder.rect = listHolder.image.get_rect(topleft = (TILE_SIZE * 5, TILE_SIZE))
    layersB.add(listHolder)

    global bagSprite
    bagSprite = pygame.sprite.Sprite()
    bagSprite.image = pygame.image.load("bagItems.png")
    bagSprite.image = pygame.transform.scale(bagSprite.image, (ENLARGE_FACTOR * 58, ENLARGE_FACTOR * 66))
    bagSprite.rect = bagSprite.image.get_rect(topleft = (TILE_SIZE * 1, TILE_SIZE * 1))
    layersB.add(bagSprite)

    global bagLabel
    bagLabel = Battle.TextImage((TILE_SIZE, TILE_SIZE * 5), "ITEMS", layersB)
    bagLabel.rect.center = (ENLARGE_FACTOR * 45, TILE_SIZE * 5.5)
    layersB.add(bagLabel)

    global itemList
    global itemListGraphics
    with open("bagItems.txt", "r") as f:
        stuff = f.readlines()
        it = 0
        for line in stuff:
            itemList[0].append(Item())
            itemList[0][it].identify(line.split()[0])
            itemListAmounts[0].append(line.split()[1])
            if it < 14 and not itemList[0][it] == None:
                itemListGraphics.append(Battle.TextImage((TILE_SIZE * 5.5, (TILE_SIZE * it)/2 + (24 * ENLARGE_FACTOR)), itemList[0][it].name, layersB))
                itemListGraphics.append(Battle.TextImage((TILE_SIZE * 9, (TILE_SIZE * it)/2 + (24 * ENLARGE_FACTOR)), ("x" + itemListAmounts[0][it]), layersB))
            it += 1
    with open("bagBalls.txt", "r") as f:
        stuff = f.readlines()
        it = 0
        for line in stuff:
            itemList[1].append(Item())
            itemList[1][it].identify(line.split()[0])
            itemListAmounts[1].append(line.split()[1])
            it += 1
    with open("bagTMs.txt", "r") as f:
        stuff = f.readlines()
        it = 0
        for line in stuff:
            itemList[2].append(Item())
            itemList[2][it].identify(line.split()[0])
            itemListAmounts[2].append(line.split()[1])
            it += 1
    with open("bagKeyItems.txt", "r") as f:
        stuff = f.readlines()
        it = 0
        for line in stuff:
            itemList[3].append(Item())
            itemList[3][it].identify(line.split()[0])
            itemListAmounts[3].append(line.split()[1])
            it += 1
    layersB.add(itemListGraphics)

    global selectArrow
    selectArrow = pygame.sprite.Sprite()
    selectArrow.image = pygame.image.load("selectArrow.png")
    selectArrow.image = pygame.transform.scale(selectArrow.image, (ENLARGE_FACTOR * 8, ENLARGE_FACTOR * 8))
    selectArrow.rect = selectArrow.image.get_rect(topleft = (TILE_SIZE * 5 + ENLARGE_FACTOR * 4, TILE_SIZE * 1.5))
    layersB.add(selectArrow)

    global descHolder
    descHolder = pygame.sprite.Sprite()
    descHolder.image = pygame.image.load("descHolder4.png")
    descHolder.image = pygame.transform.scale(descHolder.image, (ENLARGE_FACTOR * 72, ENLARGE_FACTOR * 44))
    descHolder.rect = descHolder.image.get_rect(topleft = (ENLARGE_FACTOR * 10, TILE_SIZE * 6 - ENLARGE_FACTOR * 3))
    layersB.add(descHolder)



def requestItem():
    main()
    p = 0 #pocket
    r = 0 #row
    ar = 0 #arrow row
    global bagSprite
    global itemListGraphics
    while 1:
        Battle.screen.fill((255, 255, 255))
        showDesc(itemList[p][r].description, (TILE_SIZE*1, TILE_SIZE*6))
        layersB.draw(screen)
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_ESCAPE:
                    return
                if e.key == K_RIGHT:
                    if p < 3:
                        p += 1
                    else:
                        p = 0
                    bagSprite.image = pygame.image.load(bagSprites[p])
                    bagSprite.image = pygame.transform.scale(bagSprite.image, (ENLARGE_FACTOR * 58, ENLARGE_FACTOR * 66))
                    bagLabel.update(bagLabels[p])
                    bagLabel.rect.center = (ENLARGE_FACTOR * 45, TILE_SIZE * 5.5)
                    selectArrow.rect.top = TILE_SIZE * 1.5
                    r = 0
                    ar = 0
                    layersB.remove(itemListGraphics)
                    itemListGraphics = []
                    for i in range(itemList[p].__len__()):
                        if i < 14:
                            itemListGraphics.append(Battle.TextImage((TILE_SIZE * 5.5, (TILE_SIZE * i)/2 + (24 * ENLARGE_FACTOR)), itemList[p][i].name, layersB))
                            itemListGraphics.append(Battle.TextImage((TILE_SIZE * 9, (TILE_SIZE * i)/2 + (24 * ENLARGE_FACTOR)), ("x" + itemListAmounts[p][i]), layersB))
                        else:
                            break
                    layersB.add(itemListGraphics)

                if e.key == K_LEFT:
                    if p > 0:
                        p -= 1
                    else:
                        p = 3
                    bagSprite.image = pygame.image.load(bagSprites[p])
                    bagSprite.image = pygame.transform.scale(bagSprite.image, (ENLARGE_FACTOR * 58, ENLARGE_FACTOR * 66))
                    bagLabel.update(bagLabels[p])
                    bagLabel.rect.center = (ENLARGE_FACTOR * 45, TILE_SIZE * 5.5)
                    selectArrow.rect.top = TILE_SIZE * 1.5
                    r = 0
                    ar = 0
                    layersB.remove(itemListGraphics)
                    itemListGraphics = []
                    for i in range(itemList[p].__len__()):
                        if i < 14:
                            itemListGraphics.append(Battle.TextImage((TILE_SIZE * 5.5, (TILE_SIZE * i)/2 + (24 * ENLARGE_FACTOR)), itemList[p][i].name, layersB))
                            itemListGraphics.append(Battle.TextImage((TILE_SIZE * 9, (TILE_SIZE * i)/2 + (24 * ENLARGE_FACTOR)), ("x" + itemListAmounts[p][i]), layersB))
                        else:
                            break
                    layersB.add(itemListGraphics)

                if e.key == K_DOWN:
                    if ar > 11 and r < itemList[p].__len__() - 2:
                        layersB.remove(itemListGraphics.pop(0))
                        layersB.remove(itemListGraphics.pop(0))
                        for g in itemListGraphics:
                            g.rect.top -= TILE_SIZE/2
                        itemListGraphics.append(Battle.TextImage((TILE_SIZE * 5.5, (TILE_SIZE * 13)/2 + (24 * ENLARGE_FACTOR)), itemList[p][r+2].name, layersB))
                        layersB.add(itemListGraphics[-1])
                        itemListGraphics.append(Battle.TextImage((TILE_SIZE * 9, (TILE_SIZE * i)/2 + (24 * ENLARGE_FACTOR)), ("x" + itemListAmounts[p][r+2]), layersB))
                        layersB.add(itemListGraphics[-1])
                        r += 1
                    elif r < itemList[p].__len__() - 1:
                        selectArrow.rect.top += TILE_SIZE/2
                        ar += 1
                        r += 1
                if e.key == K_UP:
                    if ar < 2 and r > 1:
                        layersB.remove(itemListGraphics.pop(itemListGraphics.__len__() -1))
                        layersB.remove(itemListGraphics.pop(itemListGraphics.__len__() -1))
                        for g in itemListGraphics:
                            g.rect.top += TILE_SIZE/2
                        itemListGraphics.insert(0,Battle.TextImage((TILE_SIZE * 9, 24 * ENLARGE_FACTOR), itemListAmounts[p][r - 2], layersB))
                        layersB.add(itemListGraphics[0])
                        itemListGraphics.insert(0,Battle.TextImage((TILE_SIZE * 5.5, 24 * ENLARGE_FACTOR), ("x" + itemList[p][r - 2].name), layersB))
                        layersB.add(itemListGraphics[0])
                        r -= 1
                    elif r > 0:
                        selectArrow.rect.top -= TILE_SIZE/2
                        ar -= 1
                        r -= 1
                if e.key == K_x:
                    print(itemList[p][r].name)
                    layersB.empty()
                    screen.fill((255,255,255))
                    return itemList[p][r]
                if e.key == K_z:
                    layersB.empty()
                    screen.fill((255,255,255))
                    return "back"

        timer = pygame.time.Clock()
        timer.tick(30)
        pygame.display.update()
def showDesc(text, pos):
    words = [word.split(' ') for word in text.splitlines()]
    font = pygame.font.Font("pokemon_font.ttf", 16)
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = (TILE_SIZE * 4.5, TILE_SIZE * 3)
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, (0,0,0))
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]
                y += word_height
            screen.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]
        y += word_height