import pygame
import threading
import Overworld, TeamInfo
from TeamInfo import Team, Monster
name = "06"
default_position = (20,20)
continue_music = "f"
pTeam = Team()
pTeam.playerTeam()
pygame.mixer.pre_init(22050,-16,2,512)
pygame.init()
while 1:
    name, default_position, continue_music = Overworld.main(name, default_position, continue_music, pTeam)