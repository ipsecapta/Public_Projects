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
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class Settings:
    def __init__(self):
        # Screen width, height, and path to background image of space - loading and scaling of images happens below, in load_images()
        self.screen_width = 1200
        self.screen_height = 580
        self.starter_bg_path = resource_path("img/background.png")
        self._3to4_bg_path = resource_path('img/background_3-4.png')
        self._5to6_bg_path = resource_path('img/background_5-6.png')
        self._7to8_bg_path = resource_path('img/background_7-8.png')
        self._9to10_bg_path = resource_path('img/background_9-10.png')
        self.startscreen_path = resource_path("img/starterscreen.png")
        self.defeat_screen = resource_path("img/glassed_earth.png")
        self.victory_screen = resource_path("img/victory.png")
        self.secret_menu_bg_path = resource_path("img/secret_menu_background.png")
        self.bonus_wave_bg_path = resource_path("img/bonus_wave_background.png")
        self.nyancat_bg_path = resource_path("img/nyancat_background.png")
        self.multiplayer_resizer = 1

        # Background transition (normal gameplay wave background swaps)
        self.bg_fade_enabled = True
        self.bg_fade_duration_ms = 800

        self.player_ship_height = 40
        self.player_ship_width = 60

        # Core alien sprite paths (base frame only; damage frames are listed below)
        self.alien_sprite_paths = {
            1: resource_path("img/alien1clean.png"),
            2: resource_path("img/alien2clean.png"),
            3: resource_path("img/alien3clean.png"),
            4: resource_path("img/alien4clean.png"),
            5: resource_path("img/destroyer_dmg0.png"),
            6: resource_path("img/cruiser_dmg0.png"),
            7: resource_path("img/laz0rtanker_dmg0.png"),
            # 8: resource_path("img/gunship_dmg0.png"),  # uncomment once gunship is hooked up
        }
        
#********* PLAYER SHIP SETTINGS
        self.base_ship_speed = 3
        self.player_starting_lives= 3
        self.player_starting_health= 11
        self.player_respawn_time_ms= 4000
        
        #Movement Keys:
        self.player1_keys = { #set movement keys for player 1 - IF YOU CHANGE THESE, MAKE SURE TO CHANGE self.p1keydesc, BELOW, AS WELL.
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "fire": pygame.K_RCTRL,
            "squadron": pygame.K_BACKSPACE,  # or separate
            "nanites": pygame.K_BACKSLASH,
            "shockwave": pygame.K_RETURN,
            "emp": pygame.K_RSHIFT,
            "mac" : pygame.K_DELETE
        }

        self.player2_keys = { # set movement keys for player 2 - IF YOU CHANGE THESE, MAKE SURE TO CHANGE self.p2keydesc, BELOW, AS WELL
            "left": pygame.K_a,
            "right": pygame.K_d,
            "up": pygame.K_w,
            "down": pygame.K_s,
            "fire": pygame.K_LCTRL,
            "squadron": pygame.K_BACKQUOTE,
            "nanites": pygame.K_TAB,
            "shockwave": pygame.K_CAPSLOCK,
            "emp": pygame.K_LSHIFT,
            "mac" : pygame.K_1
                          }
        
        self.player3_keys = { # set movement keys for player 3 - IF YOU CHANGE THESE, MAKE SURE TO CHANGE self.p3keydesc, BELOW, AS WELL
            "left": pygame.K_KP1,
            "right": pygame.K_KP3,
            "up": pygame.K_KP5,
            "down": pygame.K_KP2,
            "fire": pygame.K_KP0,
            "squadron": pygame.K_KP7,
            "nanites": pygame.K_KP8,
            "shockwave": pygame.K_KP9,
            "emp": pygame.K_KP_PLUS,
            "mac" : pygame.K_KP_MINUS
                          }
        
        self.player4_keys = { # set movement keys for player 2 - IF YOU CHANGE THESE, MAKE SURE TO CHANGE self.p4keydesc, BELOW, AS WELL
            "left": pygame.K_j,
            "right": pygame.K_l,
            "up": pygame.K_i,
            "down": pygame.K_k,
            "fire": pygame.K_SPACE,
            "squadron": pygame.K_7,
            "nanites": pygame.K_y,
            "shockwave": pygame.K_h,
            "emp": pygame.K_b,
            "mac" : pygame.K_v
                          }

        #Movement key descriptions:
        self.p1keydesc= ("the ARROW KEYS, plus the RIGHT CTRL button to fire.")
        self.p2keydesc= ("w=UP, s=DOWN, a=LEFT, d=RIGHT, LEFT CTRL=FIRE.")
        self.p3keydesc = ("numpad5=UP, numpad2=DOWN, numpad1=LEFT, numpad3=RIGHT, numpad0=FIRE.")
        self.p4keydesc = ("i=UP, k=DOWN, j=LEFT l=RIGHT, spacebar=FIRE.")

        #HUD elements:
        self.hud_text_color = (255,255,255) #white text for overall HUD
        self.player1_hud_color = (70, 170,255) #blue for player 1
        self.player2_hud_color = (255, 60, 20) #RED for player 2
        self.player3_hud_color = (100, 225, 255) #cyan for player 3
        self.player4_hud_color= (255, 190, 200) #pink for player 4

        # Bullet settings for human and normal aliens
        self.bullet_speed = 6
        self.bullet_width = 4
        self.bullet_height = 16

        self.player_firework_width = 6
        self.player_firework_height = 6
        self.player_firework_speed = 5
        self.player_firework_bloom_speed = 9
        self.player_firework_spark_height = 4
        self.player_firework_spark_width = 4
        self.player_firework_colors = [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

        # Victory fireworks tuning (normal-mode victory screen)
        # Shell deceleration behavior
        self.victory_firework_shell_decel_zone_px = 85.0  # start slowing this many px before detonation
        self.victory_firework_shell_decel_exponent = 1.25  # higher => more pronounced slowdown near detonation
        self.victory_firework_shell_min_speed_factor = 0.05  # minimum fraction of player_firework_speed near detonation
        # Shell blink
        self.victory_firework_shell_blink_rate_ms = 40
        # Spark behavior
        self.victory_firework_spark_speed_slowdown = 1.0  # sparks move at (player_firework_bloom_speed - slowdown)
        self.victory_firework_spark_lifetime_min_ms = 2000
        self.victory_firework_spark_lifetime_max_ms = 3000
        self.victory_firework_spark_fade_ms = 600
        # Number of 8-way spark sets per explosion (difficulty scaling)
        self.victory_firework_spark_sets_normal = 3
        self.victory_firework_spark_sets_hard = 2
        # Sparks per set (how many radial directions). Normal uses classic 8-way; Hard uses denser 16-way.
        self.victory_firework_sparks_per_set_normal = 8
        self.victory_firework_sparks_per_set_hard = 16
        # Delay between each 8-spark set (used when sets > 1), in milliseconds
        self.victory_firework_spark_set_delay_ms = 100

        # Nanite beam (arc-welder flicker) tuning
        # The beam is only drawn while a nanite is in "pulse" state.
        self.nanite_beam_flicker_min_ms = 10
        self.nanite_beam_flicker_max_ms = 35
        self.nanite_beam_on_probability = 0.85
        self.nanite_beam_alpha_min = 80
        self.nanite_beam_alpha_max = 255

        #bullet_max and ship speed settings for leveled up human players:
        self.player_fire_speed = 150 #150 ms between shots at all levels except level 11 - see below.
        self.levelup_speed_increase = .05 # how much faster should a player go each level they increase?
        self.lvl0_bullet_max = 2 #starting off, you can only fire one bullet.
        self.lvl0_speed = self.base_ship_speed
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
        self.lvl11_fire_speed = 75 #75 ms between firing if fire button is mashed down. 2x faster than ordinary.
        self.lvl11_bullet_color = (100, 255, 255) #special bullet color at level 11
        self.lvl11_speed = self.lvl10_speed + 0.085 #extra bump at level 11

        self.lvl0_xp_requirement = range(0, 749) #this is needed for some of the other code to work -specifically, the getattr statement in apply_start_config, where player starting score is computed
        self.lvl1_xp_requirement = range(750, 2999) #+1250
        self.lvl2_xp_requirement = range(3000,4999) #+2000
        self.lvl3_xp_requirement = range(5000,7999) #+3000
        self.lvl4_xp_requirement = range(8000,11999) #+4000
        self.lvl5_xp_requirement = range(12000,15999) #+4000
        self.lvl6_xp_requirement = range(16000,20999) #+5000
        self.lvl7_xp_requirement = range(21000,26999) #+6000
        self.lvl8_xp_requirement = range(27000,33999) #+7000
        self.lvl9_xp_requirement = range(34000,41999) #+8000
        self.lvl10_xp_requirement = range(42000,51999) #+10,000
        self.lvl10_xp_requirement_hardmode = range (4200,49999)
        self.lvl11_xp_requirement = 52000
        self.lvl11_xp_requirement_hardmode = 50000

       # experiment for later - using a for loop to create a dictionary holding info for levelups and bullets
       # #for number in range (1,11):
            #lvl_to_bullet_dict.append(number:number+2)

#**********ALIEN SETTINGS
        #bullet settings for alien sprites (width and length are included above), including different classes.-->
        #different speeds are taken care of in bullet.py with simple arithmetic.
        self.alien_bullet_speed = 3
        self.alien_bullet_width = 3
        self.alien_bullet_height = 12

        self.destroyer_bullet_width = 4
        self.destroyer_bullet_height = 14
        self.destroyer_bullet_max = 3

        self.cruiser_bullet_width = 21
        self.cruiser_bullet_height = 4
        self.cruiser_bullet_max = 1

        self.laztanker_bullet_width = 2 #doesn't get any smaller than 2 pixels
        self.laztanker_bullet_height = 28
        self.laztanker_bullet_max = 38
        self.laserminion_path = resource_path("img/laserminion.png")

        
        # Laserminion settings
        self.laserminion_drift_speed = 2.0  # Movement speed for laserminion drift
        self.laserminion_bomb_start_speed = 1.0  # Initial speed of laserminion bomb
        self.laserminion_bomb_acceleration = 0.01  # Acceleration per frame (1%)
        self.laserminion_bomb_colors = [(255, 0, 0), (255, 255, 255)]  # Red and white alternating (for testing)
        self.laserminion_min_fire_interval = 4000  # 4 seconds min
        self.laserminion_max_fire_interval = 5000  # 5 seconds max 


        self.alien1_bullet_max = 1
        self.alien2_bullet_max = 2
        self.alien3_bullet_max = 2
        self.alien4_bullet_max = 0
        self.interceptorminion_bullet_max = 2
        

        #bullet setting for boss alien
        self.boss_bullet_width = 12
        self.boss_bullet_height = 16
        self.boss_bullet_max = 7 #note these bullets will be larger.

        #Bullet styles - I have chosen to have human bullets look different from aliens' - and eventually, a third type, a boss aliens.
        self.player_bullet_color = (255, 255, 100) #A bright yellow laser bolt from human ships
        self.alien_bullet_color = (220, 255, 220) #A pale green laser from alien ships
        self.destroyerandcruiser_bullet_color = (255, 220, 255) #a light magenta bullet fired from destroyers and cruisers
        self.laztanker_bullet_color = (255, 100, 100) #a pure red laser from laser tankers
        self.gunship_bullet_color = (240, 255, 240) #a whitish greenish plasma bomb fired by gunships
        self.boss_bullet_color = (255, 255, 255) #Pure white for the bullets fired by boss aliens.

        # Alien ship speed settings (base)
        self.alien1_strafe_speed = 0.5 #for level 1 alien advance speed, see self.fleet_advance_speed below.
        self.alien2_speed = 0.22
        self.alien3_speed = 2.3
        self.alien4_speed = 1.65
        self.destroyer_speed = 0.5
        self.destroyer_list_speed = .5
        self.cruiser_speed = 0.33
        self.cruiser_list_speed = .33
        self.laztanker_speed = 0.25
        self.gunship_strafe_speed = 0.25 #gunships never advance, only strafe in the back row like artillery.

        self.interceptor_speed = 2
        self.boss_speed = 3

        #alien fleet direction, placement & speed settings (level 1 aliens spawn in fleets)
        self.fleet_direction = 1
        self.fleet_advance_speed = .02
        self.fleet_entry_speed = .5
        self.level1_warp_rows = 4
        self.fleet_warp_entry_speed = 18
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
        self.cruiser_wing_min_fire_interval = 4000  # Wing firing interval (independent of main gun)
        self.cruiser_wing_max_fire_interval = 4010
        self.laztanker_min_fire_interval = 120
        self.laztanker_max_fire_interval = 121


        #Alien ship spawning interval settings:
        self.alien2_min_spawn_interval = 5000
        self.alien2_max_spawn_interval = 10000
        self.alien3_min_spawn_interval = 10000
        self.alien3_max_spawn_interval = 18000
        self.alien4_min_spawn_interval = 18000
        self.alien4_max_spawn_interval = 18001
        self.destroyer_min_spawn_interval = 20000
        self.destroyer_max_spawn_interval = 40000
        self.cruiser_min_spawn_interval = 40000
        self.cruiser_max_spawn_interval = 80000
        self.laztanker_min_spawn_interval = 80000
        self.laztanker_max_spawn_interval = 120000
        self.gunship_max_spawn_interval = 120000
        self.gunship_max_spawn_interval = 120001
        self.interceptor_spawn_interval_base = 15000 #do not go below 11000 or the math breaks.

        # delay the first spawning of higher level aliens
        self.alien2_spawn_delay = 3000
        self.alien3_spawn_delay = 5000
        self.alien4_spawn_delay = 7000
        self.destroyer_spawn_delay = 15000
        self.cruiser_spawn_delay = 20000
        self.laztanker_spawn_delay = 25000
        self.gunship_spawn_delay = 30000


        #alien wave definitions: how many of each spawn per wave
        # Each entry: how many rows of level 1, and total level 2 & 3 aliens for that wave- THIS IS DEFUNCT: I changed to constant spawn for individual aliens as long as there are fleet aliens on screen.
        #this still works though, since the program now just checks for >0; so I leave it. 
        self.wave_master_index = [
            {"rows_level1": 5,  "count_level2": 0,  "count_level3": 0, "count_level4":0, "count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_gunships": 0}, #e.g. wave one will have 5 rows of lvl 1, and 0 lvl 2 or 3 aliens.
            {"rows_level1": 6,  "count_level2": 2,  "count_level3": 0, "count_level4":0,"count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_gunships": 0},
            {"rows_level1": 7,  "count_level2": 4,  "count_level3": 1, "count_level4":0, "count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_gunships": 0},
            {"rows_level1": 8,  "count_level2": 8,  "count_level3": 3, "count_level4":1, "count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_gunships": 0},
            {"rows_level1": 9,  "count_level2": 12, "count_level3": 6, "count_level4":3, "count_destroyers":1, "count_cruisers": 0, "count_laz0rtankers": 0, "count_gunships": 0},
            {"rows_level1": 10, "count_level2": 18, "count_level3": 9, "count_level4":4, "count_destroyers":1, "count_cruisers": 1, "count_laz0rtankers": 0, "count_gunships": 0},
            {"rows_level1": 11, "count_level2": 22, "count_level3": 12, "count_level4":5, "count_destroyers":2, "count_cruisers": 1, "count_laz0rtankers": 1, "count_gunships": 0},
            {"rows_level1": 12, "count_level2": 28, "count_level3": 15, "count_level4":6, "count_destroyers":3, "count_cruisers": 2, "count_laz0rtankers": 2, "count_gunships": 0},
            {"rows_level1": 13, "count_level2": 38, "count_level3": 21, "count_level4":7, "count_destroyers":3, "count_cruisers": 3, "count_laz0rtankers": 2, "count_gunships": 0},
            {"rows_level1": 15, "count_level2": 50, "count_level3": 30, "count_level4":11, "count_destroyers":5, "count_cruisers": 4, "count_laz0rtankers": 3, "count_gunships": 0, "final_boss": 1}
        ]
        """self.wave_master_index = [
            {"rows_level1": 1,  "count_level2": 0,  "count_level3": 0, "count_level4":0, "count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_gunships": 0}, #e.g. wave one will have 5 rows of lvl 1, and 0 lvl 2 or 3 aliens.
            {"rows_level1": 1,  "count_level2": 2,  "count_level3": 0, "count_level4":0,"count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_gunships": 0},
            {"rows_level1": 1,  "count_level2": 4,  "count_level3": 1, "count_level4":0, "count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_gunships": 0},
            {"rows_level1": 1,  "count_level2": 8,  "count_level3": 3, "count_level4":1, "count_destroyers":0, "count_cruisers": 0, "count_laz0rtankers": 0, "count_gunships": 0},
            {"rows_level1": 10,  "count_level2": 12, "count_level3": 6, "count_level4":3, "count_destroyers":1, "count_cruisers": 0, "count_laz0rtankers": 0, "count_gunships": 0},
            {"rows_level1": 1, "count_level2": 18, "count_level3": 9, "count_level4":4, "count_destroyers":1, "count_cruisers": 1, "count_laz0rtankers": 0, "count_gunships": 0},
            {"rows_level1": 1, "count_level2": 22, "count_level3": 12, "count_level4":5, "count_destroyers":2, "count_cruisers": 1, "count_laz0rtankers": 1, "count_gunships": 0},
            {"rows_level1": 1, "count_level2": 28, "count_level3": 15, "count_level4":6, "count_destroyers":3, "count_cruisers": 2, "count_laz0rtankers": 2, "count_gunships": 0},
            {"rows_level1": 1, "count_level2": 38, "count_level3": 21, "count_level4":7, "count_destroyers":3, "count_cruisers": 3, "count_laz0rtankers": 2, "count_gunships": 0},
            {"rows_level1": 1, "count_level2": 50, "count_level3": 30, "count_level4":11, "count_destroyers":5, "count_cruisers": 4, "count_laz0rtankers": 3, "count_gunships": 0, "final_boss": 1}
        ]"""
        self.level1_alien_starting_rows = 4 #every wave will start with this many rows of lvl 1 aliens on screen.

        self.new_wave_pause = 5000
        # Alien sprite sizes: THESE ARE PLACEHOLDERS - VALUES WILL BE ASSIGNED TO THESE FROM THE MAIN GAME, -->
        # USING INFO FROM THE menu_helper.py gamesetup() function.
        self.alien1_spritesize = ()
        self.alien2_spritesize = ()
        self.alien3_spritesize = ()
        self.alien4_spritesize = ()
        self.destroyer_spritesize = ()
        self.cruiser_spritesize = ()
        self.laztanker_spritesize = ()
        #Alien Damage Graphics:

        """self.alien2_hitframes = ["path here"]
        self.alien2_hp = 1
        
        self.alien3_hitframes = ["path here", "path here"]
        self.alien3_hp = len(self.alien3_hitframes)

        self.alien4_hitframes = ["path here", "path here", "path here"]
        self.alien4_hp = len(self.alien4_hitframes)"""

        self.destroyer_hitframe_paths = [resource_path("img/destroyer_dmg1.png"), resource_path("img/destroyer_dmg1.png"), resource_path("img/destroyer_dmg1.png"),
                                    resource_path("img/destroyer_dmg2.png"), resource_path("img/destroyer_dmg2.png"), resource_path("img/destroyer_dmg2.png"),
                                    resource_path("img/destroyer_dmg3.png"), resource_path("img/destroyer_dmg3.png"), resource_path("img/destroyer_dmg3.png"),
                                    resource_path("img/destroyer_dmg4.png"), resource_path("img/destroyer_dmg4.png"), resource_path("img/destroyer_dmg4.png")]
                        #note that in the main file, criuser wiings are set to stop firing at the 13th image - which is the first image where the wings are destroyed. Changing image order needs to take this into account., as do any modifications of these damage sprites in future.
        self.cruiser_hitframe_paths = [resource_path("img/cruiser_dmg1.png"), resource_path("img/cruiser_dmg1.png"), resource_path("img/cruiser_dmg1.png"), resource_path("img/cruiser_dmg1.png"), resource_path("img/cruiser_dmg1.png"), resource_path("img/cruiser_dmg1.png"),
                                  resource_path("img/cruiser_dmg2.png"), resource_path("img/cruiser_dmg2.png"), resource_path("img/cruiser_dmg2.png"), resource_path("img/cruiser_dmg2.png"), resource_path("img/cruiser_dmg2.png"), resource_path("img/cruiser_dmg2.png"),
                                  resource_path("img/cruiser_dmg3.png"), resource_path("img/cruiser_dmg3.png"), resource_path("img/cruiser_dmg3.png"), resource_path("img/cruiser_dmg3.png"), resource_path("img/cruiser_dmg3.png"), resource_path("img/cruiser_dmg3.png"),
                                  resource_path("img/cruiser_dmg4.png"), resource_path("img/cruiser_dmg4.png"), resource_path("img/cruiser_dmg4.png"), resource_path("img/cruiser_dmg4.png"), resource_path("img/cruiser_dmg4.png"), resource_path("img/cruiser_dmg4.png")]

        self.laztanker_hitframe_paths = [resource_path("img/laz0rtanker_dmg1.png"), resource_path("img/laz0rtanker_dmg1.png"), resource_path("img/laz0rtanker_dmg1.png"), resource_path("img/laz0rtanker_dmg1.png"), resource_path("img/laz0rtanker_dmg1.png"), resource_path("img/laz0rtanker_dmg1.png"), resource_path("img/laz0rtanker_dmg1.png"), resource_path("img/laz0rtanker_dmg1.png"), resource_path("img/laz0rtanker_dmg1.png"),
                                     resource_path("img/laz0rtanker_dmg2.png"), resource_path("img/laz0rtanker_dmg2.png"), resource_path("img/laz0rtanker_dmg2.png"), resource_path("img/laz0rtanker_dmg2.png"), resource_path("img/laz0rtanker_dmg2.png"), resource_path("img/laz0rtanker_dmg2.png"), resource_path("img/laz0rtanker_dmg2.png"), resource_path("img/laz0rtanker_dmg2.png"), resource_path("img/laz0rtanker_dmg2.png"), 
                                     resource_path("img/laz0rtanker_dmg3.png"), resource_path("img/laz0rtanker_dmg3.png"), resource_path("img/laz0rtanker_dmg3.png"), resource_path("img/laz0rtanker_dmg3.png"), resource_path("img/laz0rtanker_dmg3.png"), resource_path("img/laz0rtanker_dmg3.png"), resource_path("img/laz0rtanker_dmg3.png"), resource_path("img/laz0rtanker_dmg3.png"), resource_path("img/laz0rtanker_dmg3.png"),
                                     resource_path("img/laz0rtanker_dmg4.png"), resource_path("img/laz0rtanker_dmg4.png"), resource_path("img/laz0rtanker_dmg4.png"), resource_path("img/laz0rtanker_dmg4.png"), resource_path("img/laz0rtanker_dmg4.png"), resource_path("img/laz0rtanker_dmg4.png"), resource_path("img/laz0rtanker_dmg4.png"), resource_path("img/laz0rtanker_dmg4.png"), resource_path("img/laz0rtanker_dmg4.png"),
                                     resource_path("img/laz0rtanker_dmg5.png"), resource_path("img/laz0rtanker_dmg5.png"), resource_path("img/laz0rtanker_dmg5.png"), resource_path("img/laz0rtanker_dmg5.png"), resource_path("img/laz0rtanker_dmg5.png"), resource_path("img/laz0rtanker_dmg5.png"), resource_path("img/laz0rtanker_dmg5.png"), resource_path("img/laz0rtanker_dmg5.png"), resource_path("img/laz0rtanker_dmg5.png"),
                                     resource_path("img/laz0rtanker_dmg6.png"), resource_path("img/laz0rtanker_dmg6.png"), resource_path("img/laz0rtanker_dmg6.png"), resource_path("img/laz0rtanker_dmg6.png"), resource_path("img/laz0rtanker_dmg6.png"), resource_path("img/laz0rtanker_dmg6.png"), resource_path("img/laz0rtanker_dmg6.png"), resource_path("img/laz0rtanker_dmg6.png"), resource_path("img/laz0rtanker_dmg6.png"),
                                     resource_path("img/laz0rtanker_dmg7.png"), resource_path("img/laz0rtanker_dmg7.png"), resource_path("img/laz0rtanker_dmg7.png"), resource_path("img/laz0rtanker_dmg7.png"), resource_path("img/laz0rtanker_dmg7.png"), resource_path("img/laz0rtanker_dmg7.png"), resource_path("img/laz0rtanker_dmg7.png"), resource_path("img/laz0rtanker_dmg7.png"), resource_path("img/laz0rtanker_dmg7.png")]

        self.gunship_hitframe_paths = ["img/gunship_dmg1.png", "img/gunship_dmg1.png", "img/gunship_dmg1.png", "img/gunship_dmg1.png",
                                    "img/gunship_dmg2.png", "img/gunship_dmg2.png", "img/gunship_dmg1.png", "img/gunship_dmg1.png", "img/gunship_dmg1.png",
                                    "img/gunship_dmg3.png", "img/gunship_dmg3.png", "img/gunship_dmg3.png", "img/gunship_dmg3.png", "img/gunship_dmg3.png",
                                    "img/gunship_dmg4.png", "img/gunship_dmg4.png", "img/gunship_dmg3.png", "img/gunship_dmg3.png", "img/gunship_dmg3.png",
                                    "img/gunship_dmg5.png",  "img/gunship_dmg5.png",  "img/gunship_dmg5.png", "img/gunship_dmg5.png",]

        # Surfaces populated by load_images()
        self.alien_images = {}
        self.destroyer_hitframes = []
        self.cruiser_hitframes = []
        self.laztanker_hitframes = []
        self.gunship_hitframes = []

        #Base x and y sizes to scale various alien sprites to:
        self.alien1_spriteX = 50
        self.alien1_spriteY = 50
        self.alien2_spriteX=40
        self.alien2_spriteY=60
        self.alien3_spriteX=40
        self.alien3_spriteY=69
        self.alien4_spriteX=40
        self.alien4_spriteY=90
        self.destroyer_spriteX=100
        self.destroyer_spriteY=143
        self.cruiser_spriteX=175
        self.cruiser_spriteY=262
        self.laztanker_spriteX=275
        self.laztanker_spriteY=362
        self.gunship_spriteX = 500
        self.gunship_spriteY = 250
        self.carrier_spriteX = 400
        self.carrier_spriteY = 400
        self.interceptorminion_spriteX = 35
        self.interceptorminion_spriteY = 35


        # Orbital shield settings
        self.shield_colors = [
            (200, 255, 255),  # light cyan (best)
            (0, 255, 255),    # cyan
            (0, 255, 255),    # cyan
            (80, 200, 255),   # sub-cyan light blue
            (80, 200, 255),   # sub-cyan light blue
            (0, 128, 255),    # blue
            (0, 128, 255),    # blue
            (96, 64, 255),    # blue-purple
            (96, 64, 255),    # blue-purple
            (160, 64, 224),   # purple
            (160, 64, 224),   # purple
            (224, 64, 224),   # fuchsia-purple (danger)
            (224, 64, 224),   # fuchsia-purple (danger)
            (255, 32, 160)    # fuchsia-purple-red (dangerest)
                        ]
        self.orbital_shields_enabled = True
        self.shields_respawn_each_wave = False
        self.shield_count = 6
        self.shield_height_ratio = 0.02
        self.shield_y_ratio = 0.88
        self.shield_regen_delay = 10000  # 12 seconds of no hits -> orbital shields regenerate one level
        self.shield_start_index = 5 #this should be the same as the regen_cap_index, so that the shields do not "upcharge" past regular health unless forced
        self.shield_regen_cap_index = 5
        self.shield_repair_cap_index = 1
        self.shield_repair_hits_per_level = 4

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
        
        # ---------- HUD strip / playfield split ----------
        self.hud_strip_height = 40                    # black strip beneath playfield
        self.play_height = self.screen_height         # the "real" game area height, determining where sprites can move
        self.screen_height_total = self.play_height + self.hud_strip_height

        # ---------- Powerups: global toggles ----------
        self.powerups_enabled = True
        self.powerup_enable_squadron = True
        self.powerup_enable_shockwave = True
        self.powerup_enable_nanites = True
        self.enable_escape_pods = True  # Enable escape pods for dead players

        # Spawn behavior (no caps enforced anywhere)
        self.powerup_drop_chance = 0.06  # 6% chance on normal alien kills (1 in ~17)
        self.bonus_wave_powerup_drop_chance = .06  # 6% chance on bonus wave kills (1 in ~17)
        self.powerup_weights = {         # weighted random among enabled types
            "squadron": 3.0,      # Increased from 2.0
            "shockwave": 1.75,     # less common than squadron
            "nanites": 3.5,       # Still most common, but reduced from 4.0
        }

        # Powerup pickup drift (wide + slow zigzag, stronger downward drift than lvl2 alien)
        self.powerup_fall_speed = 0.8
        self.powerup_zigzag_amp = 34
        self.powerup_zigzag_freq = 0.018   # radians/ms-ish (we'll use ticks)

        # Paths
        self.powerup_squadron_path = resource_path("img/powerup_squadron.png")
        self.powerup_nanite_path = resource_path("img/powerup_nanite.png")
        self.powerup_shockwave_path = resource_path("img/powerup_shockwave.png")
        self.squadron_ship_path = resource_path("img/squadron.png")
        self.squadron_hurt_path = resource_path("img/squadron_hurt.png")
        self.nanite_path = resource_path("img/nanite.png")
        self.shockwave_path = resource_path("img/shockwave.png")
        
        # Bonus wave powerup paths
        self.powerup_dad_path = resource_path("img/powerup_dad.png")
        self.powerup_mom_path = resource_path("img/powerup_mom.png")
        self.dadship_path = resource_path("img/dadship.png")
        self.shockwave_dad_path = resource_path("img/shockwave_dad.png")
        self.momship_path = resource_path("img/momship.png")

        # Squadron behavior
        self.squadron_speed = 3.2 #slightly faster than player, but with diagonal motion, players still outpace squadrons
        self.squadron_speed_hardmode = 4.25 #squadrons move faster in hard mode
        self.squadron_offset_px = 10
        self.squadron_max_bullets = 2
        self.squadron_max_bullets_hardmode = 3
        self.squadron_hits_to_hurt = 2
        self.squadron_hits_to_die = 3
        self.squadron_speed_increment = 0.024
        self.squadron_speed_increment_hardmode = 0.009
        # Nanites behavior
        self.nanite_speed = 4.5
        # Per-nanite approach speed variation: sampled from [-delta, 0, +delta]
        self.nanite_speed_variation_delta = 0.5
        self.nanite_pulses = 14
        self.nanite_pulse_interval_ms = 100    # 14 pulses ~ 840ms
        self.nanite_beam_width = 6            # just a cheap visual beam (no bullet collisions)

        # Shockwave behavior
        self.shockwave_speed = 3.5
        self.shockwave_base_size = (400, 200)
        self.shockwave_kill_max_alien_level = 4  # Instakill level 1-4
        self.shockwave_damage_amount = 12  # Fixed damage for level 5-7 aliens (destroyer damage frame count)

        # ---------- Gameplay option toggles ----------
        self.difficulty_mode = "normal"   # "easy" or "normal"
        self.shields_recharge_at_new_wave = False
        self.sounds_enabled = True  # Master sound toggle
        self.music_enabled = True  # Music toggle (separate from sound effects)


        self.bg_img = None

        # ---------- Bonus Wave Settings ----------
        # Loafkitty settings
        self.loafkitty_speed = 0.3
        self.loafkitty_min_spawn_interval = 5000  # Same as level 2
        self.loafkitty_max_spawn_interval = 10000  # Same as level 2
        self.loafkitty_spawn_delay = 5000  # screen is blank for 5 seconds
        
        # Centurionkitty settings
        self.centurionkitty_speed = 2.3  # Same as level 3
        self.centurionkitty_min_spawn_interval = 10000  # Same as level 3
        self.centurionkitty_max_spawn_interval = 18000  # Same as level 3
        self.centurionkitty_spawn_delay = 30000  # 30 sec
        
        # Emperorkitty settings
        self.emperorkitty_speed = 0.5  # Faster than cruiser
        self.emperorkitty_list_speed = 0.29  # Increased by ~15% (0.25 * 1.15 = 0.2875, rounded up)
        self.emperorkitty_min_spawn_interval = 30000  # Same as cruiser
        self.emperorkitty_max_spawn_interval = 70000  # Same as cruiser
        self.emperorkitty_spawn_delay = 90000  # 1.5 minutes in
        self.emperorkitty_bullet_max = 3  # Bonus wave - bullet cap for emperorkitty
        
        # Ninjakitty settings
        self.ninjakitty_speed = 4.0  # Base speed of 4
        self.ninjakitty_min_spawn_interval = 40000  # 40 seconds
        self.ninjakitty_max_spawn_interval = 60000  # 60 seconds
        self.ninjakitty_spawn_delay = 150000  # 2.5 minutes in, first ninjakitty spawns

        # Bluewhalekitty settings
        self.bluewhalekitty_speed = 0.25  # Slower than cruiser
        self.bluewhalekitty_list_speed = 0.15
        self.bluewhalekitty_min_spawn_interval = 80000  # tweaked slightly from .5x lasertankers spawn rates
        self.bluewhalekitty_max_spawn_interval = 100000  # 
        self.bluewhalekitty_spawn_delay = 240000  # 4 minutes in, first bluewhalekitty spawns
        
        # Nyancat settings
        self.nyancat_speed = 1.5  # Slow horizontal movement
        self.nyancat_min_spawn_interval = 240000  # 4 minutes
        self.nyancat_max_spawn_interval = 240000  # 4 minutes (fixed interval)
        self.nyancat_spawn_delay = 360000  # 6 minutes in, first nyancat spawns
        self.nyancat_music_lead_ms = 7000  # start nyancat music this many ms before spawn
        # Longcat and Tacgnol settings
        self.longcat_tacgnol_speed = 0.2
        self.longcat_tacgnol_min_spawn_interval = 300000
        self.longcat_tacgnol_max_spawn_interval = 300000
        self.longcat_tacgnol_spawn_delay = 480000

        #grumpycat settings
        self.grumpycat_speed = 2
        self.grumpycat_min_spawn_interval = 60000
        self.grumpycat_max_spawn_interval = 80000
        self.grumpycat_spawn_delay = 150000
        self.grumpycat_yvect_change_interval = (4000, 8000)
        self.grumpycat_xvect_change_interval = (3000, 9000)
        self.grumpycat_bullet_max = 1

# Bonus wave kitty bullet settings
        self.loafkitty_bullet_width = 25
        self.loafkitty_bullet_height = 3
        self.loafkitty_bullet_speed = 3  # Same as alien_bullet_speed
        self.loafkitty_bullet_blink_rate_ms = 40

        self.centurionkitty_bullet_width = 3  # Same as alien_bullet_width
        self.centurionkitty_bullet_height = 12  # Same as alien_bullet_height
        self.centurionkitty_bullet_speed = 3
        self.centurionkitty_bullet_blink_rate_ms = 40  # Default

        self.emperorkitty_bullet_width = 3
        self.emperorkitty_bullet_height = 12
        self.emperorkitty_bullet_speed = 3
        self.emperorkitty_bullet_blink_rate_ms = 40

        self.bluewhalekitty_bullet_width = 2  # Same as laztanker
        self.bluewhalekitty_bullet_height = 28  # Same as laztanker
        self.bluewhalekitty_bullet_speed = 3.25  # Same as laztanker (alien_bullet_speed + 0.25)
        self.bluewhalekitty_bullet_blink_rate_ms = 40

        self.longcat_tacgnol_bullet_width = (self.screen_width * 0.9)
        self.longcat_tacgnol_bullet_height_outer = 7
        self.longcat_tacgnol_bullet_height_inner = 4
        self.longcat_tacgnol_bullet_speed = 5
        self.longcat_tacgnol_bullet_blink_rate_ms = 78

        self.grumpycat_bullet_width = 10
        self.grumpycat_bullet_height = 12
        self.grumpycat_bullet_speed_y = 2.3
        self.grumpycat_bullet_speed_x = 4.5
        self.grumpycat_bullet_blink_rate_ms = 67

        # Bonus wave enemy bullet colors
        self.loafkitty_bullet_color = (225, 155, 0)  # Yellow
        self.centurionkitty_bullet_color = (255, 0, 0)  # Red
        self.emperorkitty_bullet_color = (200, 0, 255)  # Bright purple
        self.bluewhalekitty_bullet_colors = [(150, 200, 255), (0, 100, 255)]  # Alternate lighter and deeper blue.
        self.boxcat_bullet_color = (255, 100, 0)  # Orange
       
        self.longcat_bullet_colors_inner = [(255,255,255), (0,0,0)] # inside alternates White and Black
        self.longcat_bullet_colors_outer = (255,255,255) # outline stays white
        self.tacgnol_bullet_colors_inner = (0,0,0) # core stays Black
        self.tacgnol_bullet_colors_outer = [(255,255,255), (0,0,0)] # outline alternates White and Black

        self.grumpycat_bullet_color = (0,255,0) # Green
        # Bonus wave enemy firework colors (separate from bullet colors)
        self.loafkitty_firework_color = (255, 255, 0)  # Yellow
        self.centurionkitty_firework_color = (255, 0, 0)  # Red
        self.ninjakitty_firework_color = (165, 165, 165)  # Gray
        self.emperorkitty_firework_color = (200, 0, 255)  # Bright purple
        self.bluewhalekitty_firework_color = (100, 190, 255)  # Light blue
        self.longcat_firework_color = (255, 255, 255)  # White
        self.tacgnol_firework_color = (0,0,0) # Black
        self.longcat_tacgnol_bullet_collision_firework_colors = [(255,255,255), (0,0,0)] # for explosions when longcat and tacgnol bullets collide

        self.grumpycat_firework_color = (00, 255, 0) # Green
        
        # Nyancat rainbow colors (for cycling)
        self.nyancat_rainbow_colors = [(255, 0, 0), (255, 192, 203), (255, 165, 0), (0, 255, 0),
                                       (0, 255, 255), (0, 0, 255), (128, 0, 128), (255, 0, 0)]
        #transcendence cat firework colors for flashing effect
        self.transcendence_cat_firework_colors = [(255,255,255), (255,102,178), (225,255,255), (255,0,255), 
                                                    (255,255,255), (255,153,51), (225,255,255),(255,255,0),
                                                    (255,255,255),(255,102,102)] #white,pink, lightning,fuchsia, white,orange, lightning,yellow, white,peach

        # Bonus wave timing
        self.bonus_wave_duration_ms = 1200000  # 20 minutes
        self.bonus_wave_defense_strength = 10
        self.bonus_wave_breach_values = {
            "loaf": 1,
            "centurion": 2,
            "emperor": 3,
            "bluewhale": 6,
            "ninja": 2
        }
        
        # Scaling: by 15 minutes, spawn rates are 3x faster, speeds are 2x faster
        self.bonus_wave_max_spawn_scale = 3.0  # At 15 minutes
        self.bonus_wave_max_speed_scale = 2.0  # At 15 minutes
        
        # Bonus wave backgrounds
        self.bonus_wave_defeat_bg_path = resource_path("img/victory_special.png")
        self.bonus_wave_victory_bg_path = resource_path("img/victory_perfect.png")

