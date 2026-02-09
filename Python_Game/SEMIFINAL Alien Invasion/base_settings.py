#!/usr/bin/env python3
#
# Project: Final Project
#
# Files needed by this file: 
#       base_settings.py (this file)
#       all images whose paths in the /img directory are referenced (e.g. see lines 23-30 below)
#
# Author: Anthony Visintainer
# Date: 8 December 2025



#This contains all the basic game config settings.
import pygame
import sys

class Settings:
    def __init__(self):
        # Screen width, height, and path to background image of space - loading and scaling of images happens below, in load_images()
        self.screen_width = 1200
        self.screen_height = 620
        self.starter_bg_path = "img/background.png"
        self._3to4_bg_path = 'img/background_3-4.png'
        self._5to6_bg_path = 'img/background_5-6.png'
        self._7to8_bg_path = 'img/background_7-8.png'
        self._9to10_bg_path = 'img/background_9-10.png'
        self.startscreen_path = "img/starterscreen.png"
        self.defeat_screen = "img/glassed_earth.png"
        self.victory_screen = "img/victory.png"
        self.multiplayer_resizer = 1
        
#********* PLAYER SHIP SETTINGS
        self.base_ship_speed = 3
        self.player_starting_lives= 3
        self.player_starting_health= 11
        self.player_respawn_time_ms= 10000
        
        #Movement Keys:
        self.player1_keys = { #set movement keys for player 1 - IF YOU CHANGE THESE, MAKE SURE TO CHANGE self.p1keydesc, BELOW, AS WELL.
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "fire": pygame.K_RCTRL,
            "shockwave": pygame.K_BACKSPACE,  # or separate
            "emp": pygame.K_BACKSLASH,
            "squadron": pygame.K_RETURN,
            "nanite": pygame.K_RSHIFT,
            "mac" : pygame.K_DELETE
        }

        self.player2_keys = { # set movement keys for player 2 - IF YOU CHANGE THESE, MAKE SURE TO CHANGE self.p2keydesc, BELOW, AS WELL
            "left": pygame.K_a,
            "right": pygame.K_d,
            "up": pygame.K_w,
            "down": pygame.K_s,
            "fire": pygame.K_q,
            "shockwave": pygame.K_BACKQUOTE,
            "emp": pygame.K_TAB,
            "squadron": pygame.K_CAPSLOCK,
            "nanite": pygame.K_LSHIFT,
            "mac" : pygame.K_LCTRL
                          }
        
        self.player3_keys = { # set movement keys for player 3 - IF YOU CHANGE THESE, MAKE SURE TO CHANGE self.p3keydesc, BELOW, AS WELL
            "left": pygame.K_KP1,
            "right": pygame.K_KP3,
            "up": pygame.K_KP5,
            "down": pygame.K_KP2,
            "fire": pygame.K_KP0,
            "shockwave": pygame.K_KP7,
            "emp": pygame.K_KP8,
            "squadron": pygame.K_KP9,
            "nanite": pygame.K_KP_PLUS,
            "mac" : pygame.K_KP_MINUS
                          }
        
        self.player4_keys = { # set movement keys for player 2 - IF YOU CHANGE THESE, MAKE SURE TO CHANGE self.p4keydesc, BELOW, AS WELL
            "left": pygame.K_j,
            "right": pygame.K_l,
            "up": pygame.K_i,
            "down": pygame.K_k,
            "fire": pygame.K_SPACE,
            "shockwave": pygame.K_7,
            "emp": pygame.K_y,
            "squadron": pygame.K_h,
            "nanite": pygame.K_b,
            "mac" : pygame.K_v
                          }

        #Movement key descriptions:
        self.p1keydesc= ("the ARROW KEYS, plus the RIGHT CTRL button to fire.")
        self.p2keydesc= ("w=UP, s=DOWN, a=LEFT, d=RIGHT, q=FIRE.")
        self.p3keydesc = ("numpad5=UP, numpad2=DOWN, numpad1=LEFT, numpad3=RIGHT, numpad0=FIRE.")
        self.p4keydesc = ("i=UP, k=DOWN, j=LEFT l=RIGHT, spacebar=FIRE.")

        # Bullet settings for human and normal aliens
        self.bullet_speed = 6
        self.bullet_width = 4
        self.bullet_height = 16

        #bullet_max and ship speed settings for leveled up human players:
        self.levelup_speed_increase = .05 # how much faster should a player go each level they increase?
        self.lvl1_bullet_max = 3
        self.lvl1_speed = self.base_ship_speed
        self.lvl2_bullet_max = 4
        self.lvl2_speed = self.lvl1_speed + self.levelup_speed_increase
        self.lvl3_bullet_max = 5
        self.lvl3_speed = self.lvl2_speed + self.levelup_speed_increase
        self.lvl4_bullet_max = 6
        self.lvl4_speed = self.lvl3_speed + self.levelup_speed_increase
        self.lvl5_bullet_max = 7
        self.lvl5_speed = self.lvl4_speed + self.levelup_speed_increase
        self.lvl6_bullet_max = 8
        self.lvl6_speed = self.lvl5_speed + self.levelup_speed_increase
        self.lvl7_bullet_max = 9
        self.lvl7_speed = self.lvl6_speed + self.levelup_speed_increase
        self.lvl8_bullet_max = 10
        self.lvl8_speed = self.lvl7_speed + self.levelup_speed_increase
        self.lvl9_bullet_max = 11
        self.lvl9_speed = self.lvl8_speed + self.levelup_speed_increase
        self.lvl10_bullet_max = 12
        self.lvl10_speed = self.lvl9_speed + self.levelup_speed_increase
        self.lvl11_bullet_max = 24
        self.lvl11_bullet_speed = 8 #bullets speed increase at level 11
        self.lvl11_bullet_color = (225, 255, 255) #special bullet color at level 11
        self.lvl11_speed = self.lvl10_speed + 0.085 #extra bump at level 11

        self.lvl2_xp_requirement = range(3000,5999) #+3000
        self.lvl3_xp_requirement = range(6000,9999) #+4000
        self.lvl4_xp_requirement = range(10000,14999) #+5000
        self.lvl5_xp_requirement = range(15000,20999) #+6000
        self.lvl6_xp_requirement = range(21000,27999) #+7000
        self.lvl7_xp_requirement = range(28000,35999) #+8000
        self.lvl8_xp_requirement = range(36000,44999) #+9000
        self.lvl9_xp_requirement = range(45000,54999) #+10000
        self.lvl10_xp_requirement = range(55000,99999) #->to 100,000
        self.lvl11_xp_requirement = 100000

       # experiment for later - using a for loop to create a dictionary holding info for levelups and bullets
       # #for number in range (1,11):
            #lvl_to_bullet_dict.append(number:number+2)

#**********ALIEN SETTINGS
        #bullet settings for alien sprites (width and length are included above), including different classes.-->
        #different speeds are taken care of in bullet.py with simple arithmetic.
        self.alien_bullet_speed = 3
        self.alien_bullet_width = round(3*self.multiplayer_resizer)
        self.alien_bullet_height = round(12*self.multiplayer_resizer)

        self.destroyer_bullet_width = round(4*self.multiplayer_resizer)
        self.destroyer_bullet_height = round(14*self.multiplayer_resizer)
        self.destroyer_bullet_max = 3

        self.cruiser_bullet_width = round(5*self.multiplayer_resizer)
        self.cruiser_bullet_height = round(14*self.multiplayer_resizer)
        self.cruiser_bullet_max = 1

        self.laztanker_bullet_width = 1 #doesn't get any smaller than one pixel...
        self.laztanker_bullet_height = round(28*self.multiplayer_resizer)
        self.laztanker_bullet_max = 12

        self.alien1_bullet_max = 1
        self.alien2_bullet_max = 2
        self.alien3_bullet_max = 2
        self.alien4_bullet_max = 0
        

        #bullet setting for boss alien
        self.boss_bullet_width = round(12*self.multiplayer_resizer)
        self.boss_bullet_height = round(16*self.multiplayer_resizer)
        self.boss_bullet_max = 7 #note these bullets will be larger.

        #Bullet styles - I have chosen to have human bullets look different from aliens' - and eventually, a third type, a boss aliens.
        self.player_bullet_color = (255, 255, 100) #A bright yellow laser bolt from human ships
        self.alien_bullet_color = (220, 255, 220) #A pale green laser from alien ships
        self.destroyerandcruiser_bullet_color = (255, 220, 255) #a light magenta bullet fired from destroyers and cruisers
        self.laztanker_bullet_color = (255, 0, 0) #a pure red laser from laser tankers
        self.bombarder_bullet_color = (240, 255, 240) #a whitish greenish plasma bomb fired by bombarders
        self.boss_bullet_color = (255, 255, 255) #Pure white for the bullets fired by boss aliens.

        # Alien ship speed settings (base)
        self.alien1_strafe_speed = 0.5 #for level 1 alien advance speed, see self.fleet_advance_speed below.
        self.alien2_speed = 0.22
        self.alien3_speed = 2.4
        self.alien4_speed = 1.75
        self.destroyer_speed = 0.3
        self.cruiser_speed = 0.25
        self.laztanker_speed = 0.20
        self.bombarder_strafe_speed = 0.25 #bombarders never advance, only strafe in the back row like artillery.
        self.boss_speed = 3

        #alien fleet direction, placement & speed settings (level 1 aliens spawn in fleets)
        self.fleet_direction = 1
        self.fleet_advance_speed = .02
        self.fleet_spacing_x = 25
        self.fleet_margin_x = 40 

        #Alien ship firing interval settings:
        self.alien1_min_fire_interval = 40000
        self.alien1_max_fire_interval = 60000
        self.alien2_min_fire_interval = 6000
        self.alien2_max_fire_interval = 12000
        self.alien3_min_fire_interval = 3000
        self.alien3_max_fire_interval = 6000
        self.destroyer_min_fire_interval = 150
        self.destroyer_max_fire_interval = 160
        self.cruiser_min_fire_interval = 200
        self.cruiser_max_fire_interval = 500
        self.laztanker_min_fire_interval = 120
        self.laztanker_max_fire_interval = 121


        #Alien ship spawning interval settings:
        self.alien2_min_spawn_interval = 5000
        self.alien2_max_spawn_interval = 10000
        self.alien3_min_spawn_interval = 10000
        self.alien3_max_spawn_interval = 14000
        self.alien4_min_spawn_interval = 18000
        self.alien4_max_spawn_interval = 18001
        self.destroyer_min_spawn_interval = 20000
        self.destroyer_max_spawn_interval = 34000
        self.cruiser_min_spawn_interval = 40000
        self.cruiser_max_spawn_interval = 64000
        self.laztanker_min_spawn_interval = 80000
        self.laztanker_max_spawn_interval = 94000
        self.bombarder_max_spawn_interval = 120000
        self.bombarder_max_spawn_interval = 120001
        # delay the first spawning of higher level aliens
        self.alien2_spawn_delay = 3000
        self.alien3_spawn_delay = 5000
        self.alien4_spawn_delay = 7000
        self.destroyer_spawn_delay = 15000


        #alien wave definitions: how many of each spawn per wave
        # Each entry: how many rows of level 1, and total level 2 & 3 aliens for that wave- THIS IS DEFUNCT: I changed to constant spawn for individual aliens as long as there are fleet aliens on screen.
        #this still works though, since the program now just checks for >0; so I leave it. 
        self.wave_master_index = [
            {"rows_level1": 5,  "count_level2": 0,  "count_level3": 0, "count_level4":0, "count_destroyers":0, "count_cruisers": 0, "count_lazortankers": 0, "count_bombarders": 0}, #e.g. wave one will have 5 rows of lvl 1, and 0 lvl 2 or 3 aliens.
            {"rows_level1": 6,  "count_level2": 2,  "count_level3": 0, "count_level4":0,"count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_bombarders": 0},
            {"rows_level1": 7,  "count_level2": 4,  "count_level3": 1, "count_level4":0, "count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_bombarders": 0},
            {"rows_level1": 8,  "count_level2": 8,  "count_level3": 3, "count_level4":1, "count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_bombarders": 0},
            {"rows_level1": 9,  "count_level2": 12, "count_level3": 6, "count_level4":3, "count_destroyers":2, "count_cruisers": 0, "count_laz0rtankers": 0, "count_bombarders": 0},
            {"rows_level1": 10, "count_level2": 18, "count_level3": 9, "count_level4":4, "count_destroyers":1, "count_cruisers": 0, "count_laz0rtankers": 0, "count_bombarders": 0},
            {"rows_level1": 11, "count_level2": 22, "count_level3": 12, "count_level4":5, "count_destroyers":2, "count_cruisers": 1, "count_laz0rtankers": 0, "count_bombarders": 0},
            {"rows_level1": 12, "count_level2": 28, "count_level3": 15, "count_level4":6, "count_destroyers":3, "count_cruisers": 2, "count_laz0rtankers": 1, "count_bombarders": 0},
            {"rows_level1": 13, "count_level2": 38, "count_level3": 21, "count_level4":7, "count_destroyers":3, "count_cruisers": 3, "count_laz0rtankers": 2, "count_bombarders": 1},
            {"rows_level1": 15, "count_level2": 50, "count_level3": 30, "count_level4":11, "count_destroyers":5, "count_cruisers": 4, "count_laz0rtankers": 3, "count_bombarders": 2, "final_boss": 1}
        ]
        self.level1_alien_starting_rows = 4 #every wave will start with this many rows of lvl 1 aliens on screen.

        self.new_wave_pause = 5000
        #Alien Damage Graphics:

        """self.alien2_hitframes = ["path here"]
        self.alien2_hp = 1
        
        self.alien3_hitframes = ["path here", "path here"]
        self.alien3_hp = len(self.alien3_hitframes)

        self.alien4_hitframes = ["path here", "path here", "path here"]
        self.alien4_hp = len(self.alien4_hitframes)"""

        self.destroyer_hitframes = ["img/destroyer_dmg1.png", "img/destroyer_dmg1.png", "img/destroyer_dmg1.png",
                                    "img/destroyer_dmg2.png", "img/destroyer_dmg2.png", "img/destroyer_dmg2.png",
                                    "img/destroyer_dmg3.png", "img/destroyer_dmg3.png", "img/destroyer_dmg3.png",
                                    "img/destroyer_dmg4.png","img/destroyer_dmg4.png", "img/destroyer_dmg4.png"]

        self.cruiser_hitframes = ["img/cruiser_dmg1.png", "img/cruiser_dmg1.png", "img/cruiser_dmg1.png", "img/cruiser_dmg1.png",
                                  "img/cruiser_dmg2.png", "img/cruiser_dmg2.png", "img/cruiser_dmg2.png", "img/cruiser_dmg2.png", "img/cruiser_dmg2.png",
                                  "img/cruiser_dmg3.png", "img/cruiser_dmg3.png", "img/cruiser_dmg3.png", "img/cruiser_dmg3.png", "img/cruiser_dmg3.png",
                                  "img/cruiser_dmg4.png", "img/cruiser_dmg4.png","img/cruiser_dmg4.png", "img/cruiser_dmg4.png"]

        self.laztanker_hitframes = ["img/laz0rtanker_dmg1.png", "img/laz0rtanker_dmg1.png", "img/laz0rtanker_dmg1.png",  "img/laz0rtanker_dmg1.png", "img/laz0rtanker_dmg1.png",
                                     "img/laz0rtanker_dmg2.png", "img/laz0rtanker_dmg2.png", "img/laz0rtanker_dmg2.png", "img/laz0rtanker_dmg2.png", "img/laz0rtanker_dmg2.png", "img/laz0rtanker_dmg2.png",
                                     "img/laz0rtanker_dmg3.png", "img/laz0rtanker_dmg3.png", "img/laz0rtanker_dmg3.png", "img/laz0rtanker_dmg3.png", "img/laz0rtanker_dmg3.png", "img/laz0rtanker_dmg3.png",
                                     "img/laz0rtanker_dmg4.png", "img/laz0rtanker_dmg4.png", "img/laz0rtanker_dmg4.png", "img/laz0rtanker_dmg4.png", "img/laz0rtanker_dmg4.png", "img/laz0rtanker_dmg4.png",
                                     "img/laz0rtanker_dmg5.png", "img/laz0rtanker_dmg5.png", "img/laz0rtanker_dmg5.png", "img/laz0rtanker_dmg5.png", "img/laz0rtanker_dmg5.png"]

        self.bombarder_hitframes = ["img/bombarder_dmg1.png", "img/bombarder_dmg1.png", "img/bombarder_dmg1.png", "img/bombarder_dmg1.png",
                                    "img/bombarder_dmg2.png", "img/bombarder_dmg2.png", "img/bombarder_dmg1.png", "img/bombarder_dmg1.png", "img/bombarder_dmg1.png",
                                    "img/bombarder_dmg3.png", "img/bombarder_dmg3.png", "img/bombarder_dmg3.png", "img/bombarder_dmg3.png", "img/bombarder_dmg3.png",
                                    "img/bombarder_dmg4.png", "img/bombarder_dmg4.png", "img/bombarder_dmg3.png", "img/bombarder_dmg3.png", "img/bombarder_dmg3.png",
                                    "img/bombarder_dmg5.png",  "img/bombarder_dmg5.png",  "img/bombarder_dmg5.png", "img/bombarder_dmg5.png",]
                                    


        # Orbital shield settings
        self.shield_colors = [
            (200, 255, 255),  # light cyan (ultimate)   
            (0, 255, 255),   # cyan (improved)
            (0, 0, 255),     # blue
            (0, 255, 0),     # green
            (255, 255, 0),   # yellow
            (255, 165, 0),   # orange
            (255, 0, 0),     # red
            (128, 0, 128)    #purple (worst damage)
                        ]
        self.shield_regen_delay = 10000  # 10 seconds of no hits -> orbital shields regenerate one level

        # Powerup drop probabilities (1 in N) - if I ever get to this feature.
        self.powerup_probs = {
            "shockwave": 30,
            "squadron": 40,
            "emp": 50,
            "nanite": 60,
            "mac" : 80
                         }

        # Max powerup inventory counts
        self.powerup_maxes = {
            "shockwave": 3,
            "squadron": 3,
            "emp": 3,
            "nanite": 3,
            "mac": 3
                    }

        self.bg_img = None

    def load_images(self):
        """Loads all background images to useable surfaces. Call this after display.set_mode so convert() works correctly. 
        This is one of the only code blocks where, after consulting an AI, I copy-pasted the code to save time, inspecting it & adding comments afterwards."""

        #load all background images into settings as pygame objects; scale them, with reference names to be used in the main file.
        starter = pygame.image.load(self.starter_bg_path).convert()
        self.bg_starter = pygame.transform.scale(starter, (self.screen_width, self.screen_height))

        bg_3_4 = pygame.image.load(self._3to4_bg_path).convert()
        self.bg_3to4 = pygame.transform.scale(bg_3_4, (self.screen_width, self.screen_height))

        bg_5_6 = pygame.image.load(self._5to6_bg_path).convert()
        self.bg_5to6 = pygame.transform.scale(bg_5_6, (self.screen_width, self.screen_height))

        bg_7_8 = pygame.image.load(self._7to8_bg_path).convert()
        self.bg_7to8 = pygame.transform.scale(bg_7_8, (self.screen_width, self.screen_height))

        bg_9_10 = pygame.image.load(self._9to10_bg_path).convert()
        self.bg_9to10 = pygame.transform.scale(bg_9_10, (self.screen_width, self.screen_height))

        # Defeat / Victory
        defeat = pygame.image.load(self.defeat_screen).convert()
        self.bg_defeat = pygame.transform.scale(defeat, (self.screen_width, self.screen_height))

        victory = pygame.image.load(self.victory_screen).convert()
        self.bg_victory = pygame.transform.scale(victory, (self.screen_width, self.screen_height))