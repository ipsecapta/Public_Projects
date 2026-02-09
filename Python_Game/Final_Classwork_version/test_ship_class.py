#!/usr/bin/env python3
#
# Project: Final Project
# Files needed by this file: 
#       Visintainer_A_AlienGame.py (this file)
#       base_settings.py
#       menu_helpers.py
#       ship.py
#       alien.py
#       bullet.py
#
# Author: Anthony Visintainer
# Date: 8 December 2025

# test_ship.py
import pygame
import pytest

from base_settings import Settings
from ship import Ship


def test_ship_p1_starting_position(): #a tiny pytest function to make sure the starting position of player 1's ship is correct.
    pygame.init()
    
    settings = Settings() #create a settings object to hand off dimensions to our screen and info to our test ship
    screen = pygame.display.set_mode((settings.screen_width, settings.screen_height)) #Create a test screen. No need to make it resizable, like in the actual game.

    ship = Ship(settings, screen, player_id=1) #create a test ship on the screen; set its player id to 1

    assert ship.keys == settings.player1_keys # are the right keys called from the settings file?
    #are the right coordinates given to the ship?
    assert ship.rect.centerx == pytest.approx(settings.screen_width * 0.65) #use  coordinate equation set in lines 61-70 of ship.py
    assert ship.rect.bottom == pytest.approx(settings.screen_height * 0.9)

    pygame.quit()

#result of running pytest should be one green dot; the result of running the file should say "1 passed"
