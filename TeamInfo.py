import pypokedex
import random
class Team:
    def __init__(self):
        self.monsters = [Monster(), Monster(), Monster(), Monster(), Monster(), Monster()]
    def playerTeam(self):
        txt = open("playerTeam.txt", "r").readlines()
        i = 0
        for line in txt:
            words = line.split()
            self.monsters[i].dex = int(words[0])
            self.monsters[i].moves.append(words[1])
            self.monsters[i].moves.append(words[2])
            self.monsters[i].moves.append(words[3])
            self.monsters[i].moves.append(words[4])
            self.monsters[i].level = int(words[5])
            self.monsters[i].exp = int(words[6])
            self.monsters[i].ownMonster()
            i += 1
    def wildTeam(self, mapname):
        with open("encounterLists/eList" + mapname + ".txt", "r") as f:
            data = f.readlines()
        chances = []
        total = 0
        for line in data:
            chance = int(line.split()[0])
            total += chance
            chances.append(chance)
        rand = random.randint(1, total)
        i = 0
        for ch in chances:
            rand -= ch
            if rand <= 0:
                pkmnData = data[i].split()
                monsterNum = int(pkmnData[1])
                break
            i += 1
        self.monsters[0].wildMonster(monsterNum, pkmnData[2], pkmnData[3])

class Monster:
    def __init__(self):
        self.dex = 0
        self.species = "UNKNOWN"
        self.name = "UNKNOWN"
        self.level = 1
        self.frontImage = ("pokemon_sprites/Missingno.png")
        self.backImage = ("pokemon_sprites/Missingno.png")
        self.moves = []
        self.ppMax = []
        self.pp = []
        self.baseStats = [] #[maxhp, atk, def, sp_atk, sp_def, spd]
        self.stats = [1, 1, 1, 1, 1, 1] #[maxhp, atk, def, sp_atk, sp_def, spd, accuracy, evasion]
        self.normStats = self.stats.copy()
        self.statStages = [0,0,0,0,0,0,0,0] #index 0 is never used, but included to reduce confusion
        self.hp = self.stats[0]
        self.exp = 0
        self.IVs = []
        for i in range(6):
            self.IVs.append(random.randint(0,31))
        self.EVs = [0, 0, 0, 0, 0, 0]
        self.statusCondition = "None"
        self.caught = False
    def wildMonster(self, number, minlvl, maxlvl):
        with open("pkmnBasicInfo.txt", "r") as f:
            info = list(f)[number].split()
        self.dex = number
        self.species = info[0]
        self.name = self.species
        self.frontImage = ("pokemon_sprites/" + self.species + "F.png")
        self.backImage = ("pokemon_sprites/" + self.species + "B.png")
        self.moves = ["-", "-", "-", "-"]
        self.baseStats = [int(info[1]),int(info[2]),int(info[3]),int(info[4]),int(info[5]),int(info[6])]
        self.calculateStats()
        self.catchRate = int(info[7])
        self.hp = self.stats[0]
        self.avaiMoves = [] #Replace 'moves' with this after move methods are created
        allMoves = info[8:]
        for i in range(int(allMoves.__len__()/2)):
            if allMoves[(2 * i) + 1] != "None":
                if int(allMoves[(2 * i) + 1]) <= self.level:
                    self.avaiMoves.append([allMoves[2 * i], allMoves[(2 * i) + 1]])
        self.avaiMoves.sort(key=takeLevel, reverse = True)
        i = 0
        for move in self.avaiMoves:
            self.moves[i] = self.avaiMoves[i][0].replace("-", "").capitalize()
            i += 1
        with open("movePP.txt", "r") as g:
            data = g.readlines()
        for i in range(4):
            for line in data:
                if line.split()[0] == self.moves[i]:
                    self.ppMax.append(int(line.split()[1]))
        for i in range(4 - self.ppMax.__len__()):
            self.ppMax.append(0)
        self.pp = self.ppMax.copy()
        self.level = random.randint(int(minlvl), int(maxlvl))
        self.exp = calcBaseEXP(self.level, 3) #3 for now, change to allow more increase types later
    def ownMonster(self):
        if self.dex != 0:
            with open("pkmnBasicInfo.txt", "r") as f:
                info = list(f)[self.dex].split()
            self.species = info[0]
            self.name = self.species #just for now
            self.frontImage = ("pokemon_sprites/" + self.species + "F.png")
            self.backImage = ("pokemon_sprites/" + self.species + "B.png")
            self.baseStats = [int(info[1]),int(info[2]),int(info[3]),int(info[4]),int(info[5]),int(info[6])]
            self.calculateStats()
            self.hp = self.stats[0]
            self.caught = True
            with open("movePP.txt", "r") as g:
                data = g.readlines()
            for i in range(4):
                for line in data:
                    if line.split()[0] == self.moves[i]:
                        self.ppMax.append(int(line.split()[1]))
            for i in range(4 - self.ppMax.__len__()):
                self.ppMax.append(0)
            self.pp = self.ppMax.copy() #this should be replaced with a save-file based pp amount
    def calculateStats(self):
        self.stats[0] = int(((2*self.baseStats[0] + self.IVs[0] + int(self.EVs[0]/4)) * self.level) / 100) + self.level + 10
        self.stats[1] = int((int(((2*self.baseStats[1] + self.IVs[1] + int(self.EVs[1]/4)) * self.level) / 100) + 5) * 1)
        self.stats[2] = int((int(((2*self.baseStats[2] + self.IVs[2] + int(self.EVs[2]/4)) * self.level) / 100) + 5) * 1)
        self.stats[3] = int((int(((2*self.baseStats[3] + self.IVs[3] + int(self.EVs[3]/4)) * self.level) / 100) + 5) * 1)
        self.stats[4] = int((int(((2*self.baseStats[4] + self.IVs[4] + int(self.EVs[4]/4)) * self.level) / 100) + 5) * 1)
        self.stats[5] = int((int(((2*self.baseStats[5] + self.IVs[5] + int(self.EVs[5]/4)) * self.level) / 100) + 5) * 1)
        self.normStats = self.stats.copy()
    def levelUp(self): #Increases the monster's level, and returns an array containing the changes made to the monster's stats (ints)
        self.level += 1
        prevStats = self.stats.copy()
        self.calculateStats()
        statChanges = []
        i = 0
        for stat in self.stats:
            statChanges.append(self.stats[i] - prevStats[i])
            i += 1
        self.hp += statChanges[0]
        return statChanges
    def addEXP(self, points):
        self.exp += points
        if self.exp >= calcBaseEXP(self.level + 1, 3): #3 for now, change to allow more increase types later
            return self.levelUp()

def takeLevel(elem):
    return elem[1]
def calcBaseEXP(level, incType): #incType- erratic, fast, medium-fast, medium-slow, slow, fluctuating
    if incType == 3: #MEDIUM-SLOW
        with open("anomalousEXP.txt") as f:
            data = f.readlines()
            return int(data[level].split()[0])
def getSpecies(dex):
    with open("pkmnBasicInfo.txt", "r") as f:
        return list(f)[int(dex)].split()[0]

