#Base_settings.py
#file for basic game config
import pygame
import sys

class Settings:
    def __init__(self):
        # Screen width, height, and path to background image of space
        self.screen_width = 1200
        self.screen_height = 620
        self.bg_path = "img/background.png"

        # Ship settings for human players
        self.ship_speed = 3
        self.player1_keys = { #set movement keys for player 1
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "fire": pygame.K_RCTRL,
            "shockwave": pygame.K_BACKSPACE,
            "emp": pygame.K_BACKSLASH,
            "squadron": pygame.K_RETURN,
            "nanite": pygame.K_RSHIFT,
            "mac": pygame.K_DELETE
        }

        self.player2_keys = { # set movement keys for player 2
            "left": pygame.K_a,
            "right": pygame.K_d,
            "up": pygame.K_w,
            "down": pygame.K_s,
            "fire": pygame.K_BACKQUOTE,
            "shockwave": pygame.K_q,
            "emp": pygame.K_TAB,
            "squadron": pygame.K_CAPSLOCK,
            "nanite": pygame.K_LSHIFT,
            "mac" : pygame.K_LCTRL
                          }
        
        self.player3_keys = { # set movement keys for player 3
            "left": pygame.K_KP1,
            "right": pygame.K_KP3,
            "up": pygame.K_KP5,
            "down": pygame.K_KP2,
            "fire": pygame.K_KP0,
            "shockwave": pygame.K_KP7,
            "emp": pygame.K_KP8,
            "squadron": pygame.K_9,
            "nanite": pygame.K_KP_PLUS,
            "mac" : pygame.K_KP_MINUS
                          }
        
        self.player4_keys = { # set movement keys for player 4
            "left": pygame.K_a,
            "right": pygame.K_d,
            "up": pygame.K_w,
            "down": pygame.K_s,
            "fire": pygame.K_LCTRL,
            "shockwave": pygame.K_f,
            "emp": pygame.K_g,
            "squadron": pygame.K_h,
            "nanite": pygame.K_y,
                          }

        # Bullet settings for human and normal aliens
        self.bullet_speed = 6
        self.bullet_width = 4
        self.bullet_height = 16

        #bullet settings for leveled up human players:
        self.lvl1_bullet_max = 3
        self.lvl2_bullet_max = 4
        self.lvl3_bullet_max = 5
        self.lvl4_bullet_max = 6
        self.lvl5_bullet_max = 7
        self.lvl6_bullet_max = 8
        self.lvl7_bullet_max = 9
        self.lvl8_bullet_max = 10
        self.lvl9_bullet_max = 11
        self.lvl10_bullet_max = 12
        self.lvl11_bullet_max = 24

        self.lvl2_xp_requirement = range(1000,1999)
        self.lvl3_xp_requirement = range(2000,2999)
        self.lvl4_xp_requirement = range(3000,3999)
        self.lvl5_xp_requirement = range(4000,4999)
        self.lvl6_xp_requirement = range(5000,5999)
        self.lvl7_xp_requirement = range(6000,6999)
        self.lvl8_xp_requirement = range(7000,7999)
        self.lvl9_xp_requirement = range(8000,8999)
        self.lvl10_xp_requirement = range(9000,11999)
        self.lvl11_xp_requirement = 12000

       # experiment for later - using a for loop to create a dictionary holding info for levelups and bullets
       # #for number in range (1,11):
            #lvl_to_bullet_dict.append(number:number+2)


        #bullet settings for alien sprites (width and length are included above), including different classes.-->
        #different speeds are taken care of in bullet.py with simple arithmetic.
        self.alien_bullet_speed = 3
        self.alien_bullet_width = 3
        self.alien_bullet_height = 12

        self.destroyer_bullet_width = 4
        self.destroyer_bullet_height = 14
        self.destroyer_bullet_max = 3

        self.cruiser_bullet_width = 5
        self.cruiser_bullet_height = 14
        self.cruiser_bullet_max = 1

        self.laztanker_bullet_width = 1
        self.laztanker_bullet_height = 30
        self.laztanker_bullet_max = 12

        self.alien1_bullet_max = 1
        self.alien2_bullet_max = 2
        self.alien3_bullet_max = 2
        self.alien4_bullet_max = 0
        

        #bullet setting for boss alien
        self.boss_bullet_width = 12
        self.boss_bullet_height = 16
        self.boss_bullet_max = 7 #note these bullets will be larger.

        #Bullet styles - I have chosen to have human bullets look different from aliens' - and eventually, a third type, a boss aliens.
        self.player_bullet_color = (255, 255, 80) #A bright yellow laser bolt from human ships
        self.alien_bullet_color = (220, 255, 240) #A whitish green laser from alien ships
        self.destroyerandcruiser_bullet_color = (255, 220, 255) #Destroyer and cruiser bullets are a deeper green.
        self.laztanker_bullet_color = (255, 0, 0) #a pure red laser from laser tankers
        self.boss_bullet_color = (255, 255, 255) #A bright white for the bullets fired by boss aliens.

        # Alien ship speed settings (base)
        self.alien1_strafe_speed = 0.5 #for level 1 alien advance speed, see self.fleet_advance_speed below.
        self.alien2_speed = 0.22
        self.alien3_speed = 2.4
        self.alien4_speed = 2
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
        self.laztanker_min_fire_interval = 110
        self.laztanker_max_fire_interval = 111


        #Alien ship spawning interval settings:
        self.alien2_min_spawn_interval = 5000
        self.alien2_max_spawn_interval = 10000
        self.alien3_min_spawn_interval = 7000
        self.alien3_max_spawn_interval = 14000
        self.alien4_min_spawn_interval = 10000
        self.alien4_max_spawn_interval = 18000
        self.destroyer_min_spawn_interval = 16000
        self.destroyer_max_spawn_interval = 22000
        self.cruiser_min_spawn_interval = 33000
        self.cruiser_max_spawn_interval = 44000
        self.laztanker_min_spawn_interval = 30000
        self.laztanker_max_spawn_interval = 60000
        
        # delay the first spawning of higher level aliens
        self.alien2_spawn_delay = 3000
        self.alien3_spawn_delay = 5000
        self.alien4_spawn_delay = 7000
        self.destroyer_spawn_delay = 15000


        #alien wave definitions: how many of each spawn per wave
        # Each entry: how many rows of level 1, and total level 2 & 3 aliens for that wave
        self.wave_master_index = [
            {"rows_level1": 5,  "count_level2": 40,  "count_level3": 40, "count_level4":4, "count_destroyers":3, "count_cruisers": 0, "count_lazortankers": 0, "count_bombarders": 0}, #e.g. wave one will have 5 rows of lvl 1, and 0 lvl 2 or 3 aliens.
            {"rows_level1": 6,  "count_level2": 2,  "count_level3": 0, "count_level4":0,"count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_bombarders": 0},
            {"rows_level1": 7,  "count_level2": 4,  "count_level3": 1, "count_level4":0, "count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_bombarders": 0},
            {"rows_level1": 8,  "count_level2": 8,  "count_level3": 3, "count_level4":1, "count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_bombarders": 0},
            {"rows_level1": 9,  "count_level2": 12, "count_level3": 6, "count_level4":3, "count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_bombarders": 0},
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

        self.destroyer_hitframes = ["img/destroyer_dmg1.png", "img/destroyer_dmg1.png",
                                    "img/destroyer_dmg2.png", "img/destroyer_dmg2.png",
                                    "img/destroyer_dmg3.png", "img/destroyer_dmg3.png",
                                    "img/destroyer_dmg4.png","img/destroyer_dmg4.png"]

        self.cruiser_hitframes = ["img/cruiser_dmg1.png", "img/cruiser_dmg1.png",
                                  "img/cruiser_dmg2.png", "img/cruiser_dmg2.png", "img/cruiser_dmg2.png",
                                  "img/cruiser_dmg3.png", "img/cruiser_dmg3.png",
                                  "img/cruiser_dmg4.png", "img/cruiser_dmg4.png","img/cruiser_dmg4.png"]

        self.laztanker_hitframes = ["img/laz0rtanker_dmg1.png", "img/laz0rtanker_dmg1.png", "img/laz0rtanker_dmg1.png",
                                     "img/laz0rtanker_dmg2.png", "img/laz0rtanker_dmg2.png",
                                     "img/laz0rtanker_dmg3.png", "img/laz0rtanker_dmg3.png", "img/laz0rtanker_dmg3.png",
                                     "img/laz0rtanker_dmg4.png", "img/laz0rtanker_dmg4.png",
                                     "img/laz0rtanker_dmg5.png", "img/laz0rtanker_dmg5.png", "img/laz0rtanker_dmg5.png"]

        self.bombarder_hitframes = ["img/bombarder_dmg1.png", "img/bombarder_dmg1.png", "img/bombarder_dmg1.png",
                                    "img/bombarder_dmg2.png", "img/bombarder_dmg2.png", "img/bombarder_dmg2.png",
                                    "img/bombarder_dmg3.png", "img/bombarder_dmg3.png", "img/bombarder_dmg3.png",
                                    "img/bombarder_dmg4.png", "img/bombarder_dmg4.png", "img/bombarder_dmg4.png",
                                    "img/bombarder_dmg5.png",  "img/bombarder_dmg5.png",  "img/bombarder_dmg5.png",
                                    "img/bombarder_dmg6.png", "img/bombarder_dmg6.png", "img/bombarder_dmg6.png",]


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

    def load_images(self, screen):
        """Call this after display.set_mode so convert() works correctly."""
        bg_img = pygame.image.load(self.bg_path).convert()#load the background image of space
        self.bg_img = pygame.transform.scale(bg_img, (self.screen_width, self.screen_height)) #scale the background image to be the same size as the window       
