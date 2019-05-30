import pygame
from pygame import *
import random
import TeamInfo
from TeamInfo import *
import sys
import Overworld
from Overworld import *
import Bag
from Bag import *
import PkmnMenu
from PkmnMenu import *
import os
import pypokedex

class Selector(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(layers)
        self.pos = pos
        self.image = pygame.image.load("select2.png")
        self.image = pygame.transform.scale(self.image, (TILE_SIZE * 2, TILE_SIZE))
        self.rect = self.image.get_rect(topleft = (TILE_SIZE * 4.5, TILE_SIZE * 6.5))
        self.selected = 0
        self.wait = 0
    def update(self):
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_UP:
                    if self.selected <= 1:
                        self.selected += 2
                        self.rect.top += TILE_SIZE
                    else:
                        self.selected -= 2
                        self.rect.top -= TILE_SIZE
                if event.key == K_DOWN:
                    if self.selected <= 1:
                        self.selected += 2
                        self.rect.top += TILE_SIZE
                    else:
                        self.selected -= 2
                        self.rect.top -= TILE_SIZE
                if event.key == K_LEFT:
                    if self.selected % 2 == 0:
                        self.selected += 1
                        self.rect.left += TILE_SIZE * 2
                    else:
                        self.selected -= 1
                        self.rect.left -= TILE_SIZE * 2
                if event.key == K_RIGHT:
                    if self.selected % 2 == 0:
                        self.selected += 1
                        self.rect.left += TILE_SIZE * 2
                    else:
                        self.selected -= 1
                        self.rect.left -= TILE_SIZE * 2
                if event.key == K_x:
                    Overworld.play_sound("sounds/selection.wav")
                    return True
                if event.key == K_z:
                    return "back"
                self.pos = (self.rect.topleft)
        pygame.event.clear()
        return False

class Button(pygame.sprite.Sprite):
    def __init__(self, pos, text, text2):
        super().__init__(layers)
        self.myfont = pygame.font.Font("pokemon_font.ttf", 8)
        self.image = pygame.image.load("button.png")
        self.image = pygame.transform.scale(self.image, (TILE_SIZE * 2, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = pos
        self.label = self.myfont.render(text, 1, (0,0,0))
        self.labelrect = self.label.get_rect()
        self.labelrect.center = self.rect.center
        self.labelrect.top -= ENLARGE_FACTOR
        self.label2 = self.myfont.render(text2, 1, (0,0,0))
        self.label2rect = self.label2.get_rect()
        self.label2rect.center = self.rect.center
        self.label2rect.top += ENLARGE_FACTOR*2
    def update2(self, text2):
        self.label2 = self.myfont.render(text2, 1, (0,0,0))
        self.label2rect = self.label2.get_rect()
        self.label2rect.center = self.rect.center
        self.label2rect.top += ENLARGE_FACTOR*2

class HPBar(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(layers)
        self.pos = pos
        self.image = pygame.image.load("hpbar2.png")
        self.image = pygame.transform.scale(self.image, (int(68 * ENLARGE_FACTOR), int(6 * ENLARGE_FACTOR)))
        self.rect = self.image.get_rect(topleft=pos)

class EXPBar(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(layers)
        self.pos = pos
        self.image = pygame.image.load("expbar.png")
        self.image = pygame.transform.scale(self.image, (int(76 * ENLARGE_FACTOR), int(4 * ENLARGE_FACTOR)))
        self.rect = self.image.get_rect(topleft=pos)

class TextImage(pygame.sprite.Sprite):
    def __init__(self, pos, text, *groups):
        super().__init__(*groups)
        self.text = text
        self.pos = pos
        self.myfont = pygame.font.Font("pokemon_font.ttf", 16)
        self.image = self.myfont.render(str(text), 1, (0,0,0))
        self.rect = self.image.get_rect(topleft=pos)
    def update(self, text):
        self.text = text
        self.image = self.myfont.render(str(text), 1, (0,0,0))
        self.rect = self.image.get_rect(topleft=self.pos)
    def resizeText(self, size):
        self.myfont = pygame.font.Font("pokemon_font.ttf", size)
        self.image = self.myfont.render(str(self.text), 1, (0,0,0))
        self.rect = self.image.get_rect(topleft=self.pos)

pTeam = Overworld.pTeam
oTeam = None
layers = pygame.sprite.LayeredUpdates()
pSprite = pygame.sprite.Sprite()
oSprite = pygame.sprite.Sprite()
pHPratio = None
pLvl = None
pNextTurns = [None] * 2
pNextItem = None
oNextTurns = [None] * 2
buttons = []
select = None
pHP = None
oHP = None
pEXP = None
wild = False
runAttempts = 0

def main(battleID):
    global pTeam
    global oTeam
    pTeam = Overworld.pTeam
    global wild
    if battleID is None: #WILD BATTLE- Pokemon can be caught, the player can run, and wild Pokemon can flee.
        wild = True
        oTeam = Team()
        oTeam.wildTeam(Overworld.mapname) #Replace this line with a system that determines wild pokemon
    dbox = Overworld.DialogBox("ERROR", (TILE_SIZE * 1, TILE_SIZE * 5))
    layers.add(dbox)

    background = pygame.sprite.Sprite()
    background.image = pygame.image.load("grasspixel.jpg")
    background.rect = background.image.get_rect(topleft = (-4*ENLARGE_FACTOR, int(TILE_SIZE*5.5)))
    layers.add(background)

    global pSprite
    global oSprite
    
    
    oSprite.image = pygame.image.load(oTeam.monsters[0].frontImage) #change this to backImage when I import the back images
    oSprite.image = pygame.transform.scale(oSprite.image, (int(oSprite.image.get_width() * 2), int(oSprite.image.get_height() * 2)))
    oSprite.rect = oSprite.image.get_rect(topleft = (TILE_SIZE * 7, TILE_SIZE * 1))
    layers.add(oSprite)

    global pHP
    global oHP
    global pEXP
    pHP = HPBar((TILE_SIZE * 5, TILE_SIZE * 3.5))
    layers.add(pHP)
    oHP = HPBar((TILE_SIZE * 1, TILE_SIZE * 1))
    layers.add(oHP)
    pEXP = EXPBar((TILE_SIZE * 5, TILE_SIZE * 4.5))
    layers.add(pEXP)
    
    global pLvl
    pLvl = TextImage((TILE_SIZE * 8, TILE_SIZE * 3), "L:" + str(pTeam.monsters[0].level), layers)
    layers.add(pLvl)
    oLvl = TextImage((TILE_SIZE * 4, TILE_SIZE * 0.5), "L:" + str(oTeam.monsters[0].level), layers)
    layers.add(oLvl)

    global pName
    global oName
    pName = TextImage((TILE_SIZE * 5, TILE_SIZE * 3), pTeam.monsters[0].name.upper(), layers)
    layers.add(pName)
    oName = TextImage((TILE_SIZE * 1, TILE_SIZE * 0.5), oTeam.monsters[0].name.upper(), layers)
    layers.add(oName)

    global pHPratio
    pHPratio = TextImage((TILE_SIZE * 6.5, TILE_SIZE * 4), str(pTeam.monsters[0].hp) + "/ " + str(pTeam.monsters[0].stats[0]), layers)
    layers.add(pHPratio)

    emptyBox = pygame.sprite.Sprite()
    emptyBox.image = pygame.image.load("dialogBoxx3.png")
    emptyBox.rect = oSprite.image.get_rect(topleft = (TILE_SIZE, TILE_SIZE * 5))
    layers.add(emptyBox)

    buttons.append(Button((TILE_SIZE * 4.5, TILE_SIZE * 6.5), "FIGHT", ""))
    buttons.append(Button((TILE_SIZE * 4.5, TILE_SIZE * 7.5), "$%", ""))
    buttons.append(Button((TILE_SIZE * 6.5, TILE_SIZE * 6.5), "BAG", ""))
    buttons.append(Button((TILE_SIZE * 6.5, TILE_SIZE * 7.5), "RUN", ""))

    global select
    select = Selector((TILE_SIZE * 4.5, TILE_SIZE * 6.5))

    trainer = pygame.sprite.Sprite()
    trainer.image = pygame.image.load("character_sprites/charstand.png")
    trainer.image = pygame.transform.scale(trainer.image, (int(TILE_SIZE*4), int(TILE_SIZE*4)))
    trainer.rect = trainer.image.get_rect(topleft = (TILE_SIZE, TILE_SIZE))
    layers.add(trainer)

    Overworld.screen.fill((255, 255, 255))
    layers.draw(screen)
    pygame.display.update()
    dbox.openBattle("A wild " + oTeam.monsters[0].species + " appeared!", layers)

    global runAttempts
    runAttempts = 0

    ball = pygame.sprite.Sprite()
    ball.image = pygame.image.load("throwball.png")
    ball.image = pygame.transform.scale(ball.image, (TILE_SIZE, TILE_SIZE))
    ball.rect = ball.image.get_rect(topleft = (TILE_SIZE, TILE_SIZE*3 + 12))
    ball.orig_image = ball.image
    layers.add(ball)

    for i in range(60):
        pygame.draw.rect(screen, Color(255,255,255), trainer.rect)
        trainer.rect.left = TILE_SIZE - int(ENLARGE_FACTOR*i*1.25)
        trainer.image = pygame.transform.scale(pygame.image.load("character_sprites/throw"+str(int(i/15))+".png"), trainer.rect.size)
        if i <=8:
            ball.rect.left -= int(ENLARGE_FACTOR*1.25)
        if i > 8 and i <= 24:
            ball.rect.top -= int(ENLARGE_FACTOR)
            ball.rect.left -= int(ENLARGE_FACTOR)
        if i <= 45 and i > 24:
            pygame.draw.rect(screen, Color(255,255,255), ball.rect)
            ball.image = pygame.transform.rotate(ball.orig_image, i*-20)
            ball.rect = ball.image.get_rect()
            ball.rect.center = (24 + 3*i, 120 + ((i-24)*(i-24))/6)
        elif i > 45 and i <= 50:
            ball.image = ball.orig_image
            ball.rect = ball.image.get_rect(center = (24 + 135, 120+74))
        elif i > 50 and i <= 55:
            ball.image = pygame.image.load("ballpartopen.png")
            ball.image = pygame.transform.scale(ball.image, (TILE_SIZE, TILE_SIZE))
        elif i > 55:
            ball.image = pygame.image.load("ballfullopen.png")
            ball.image = pygame.transform.scale(ball.image, (TILE_SIZE, TILE_SIZE))
        screen.blit(ball.image, ball.rect)
        screen.blit(trainer.image, trainer.rect)
        screen.blit(oHP.image, oHP.rect)
        screen.blit(oLvl.image, oLvl.rect)
        pygame.display.update()
        timer.tick(60)
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()

    pSprite.image = pygame.image.load(pTeam.monsters[0].backImage)
    pSprite.image = pygame.transform.scale(pSprite.image, (int(pSprite.image.get_width() * 2), int(pSprite.image.get_height() * 2)))
    pSprite.rect = pSprite.image.get_rect(topleft = (TILE_SIZE * 2, TILE_SIZE * 3))
    layers.add(pSprite)
    screen.blit(pSprite.image, pSprite.rect)

    while 1:
        if pTeam.monsters[0].hp <= pTeam.monsters[0].stats[0]/5:
            color = Color(255, 0, 0, 255)
        elif pTeam.monsters[0].hp <= pTeam.monsters[0].stats[0]/2:
            color = Color(255, 255, 0, 255)
        else:
            color = Color(0, 255, 0, 255)
        screen.blit(pHP.image, pHP.pos)
        pygame.draw.rect(screen, color, (pHP.pos[0] + (16 * ENLARGE_FACTOR), pHP.pos[1] + ENLARGE_FACTOR, (pTeam.monsters[0].hp/pTeam.monsters[0].stats[0]) * (48 * ENLARGE_FACTOR), ENLARGE_FACTOR * 3))
        if oTeam.monsters[0].hp <= oTeam.monsters[0].stats[0]/5:
            color = Color(255, 0, 0, 255)
        elif oTeam.monsters[0].hp <= oTeam.monsters[0].stats[0]/2:
            color = Color(255, 255, 0, 255)
        else:
            color = Color(0, 255, 0, 255)
        screen.blit(oHP.image, oHP.pos)
        pygame.draw.rect(screen, color, (oHP.pos[0] + (16 * ENLARGE_FACTOR), oHP.pos[1] + ENLARGE_FACTOR, (oTeam.monsters[0].hp/oTeam.monsters[0].stats[0]) * (48 * ENLARGE_FACTOR), ENLARGE_FACTOR * 3))

        pygame.draw.rect(screen, Color(0, 255, 255, 255), (pEXP.pos[0] + (8 * ENLARGE_FACTOR), pEXP.pos[1] + ENLARGE_FACTOR, ((pTeam.monsters[0].exp - calcBaseEXP(pTeam.monsters[0].level, 3))/(calcBaseEXP(pTeam.monsters[0].level + 1, 3) - calcBaseEXP(pTeam.monsters[0].level, 3))) * (64 * ENLARGE_FACTOR), ENLARGE_FACTOR * 2))

        battleStatus = doTurn(dbox)
        if battleStatus == "running" or battleStatus == "catch":
            break
        elif battleStatus == "pwin":
            dbox.openBattle("You won!", layers)
            break
        elif battleStatus == "owin":
            dbox.openBattle("You ran out of usable Pokemon!", layers)
            dbox.openBattle("You whited out!", layers)
            break
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                return
        timer.tick(30)
    #Post-battle resetting:
    for m in pTeam.monsters:
        m.stats = m.normStats.copy()
        m.statStages = [0,0,0,0,0,0,0,0]
    i = 0
    for turn in pNextTurns:
        pNextTurns[i] = None
        i += 1
    i = 0
    for turn in oNextTurns:
        oNextTurns[i] = None
        i += 1
    buttons.clear()
    layers.empty()
    if battleStatus == "owin":
        return "loss"
def barBlit():
    if pTeam.monsters[0].hp <= pTeam.monsters[0].stats[0]/5:
        color = Color(255, 0, 0, 255)
    elif pTeam.monsters[0].hp <= pTeam.monsters[0].stats[0]/2:
        color = Color(255, 255, 0, 255)
    else:
        color = Color(0, 255, 0, 255)
    screen.blit(pHP.image, pHP.pos)
    pygame.draw.rect(screen, color, (pHP.pos[0] + (16 * ENLARGE_FACTOR), pHP.pos[1] + ENLARGE_FACTOR, (pTeam.monsters[0].hp/pTeam.monsters[0].stats[0]) * (48 * ENLARGE_FACTOR), ENLARGE_FACTOR * 3))
    if oTeam.monsters[0].hp <= oTeam.monsters[0].stats[0]/5:
        color = Color(255, 0, 0, 255)
    elif oTeam.monsters[0].hp <= oTeam.monsters[0].stats[0]/2:
        color = Color(255, 255, 0, 255)
    else:
        color = Color(0, 255, 0, 255)
    screen.blit(oHP.image, oHP.pos)
    pygame.draw.rect(screen, color, (oHP.pos[0] + (16 * ENLARGE_FACTOR), oHP.pos[1] + ENLARGE_FACTOR, (oTeam.monsters[0].hp/oTeam.monsters[0].stats[0]) * (48 * ENLARGE_FACTOR), ENLARGE_FACTOR * 3))
    if pTeam.monsters[0].level > 0:
        pygame.draw.rect(screen, Color(0, 255, 255, 255), (pEXP.pos[0] + (8 * ENLARGE_FACTOR), pEXP.pos[1] + ENLARGE_FACTOR, ((pTeam.monsters[0].exp - calcBaseEXP(pTeam.monsters[0].level, 3))/(calcBaseEXP(pTeam.monsters[0].level + 1, 3) - calcBaseEXP(pTeam.monsters[0].level, 3))) * (64 * ENLARGE_FACTOR), ENLARGE_FACTOR * 2))

def doTurn(dbox): #checks if the battle should continue, and then initializes the turn
    global pTeam
    global oTeam
    if askForTurnInput(dbox) != "running":
        performAttacks(dbox)
        if oTeam.monsters[0].hp <= 0:
            displayFaint(0)
            layers.remove(oSprite)
            if wild:
                pygame.mixer.music.load("music/wildwin.ogg")
                pygame.mixer.music.play(-1)
            dbox.openBattle("The opposing " + oTeam.monsters[0].name + " fainted!", layers)
            expGain(pTeam.monsters[0], oTeam.monsters[0], dbox)
            if oTeam.monsters[1] == None or oTeam.monsters[1].name == "UNKNOWN":
                return "pwin"
            else:
                layers.add(oSprite)
        if oTeam.monsters[0].caught == True:
            added = False
            for i in range(pTeam.monsters.__len__()):
                if pTeam.monsters[i].dex == 0:
                    pTeam.monsters[i] = oTeam.monsters[0]
                    added = True
                    break
            if not added:
                dbox.openBattle(oTeam.monsters[0].name + " was sent to the PC.", layers)
                with open("PCList.txt", "a") as f:
                    f.write(str(oTeam.monsters[0].dex) + "\n")
                #else: add to PC list
            return "catch"
        if pTeam.monsters[0].hp <= 0:
            displayFaint(1)
            layers.remove(pSprite)
            dbox.openBattle(pTeam.monsters[0].name + " fainted!", layers)
            switched = False
            for i in range(1,6):
                if pTeam.monsters[i].hp > 0 and pTeam.monsters[i].name != "UNKNOWN":
                    battleSwitch(pTeam)
                    screen.fill((255, 255, 255))
                    pLvl.update("L:" + str(pTeam.monsters[0].level))
                    pHPratio.update(str(pTeam.monsters[0].hp) + "/ " + str(pTeam.monsters[0].stats[0]))
                    pSprite.image = pygame.image.load(pTeam.monsters[0].backImage)
                    pSprite.image = pygame.transform.scale(pSprite.image, (int(pSprite.image.get_width() * 2), int(pSprite.image.get_height() * 2)))
                    barBlit()
                    layers.draw(screen)
                    pygame.display.update()
                    switched = True
                    break
            if not switched:
                return "owin"
            else:
                layers.add(pSprite)
    else:
        return "running"
def askForTurnInput(dbox): #Displays the main 4-option selection screen for player move choice, and determines the next opponent move
    global pNextTurns
    global pNextItem
    if pNextTurns[0] == None:
        buttons[0] = Button((TILE_SIZE * 4.5, TILE_SIZE * 6.5), "FIGHT", "")
        buttons[1] = Button((TILE_SIZE * 4.5, TILE_SIZE * 7.5), "$%", "")
        buttons[2] = Button((TILE_SIZE * 6.5, TILE_SIZE * 6.5), "BAG", "")
        buttons[3] = Button((TILE_SIZE * 6.5, TILE_SIZE * 7.5), "RUN", "")
        dbox.openBattle("What will " + pTeam.monsters[0].name + " é do?", layers)
        while 1:
            ready = select.update()
            if ready == True:
                if select.selected == 0:
                    choice = chooseMove(dbox)
                    if choice == "back":
                        buttons[0] = Button((TILE_SIZE * 4.5, TILE_SIZE * 6.5), "FIGHT", "")
                        buttons[1] = Button((TILE_SIZE * 4.5, TILE_SIZE * 7.5), "$%", "")
                        buttons[2] = Button((TILE_SIZE * 6.5, TILE_SIZE * 6.5), "BAG", "")
                        buttons[3] = Button((TILE_SIZE * 6.5, TILE_SIZE * 7.5), "RUN", "")
                        ready = False
                    else:
                        pNextTurns[0] = choice
                        break
                elif select.selected == 1:
                    info = openBag()
                    if info == "back":
                        barBlit()
                        layers.draw(screen)
                        pygame.display.update()
                    else:
                        pNextTurns[0] = info[0]
                        pNextItem = info[1]
                        break
                elif select.selected == 2:
                    info = PkmnMenu.battleSwitch(pTeam)
                    if info == "back":
                        screen.fill((255, 255, 255))
                        barBlit()
                        layers.draw(screen)
                        pygame.display.update()
                    else:
                        pNextTurns[0] = "Switch"
                        screen.fill((255, 255, 255))
                        pLvl.update("L:" + str(pTeam.monsters[0].level))
                        pHPratio.update(str(pTeam.monsters[0].hp) + "/ " + str(pTeam.monsters[0].stats[0]))
                        pSprite.image = pygame.image.load(pTeam.monsters[0].backImage)
                        pSprite.image = pygame.transform.scale(pSprite.image, (int(pSprite.image.get_width() * 2), int(pSprite.image.get_height() * 2)))
                        barBlit()
                        layers.draw(screen)
                        pygame.display.update()
                        dbox.openBattle("You sent out " + info.name + "!", layers)
                        break
                elif select.selected == 3:
                    pNextTurns[0] = "Run"
                    global runAttempts
                    runAttempts += 1
                    f = (((pTeam.monsters[0].stats[5] * 128)/pTeam.monsters[0].stats[5]) + (30 * runAttempts)) % 256
                    if random.randint(0, 255) < f: #formula for whether player can run
                        dbox.openBattle("Got away safely!", layers)
                        return "running"
                    break
            screen.blit(select.image, (select.rect.x, select.rect.y))
            layers.draw(screen)
            for button in buttons:
                screen.blit(button.image, button.pos)
                screen.blit(button.label, (button.labelrect.x, button.labelrect.y))
                screen.blit(button.label2, (button.label2rect.x, button.label2rect.y))
            screen.blit(select.image, (select.rect.x, select.rect.y))
            pygame.display.update()
            timer.tick(30)
    if oNextTurns[0] == None:
        randNum = -1
        for move in oTeam.monsters[0].moves:
            if move != "-":
                randNum += 1
        oNextTurns[0] = oTeam.monsters[0].moves[random.randint(0, randNum)]
def chooseMove(dbox): #Displays the 4-move selection screen
    buttons[0] = Button((TILE_SIZE * 4.5, TILE_SIZE * 6.5), pTeam.monsters[0].moves[0], str(pTeam.monsters[0].pp[0]) + "/" + str(pTeam.monsters[0].ppMax[0]))
    buttons[1] = Button((TILE_SIZE * 4.5, TILE_SIZE * 7.5), pTeam.monsters[0].moves[2], str(pTeam.monsters[0].pp[2]) + "/" + str(pTeam.monsters[0].ppMax[2]))
    buttons[2] = Button((TILE_SIZE * 6.5, TILE_SIZE * 6.5), pTeam.monsters[0].moves[1], str(pTeam.monsters[0].pp[1]) + "/" + str(pTeam.monsters[0].ppMax[1]))
    buttons[3] = Button((TILE_SIZE * 6.5, TILE_SIZE * 7.5), pTeam.monsters[0].moves[3], str(pTeam.monsters[0].pp[3]) + "/" + str(pTeam.monsters[0].ppMax[3]))
    selection = None
    while 1:
        ready = select.update()
        if ready == True:
            selection = pTeam.monsters[0].moves[select.selected]
            index = pTeam.monsters[0].moves.index(selection)
            if selection != "-" and pTeam.monsters[0].pp[index] > 0:
                pTeam.monsters[0].pp[index] -= 1
                buttons[index].update2(str(pTeam.monsters[0].pp[3]) + "/" + str(pTeam.monsters[0].ppMax[3]))
                break
            else:
                dbox.openBattle("You can't do that!", layers)
        elif ready == "back":
            return "back"
        layers.draw(screen)
        for button in buttons:
            screen.blit(button.image, button.pos)
            screen.blit(button.label, (button.labelrect.x, button.labelrect.y))
            screen.blit(button.label2, (button.label2rect.x, button.label2rect.y))
        screen.blit(select.image, (select.rect.x, select.rect.y))
        pygame.display.update()
        timer.tick(30)
    return selection

def openBag():
    itemSelected = Bag.requestItem()
    if itemSelected == "back":
        return "back"
    for spr in layers:
        screen.blit(spr.image, spr.rect.topleft)
    layers.draw(screen)
    pygame.display.update()
    if itemSelected.pocket == "balls":
        return ("catch", itemSelected)
    elif itemSelected.pocket == "battle items":
        return ("item", itemSelected)
def performAttacks(dbox): #This function determines move order
    global pNextItem
    if(pTeam.monsters[0].stats[5] >= oTeam.monsters[0].stats[5]):
        attack(pTeam, oTeam, dbox, pNextTurns[0], pHP.pos, oHP.pos, pNextItem)
        pNextTurns[0] = pNextTurns[1]
        pNextTurns[1] = None
        if checkFaint():
            return
        attack(oTeam, pTeam, dbox, oNextTurns[0], oHP.pos, pHP.pos, None)
        oNextTurns[0] = oNextTurns[1]
        oNextTurns[1] = None
        if checkFaint():
            return
    else:
        attack(oTeam, pTeam, dbox, pNextTurns[0], oHP.pos, pHP.pos, None)
        oNextTurns[0] = oNextTurns[1]
        oNextTurns[1] = None
        if checkFaint():
            return
        attack(pTeam, oTeam, dbox, oNextTurns[0], pHP.pos, oHP.pos, pNextItem)
        pNextTurns[0] = pNextTurns[1]
        pNextTurns[1] = None
        if checkFaint():
            return
    pNextItem = None
def checkFaint(): #This function checks if one of the battling Pokemon has fainted
    if pTeam.monsters[0].hp <= 0:
        return True
    elif oTeam.monsters[0].hp <= 0:
        return True
    elif oTeam.monsters[0].caught == True:
        return True
    else:
        return False
def attack(aTeam, dTeam, dbox, move, aBarPos, dBarPos, item): #This function calls the corresponding move-function
    if move == "catch":
        catch(dTeam, item, dbox)
    elif move == "item":
        item(aTeam, dTeam, dbox, aBarPos, dBarPos, item)
    else:
        globals()[move.replace("-","").lower().capitalize()](aTeam, dTeam, dbox, aBarPos, dBarPos)
def basicDamage(a, d, power): #Calculator for most attack damage
    modifier = 1 #modifier is weather * crit * randfactor * STAB * typebonus * burneffect, just 1 for now
    damage = int(((((((2 * a.level) / 5) + 2) * power * float(a.stats[1] / d.stats[2])) / 50) + 2) * modifier)
    if d.hp < damage:
        return d.hp
    else:
        return damage
def changeStatStage(monster, stat, change): #use team.monsters[m].statStages[6/7] += n for accuracy/evasion
    monster.statStages[stat] += change
    if monster.statStages[stat] > 0:
        monster.stats[stat] = monster.normStats[stat] * ((monster.statStages[stat]+2)/2)
    elif monster.statStages[stat] < 0:
        monster.stats[stat] = int((monster.normStats[stat] * float(2 / ((-1 * monster.statStages[stat]) + 2))))
    else:
        monster.stats[stat] = monster.normStats[stat]
def miss(aMonster, dMonster, accuracy, dbox):
    otherMods = 1
    combined = aMonster.statStages[6] - dMonster.statStages[7]
    if combined > 0:
        factor = (combined+3)/3
    elif combined < 0:
        factor = float(3 / ((-1 * combined) + 3))
    else:
        factor = 1
    hitChance = int(accuracy * factor * otherMods);
    if(random.randint(1,100)) > hitChance:
        dbox.openBattle(aMonster.name + "'s move missed!", layers)
        return True
    return False

def expGain(gMonster, kMonster, dbox): #gainmonster, killedmonster
    trainerBonus = 1
    if not wild:
        trainerBonus = 1.5
    with open("pkmnBaseEXPGain.txt") as f:
        data = f.readlines()
        baseEXP = int(data[kMonster.dex])
    exp = int((trainerBonus * baseEXP * kMonster.level) / 7) #should factor in EXP Share when it becomes relevant
    dbox.openBattle(gMonster.name + " earned " + str(exp) + " experience points!", layers)
    print(str(gMonster.exp) + " + " + str(exp) + " / " + str(calcBaseEXP(gMonster.level + 1, 3)))
    while 1:
        nextLvlEXP = calcBaseEXP(gMonster.level + 1, 3)
        currLvlEXP = calcBaseEXP(gMonster.level, 3)
        if exp >= nextLvlEXP - gMonster.exp:
            addThisLevel = nextLvlEXP - gMonster.exp
            statChanges = gMonster.addEXP(addThisLevel)
            changeEXP(pEXP.pos, nextLvlEXP - currLvlEXP, gMonster.exp - (currLvlEXP + addThisLevel), addThisLevel)
            pygame.mixer.music.pause()

            Overworld.play_sound("sounds/levelup.wav")
            dbox.openBattle(gMonster.name + " leveled up!", layers)
            pygame.mixer.music.unpause()
            pygame.draw.rect(screen, Color(255,255,255,255), pLvl.rect)
            pLvl.update("L: " + str(gMonster.level))
            pygame.draw.rect(screen, Color(255,255,255,255), pHPratio.rect)
            pHPratio.update(str(gMonster.hp) + "/ " + str(gMonster.stats[0]))
            if gMonster.hp <= gMonster.stats[0]/5:
                color = Color(255, 0, 0, 255)
            elif gMonster.hp <= gMonster.stats[0]/2:
                color = Color(255, 255, 0, 255)
            else:
                color = Color(0, 255, 0, 255)
            screen.blit(pHP.image, pHP.pos)
            pygame.draw.rect(screen, color, (pHP.pos[0] + (16 * ENLARGE_FACTOR), pHP.pos[1] + ENLARGE_FACTOR, (gMonster.hp/pTeam.monsters[0].stats[0]) * (48 * ENLARGE_FACTOR), ENLARGE_FACTOR * 3))
            displayChanges(statChanges, gMonster)
            layers.draw(screen)
            exp -= addThisLevel
            learnMoves(gMonster, dbox)
        else:
            print(str(gMonster.exp))
            gMonster.addEXP(exp)
            print(str(gMonster.exp))
            changeEXP(pEXP.pos, nextLvlEXP - currLvlEXP, gMonster.exp - (currLvlEXP + exp), exp)
            break

def changeHP(barPos, maxHP, startHP, dif): #This function displays the animation for hp loss/gain
    for i in range(int(dif*100/maxHP)):
        difPer = (maxHP*i/100)
        if startHP - difPer <= maxHP/5:
            color = Color(255, 0, 0, 255)
        elif startHP - difPer <= maxHP/2:
            color = Color(255, 255, 0, 255)
        else:
            color = Color(0, 255, 0, 255)
        pygame.draw.rect(screen, Color(255, 255, 255, 255), (barPos[0] + (16 * ENLARGE_FACTOR), barPos[1] + ENLARGE_FACTOR, TILE_SIZE * 3, ENLARGE_FACTOR * 3))
        pygame.draw.rect(screen, color, (barPos[0] + (16 * ENLARGE_FACTOR), barPos[1] + ENLARGE_FACTOR, ((startHP - difPer)/maxHP) * (48 * ENLARGE_FACTOR), ENLARGE_FACTOR * 3))
        if barPos == pHP.pos:
            pygame.draw.rect(screen, Color(255, 255, 255, 255), pHPratio.rect)
            pHPratio.update(str(int(startHP - difPer)) + "/ " + str(maxHP))
            screen.blit(pHPratio.image, pHPratio.pos)
        pygame.display.flip()
        timer.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

def changeEXP(barPos, maxEXP, startEXP, dif): #This function displays the animation for exp loss/gain
    Overworld.play_sound("sounds/xpgain.wav")
    for i in range(dif * 2 + 2): #maybe shouldnt have a +2 there, but ok
        if(startEXP + (i/2) <= maxEXP):
            pygame.draw.rect(screen, Color(255, 255, 255, 255), (barPos[0] + (8 * ENLARGE_FACTOR), barPos[1] + ENLARGE_FACTOR, TILE_SIZE * 4, ENLARGE_FACTOR * 2))
            pygame.draw.rect(screen, Color(0, 255, 255, 255), (barPos[0] + (8 * ENLARGE_FACTOR), barPos[1] + ENLARGE_FACTOR, ((startEXP + (i/2))/maxEXP) * (64 * ENLARGE_FACTOR), ENLARGE_FACTOR * 2))
            pygame.display.update()
            timer.tick(60)
        else:
            Overworld.stop_sound("sounds/xpgain.wav")
            Overworld.play_sound("sounds/levelupding.wav")
            pygame.draw.rect(screen, Color(255, 255, 255, 255), (barPos[0] + (8 * ENLARGE_FACTOR), barPos[1] + ENLARGE_FACTOR, TILE_SIZE * 4, ENLARGE_FACTOR * 2))
            pygame.display.update()
            break
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
    Overworld.stop_sound("sounds/xpgain.wav")

def displayChanges(statChanges, monster):
    stuff = pygame.sprite.Group()
    box = pygame.sprite.Sprite()
    box.image = pygame.image.load("statDisplay.png")
    box.image = pygame.transform.scale(box.image, (TILE_SIZE*3,TILE_SIZE*4))
    box.rect = box.image.get_rect(topleft = (TILE_SIZE * 6, TILE_SIZE * 5))
    stuff.add(box)
    statStrings = ["HP", "ATT", "DEF", "SP.ATT", "SP.DEF", "SPD"]
    texts = []
    for i in range(6):
        text = TextImage((int(TILE_SIZE*6.125), int(TILE_SIZE*5.5+float(TILE_SIZE*i*0.5))), (statStrings[i]+": +" + str(statChanges[i])), stuff)
        text.resizeText(12)
        texts.append(text)
        stuff.add(text)
    
    clicked = False
    while 1:
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                return
            if e.type == KEYDOWN and e.key == K_x:
                Overworld.play_sound("sounds/selection.wav")
                clicked = True
        if clicked:
            break
        stuff.draw(screen)
        pygame.display.update()
        timer.tick(30)
    for i in range(6):
        texts[i].update(statStrings[i]+": " + str(monster.stats[i]))
    while 1:
        for e in pygame.event.get():
            if e.type == QUIT:
                pygame.quit()
                sys.exit()
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                return
            if e.type == KEYDOWN and e.key == K_x:
                Overworld.play_sound("sounds/selection.wav")
                return
        stuff.draw(screen)
        pygame.display.update()
        timer.tick(30)

def displayFaint(monster):
    global oSprite
    global pSprite
    Overworld.play_sound("sounds/faint.wav")
    if monster == 0:
        orect = pygame.Rect(oSprite.rect)
        new_surface = pygame.Surface((orect.width, orect.height))
        for i in range(10):
            new_surface.fill(Color(255,255,255))
            new_surface.blit(oSprite.image, (0,i*12))
            screen.blit(new_surface, orect)
            pygame.display.update(orect)
            timer.tick(30)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
    else:
        prect = pygame.Rect(pSprite.rect)
        new_surface = pygame.Surface((prect.width, prect.height))
        for i in range(10):
            new_surface.fill(Color(255,255,255))
            new_surface.blit(pSprite.image, (0,i*12))
            screen.blit(new_surface, prect)
            pygame.display.update(prect)
            timer.tick(30)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
    
def learnMoves(monster, dbox):
    with open("pkmnBasicInfo.txt", "r") as f:
        info = list(f)[monster.dex].split()
        allMoves = info[8:]
        for i in range(int(allMoves.__len__()/2)):
            if allMoves[(2 * i) + 1] != "None":
                if int(allMoves[(2 * i) + 1]) == monster.level:
                    hasASpace = False
                    j = 0
                    for move in monster.moves:
                        if move == "-":
                            hasASpace = True
                            monster.moves[j] = allMoves[2*i].capitalize()
                            dbox.openBattle(monster.name + " learned " + allMoves[2*i].capitalize() + "!", layers)
                            break
                        j += 1
                    if not hasASpace:
                        dbox.openBattle(monster.name + " wants to learn the move " + move + ". Would you like to swap out a move with " + move + "?", layers)
                        yes = yesNo()

# MOVE METHODS (Keep in alphabetical order for ease of search)
def Run(aTeam, dTeam, dbox, aBarPos, dBarPos): #placeholder method for when run attempt fails
    dbox.openBattle("Can't escape!", layers)
def catch(dTeam, ball, dbox):
    if wild == False:
        dbox.openBattle("You can't catch another Trainer's Pokemon!", layers)
        return
    dbox.openBattle("You threw a " + ball.name + "!", layers)
    bonusball = float(ball.infoString.split()[1])
    bonusstatus = 1
    sc = dTeam.monsters[0].statusCondition
    if sc == "sleep" or sc == "freeze":
        bonusstatus = 2
    elif sc == "poison" or sc == "burn" or sc == "paralyze":
        bonusstatus = 1.5
    a = ((((3 * dTeam.monsters[0].stats[0]) - (2 * dTeam.monsters[0].hp)) * dTeam.monsters[0].catchRate * bonusball) / (3 * dTeam.monsters[0].stats[0])) * bonusstatus
    if random.randint(1,255) < a:
        dbox.openBattle("Gotcha! The wild " + dTeam.monsters[0].name + " was caught!", layers)
        dTeam.monsters[0].caught = True
    else:
        dbox.openBattle("Oh no! The wild " + dTeam.monsters[0].name + " broke free!", layers)
def item(aTeam, dTeam, dbox, aBarPos, dBarPos):
    print("eat")
def Switch(aTeam, dTeam, dbox, aBarPos, dBarPos):
    #do nothing
    None
def Growl(aTeam, dTeam, dbox, aBarPos, dBarPos):
    dbox.openBattle(aTeam.monsters[0].name + " used Growl!", layers)
    if not miss(aTeam.monsters[0], dTeam.monsters[0], 100, dbox):
        changeStatStage(dTeam.monsters[0], 1, -1)
        dbox.openBattle(dTeam.monsters[0].name + "'s ATTACK stat was lowered!", layers)
def Poisonsting(aTeam, dTeam, dbox, aBarPos, dBarPos):
    dbox.openBattle(aTeam.monsters[0].name + " used Poison Sting!", layers)
    if not miss(aTeam.monsters[0], dTeam.monsters[0], 100, dbox):
        damage = basicDamage(aTeam.monsters[0], dTeam.monsters[0], 15)
        prevHP = dTeam.monsters[0].hp
        dTeam.monsters[0].hp -= damage
        changeHP(dBarPos, dTeam.monsters[0].stats[0], prevHP, damage)
        dbox.openBattle(dTeam.monsters[0].name + " took " + str(damage) + " damage!", layers)
        if random.randint(0,10) < 3:
            dTeam.monsters[0].statusCondition = "poison"
            dbox.openBattle(dTeam.monsters[0].name + " was poisoned!", layers)
def Sandattack(aTeam, dTeam, dbox, aBarPos, dBarPos):
    dbox.openBattle(aTeam.monsters[0].name + " used Sand Attack!", layers)
    if not miss(aTeam.monsters[0], dTeam.monsters[0], 100, dbox):
        dTeam.monsters[0].statStages[6] -= 1
        dbox.openBattle(dTeam.monsters[0].name + "'s accuracy was lowered!", layers)
def Scratch(aTeam, dTeam, dbox, aBarPos, dBarPos):
    dbox.openBattle(aTeam.monsters[0].name + " used Scratch!", layers)
    if not miss(aTeam.monsters[0], dTeam.monsters[0], 100, dbox):
        damage = basicDamage(aTeam.monsters[0], dTeam.monsters[0], 40)
        prevHP = dTeam.monsters[0].hp
        dTeam.monsters[0].hp -= damage
        changeHP(dBarPos, dTeam.monsters[0].stats[0], prevHP, damage)
        dbox.openBattle(dTeam.monsters[0].name + " took " + str(damage) + " damage!", layers)
def Stringshot(aTeam, dTeam, dbox, aBarPos, dBarPos):
    dbox.openBattle(aTeam.monsters[0].name + " used String Shot!", layers)
    if not miss(aTeam.monsters[0], dTeam.monsters[0], 95, dbox):
        changeStatStage(dTeam.monsters[0], 5, -1)
        dbox.openBattle(dTeam.monsters[0].name + "'s SPEED stat was lowered!", layers)
def Tackle(aTeam, dTeam, dbox, aBarPos, dBarPos):
    dbox.openBattle(aTeam.monsters[0].name + " used Tackle!", layers)
    if not miss(aTeam.monsters[0], dTeam.monsters[0], 100, dbox):
        damage = basicDamage(aTeam.monsters[0], dTeam.monsters[0], 40)
        prevHP = dTeam.monsters[0].hp
        dTeam.monsters[0].hp -= damage
        changeHP(dBarPos, dTeam.monsters[0].stats[0], prevHP, damage)
        dbox.openBattle(dTeam.monsters[0].name + " took " + str(damage) + " damage!", layers)
def Tailwhip(aTeam, dTeam, dbox, aBarPos, dBarPos):
    dbox.openBattle(aTeam.monsters[0].name + " used Tail Whip!", layers)
    if not miss(aTeam.monsters[0], dTeam.monsters[0], 100, dbox):
        changeStatStage(dTeam.monsters[0], 2, -1)
        dbox.openBattle(dTeam.monsters[0].name + "'s DEFENSE stat was lowered!", layers)