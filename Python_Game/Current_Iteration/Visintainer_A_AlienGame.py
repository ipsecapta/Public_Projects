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

import sys
import pygame
import copy
import random
import os

from base_settings import Settings, resource_path #import Settings module before other custom - because custom modules are referencing base_settings through the main file's code,-->
                                   #-->not directly from the base_settings module.
from ship import Ship, Lifepod_Squadron
from bullet import Bullet, NyancatBullet, VictoryFireworkShell, VictoryFireworkShellSmall
from alien import Alien, Minion, Laserminion, LaserminionBomb
from shield import Shield  # orbital shield sprite
from menu_main import MenuMain
from powerups import PowerUpPickup, SquadronShip, Nanite, Shockwave, choose_powerup_type, DadShip, DadShockwave, MomShip, MomBullet
from bonus_wave import BonusWaveEnemy, BonusWaveFirework  # bonus wave - custom secret wave enemies
import math  # bonus wave - for firework angle calculations

from death_animations import LazertankerDeathAnimation, CruiserDeathAnimation, DestroyerDeathAnimation
from sound_manager import AudioManager

#create the game class
class AlienInvasion:
    """Class to manage entire game, its classes, assets, and behavior of elements."""
#initialize it with the init function:
    def __init__(self):
        """initialize the game, create game resources"""
        pygame.init() # initialize pygame background settings the game will need to function correctly
        pygame.mixer.init() #initialize pygame game sounds capability
        pygame.mixer.set_num_channels(24)  # 24 channels for better sound management


        pygame.display.set_caption("Alien Invasion!") # set the title for the game
        
        self.clock = pygame.time.Clock() #this lets pygame automatically handle the frame rate correction. It creates a clock that ticks one on each pass through the main loop.
        self.settings = Settings() # import settings from base_settings.py and assign them to an attribute of the __init__ function.

        # Audio manager (loaded early so sounds are available for menus)
        self.audio = AudioManager(self.settings)
        self.audio.load_sounds()

#basic visuals setup:
    #Initialize HUD elements
        self._update_hud_font_size()  # Scale HUD font based on resolution
        self.hud_text_color = self.settings.hud_text_color #get default HUD color from base settings (white)
        
        # Performance optimization: Cache key name lookups
        self._key_name_cache = {}
        
        # Performance optimization: Cache HUD rendered surfaces per player
        # Structure: {player_id: {'hp': (surface, last_value), 'lives': (surface, last_value), 'level': (surface, last_value), 'powerups': {ptype: (surface, last_value)}}}
        self._hud_cache = {}

        # Background crossfade state (used when wave-based bg_ref changes during normal gameplay)
        self._bg_last_ref = None
        self._bg_fade_active = False
        self._bg_fade_start_ms = 0
        self._bg_fade_duration_ms = 0
        self._bg_fade_old = None
        self._bg_fade_new = None
        self._bg_fade_new_ref = None

    #Create screen -->create the screen according to the specifications in in the base_settings file, and allow it to be resizable:
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height_total), pygame.RESIZABLE) 
    # Next create the ship sprite groups
        self.players = pygame.sprite.Group() # create the sprite grouping for both player ship sprites. menu_helpers module will populate this group based on player input.
        self.players_inactive = 0
        self.shields = pygame.sprite.Group()  # hold orbital shield sprites
        self._shields_initialized = False  # gate shield creation so they only spawn when enabled

    #then the alien sprite groups
        self.aliens = pygame.sprite.Group()
        self.minions = pygame.sprite.Group()  # Sprite group for minion entities
    #Then bullet sprite groups:
        self.player_bullets = pygame.sprite.Group()#create a pygame Group object including all player bullets
        self.alien_bullets = pygame.sprite.Group()# "" "" all alien bullets.
        
        # Victory fireworks (normal mode only): cosmetic spark blooms
        self.victory_fireworks = pygame.sprite.Group()
        self.victory_fireworks_active = False
        
        # Bonus wave sprite groups #bonus wave - custom secret wave enemies
        self.bonus_wave_enemies = pygame.sprite.Group()
        self.bonus_wave_fireworks = pygame.sprite.Group()
        self.is_bonus_wave = False  # bonus wave - flag to track if in bonus wave mode
        self.bonus_wave_start_time = None  # bonus wave - track when bonus wave started
        self.bonus_wave_defense_strength = 10  # bonus wave - defense strength starts at 10
        
        # Bonus wave powerup sprite groups
        self.dad_ships = pygame.sprite.Group()  # bonus wave - dad ships
        self.dad_shockwaves = pygame.sprite.Group()  # bonus wave - dad shockwaves
        self.mom_ships = pygame.sprite.Group()  # bonus wave - mom ships
        self.mom_bullets = pygame.sprite.Group()  # bonus wave - mom bullets
        self.player_shields = {}  # bonus wave - track shields created by mom bullets per player {player_id: Shield}

        # Escape pod sprite group
        self.lifepods = pygame.sprite.Group()  # escape pods for dead players
        self.next_dad_run_time = None  # bonus wave - timer for next dad ship run
        
        # Lasertanker death animation sprites
        self.lazertanker_death_animations = pygame.sprite.Group()
        # Cruiser death animation sprites
        self.cruiser_death_animations = pygame.sprite.Group()
        # Destroyer death animation sprites
        self.destroyer_death_animations = pygame.sprite.Group()
        
        # Nyancat music channel is now owned by AudioManager

#set up wave mechanics:
        self.current_wave_num = None #wave will be selected at game start
        self.game_state = "start_menu" #have six: start_menu, countdown, playing, paused, between_waves, or finished.
        self._previous_game_state = "playing"  # Track state before pause

        # Pause menu state
        self.pause_menu_selection = 0  # 0 = Resume, 1 = Quit to Main Menu
        self.pause_menu_confirming_quit = False
        self.pause_menu_quit_selection = 0  # 0 = No, 1 = Yes
        self.pause_info_selection = -1  # -1 = none selected (Resume/Quit active), 0 = Sound toggle
        self.next_wave_start_time = None
        self.wave_banner_active = False
        
        # Countdown timer state
        self.countdown_start_time = None
        self.countdown_duration_ms = 4000  # 4 seconds total (1s per number + GO!)
        
        # Defeat/Victory screen state
        self.defeat_banner_x = None
        self.defeat_banner_active = False
        self.victory_banner_x = None
        self.victory_banner_active = False
        self.victory_banner_text = None
        self.credits_y = None
        self.credits_active = False
        self.thanks_active = False
        self.password_phase = None  # None, "transmission", "password"
        self.password_start_time = None
        # Credits data:
        # - final_player_snapshots: per-player snapshot of score/powerups at final death (player sprite is about to be killed)
        # - final_player_data: full per-player rows used by credits, built once at victory/defeat screen init
        self.final_player_snapshots = {}  # {player_id: {"player_score": int, "powerups_used": dict}}
        self.final_player_data = []  # [{"player_id": int, "player_score": int, "powerups_used": dict, ...stats...}]
        
        # Player statistics tracking for credits
        self.player_stats = {}  # {player_id: {
            # 'damage_taken': 0,
            # 'lives_lost': 0,
            # 'bullets_fired': 0,
            # 'bullets_hit': 0,
            # 'shield_recharge_shots': 0,
            # 'alien_collision_kills': 0,
            # 'time_in_top_30_percent': 0,  # milliseconds
            # 'enemies_destroyed': 0
        # }}
        
        # Track which players were active at game start (for credits display)
        self.active_player_ids = []
        
        # Cached ship images for credits (loaded once, reused)
        self.credits_ship_images = None
        
        # Defeat/victory music tracking
        self.defeat_screen_start_time = None
        self.victory_screen_start_time = None
        # (music channels are tracked by self.audio)
        self.wave_banner_text = ""
        self.wave_banner_x = 0.0
        self.wave_banner_y = int(self.settings.screen_height * 0.2)
        self.wave_banner_speed = 4.0
        self.between_wave_phase = None
        self.wave_complete_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.14))
        self.warping_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.10))
        self.warp_banner_end_time = None
        self.warp_blink_period_ms = 400

        self.max_visible_level1_rows = 4 #only four rows of level 1 aliens on screen at any given time
        self.level1_row_spawn_delay_ms = 800 #delay the spawning of the next row for just under a second (800 milliseconds)
        self.level1_reinforcements_threshhold = 60 #when current row is 50 pixels down the screen, spawn next row.

        #Baselines so menu config can be re-applied without compounding numerical values
        self._base_wave_master_index = copy.deepcopy(self.settings.wave_master_index)
        self._base_level1_alien_starting_rows = self.settings.level1_alien_starting_rows
        self._base_fleet_advance_speed = self.settings.fleet_advance_speed
        self._base_level1_reinforce_threshold = self.level1_reinforcements_threshhold
        
        # Baselines for wave-based scaling
        self._base_alien2_speed = self.settings.alien2_speed
        self._base_alien3_speed = self.settings.alien3_speed
        self._base_alien4_speed = self.settings.alien4_speed
        self._base_destroyer_speed = self.settings.destroyer_speed
        self._base_cruiser_speed = self.settings.cruiser_speed
        self._base_laztanker_speed = self.settings.laztanker_speed
        self._base_alien2_min_fire_interval = self.settings.alien2_min_fire_interval
        self._base_alien2_max_fire_interval = self.settings.alien2_max_fire_interval
        self._base_alien3_min_fire_interval = self.settings.alien3_min_fire_interval
        self._base_alien3_max_fire_interval = self.settings.alien3_max_fire_interval
        self._base_destroyer_min_fire_interval = self.settings.destroyer_min_fire_interval
        self._base_destroyer_max_fire_interval = self.settings.destroyer_max_fire_interval
        self._base_cruiser_min_fire_interval = self.settings.cruiser_min_fire_interval
        self._base_cruiser_max_fire_interval = self.settings.cruiser_max_fire_interval
        self._base_laztanker_min_fire_interval = self.settings.laztanker_min_fire_interval
        self._base_laztanker_max_fire_interval = self.settings.laztanker_max_fire_interval
        self._base_alien_bullet_width = self.settings.alien_bullet_width
        self._base_alien_bullet_height = self.settings.alien_bullet_height
        self._base_destroyer_bullet_width = self.settings.destroyer_bullet_width
        self._base_destroyer_bullet_height = self.settings.destroyer_bullet_height
        self._base_cruiser_bullet_width = self.settings.cruiser_bullet_width
        self._base_cruiser_bullet_height = self.settings.cruiser_bullet_height
        self._base_laztanker_bullet_width = self.settings.laztanker_bullet_width
        self._base_laztanker_bullet_height = self.settings.laztanker_bullet_height
        self._base_boss_bullet_width = self.settings.boss_bullet_width
        self._base_boss_bullet_height = self.settings.boss_bullet_height


        self.level1_rows_total = 0 #counter for total number of lvl1 aliens in this wave
        self.level1_rows_spawned = 0 #counter for how many are spawned
        self.level1_rows_remaining = 0 #counter for how many are left.

        self.level2_remaining = 0 #counter for how many level 2 aliens remain for this wave
        self.level3_remaining = 0 #counter for how many level 3 aliens remain for a given wave
        self.level4_remaining = 0 # "" level 4 ""
        self.next_level1_row_time = 0 #timer till next level1 alien spawn
        self.next_level2_spawn_time = 0 #timer till next lvl2 alien spawn
        self.next_level3_spawn_time = 0 #timer till text lvl3 alien spawn
        self.next_level4_spawn_time = 0 # " " lvl4 " "
        self.next_destroyer_spawn_time = 0
        self.next_cruiser_spawn_time = 0
    

#Setup POWERUP groups and inventories:

        self.powerups = pygame.sprite.Group()     # pickups drifting down
        self.squadrons = pygame.sprite.Group()    # active squadron ships
        self.nanites = pygame.sprite.Group()      # active nanites
        self.shockwaves = pygame.sprite.Group()   # active shockwaves
    #Function to set up graphics based on gamesetup() input - is called below, at start of Main Game Loop.
    def _load_images(self):
            """Loads all background images to useable surfaces. This is called in the Main Game Loop below. (Note that this mus be called after display.set_mode so convert() works correctly). 
            This is one of the only code blocks where, after consulting an AI, I copy-pasted large portions of it to save time, inspecting it & adding comments afterwards."""

            def _load_scaled(path, size=None):
                img = pygame.image.load(path).convert_alpha()
                if size:
                    return pygame.transform.smoothscale(img, size)
                return img

            #load all background images into settings as pygame objects; scale them, with reference names to be used in the main file.
            starter = pygame.image.load(self.settings.starter_bg_path).convert()
            self.bg_starter = pygame.transform.scale(starter, (self.settings.screen_width, self.settings.screen_height))

            bg_3_4 = pygame.image.load(self.settings._3to4_bg_path).convert()
            self.bg_3to4 = pygame.transform.scale(bg_3_4, (self.settings.screen_width, self.settings.screen_height))

            bg_5_6 = pygame.image.load(self.settings._5to6_bg_path).convert()
            self.bg_5to6 = pygame.transform.scale(bg_5_6, (self.settings.screen_width, self.settings.screen_height))

            bg_7_8 = pygame.image.load(self.settings._7to8_bg_path).convert()
            self.bg_7to8 = pygame.transform.scale(bg_7_8, (self.settings.screen_width, self.settings.screen_height))

            bg_9_10 = pygame.image.load(self.settings._9to10_bg_path).convert()
            self.bg_9to10 = pygame.transform.scale(bg_9_10, (self.settings.screen_width, self.settings.screen_height))

            # Defeat / Victory
            defeat = pygame.image.load(self.settings.defeat_screen).convert()
            self.bg_defeat = pygame.transform.scale(defeat, (self.settings.screen_width, self.settings.screen_height))

            victory = pygame.image.load(self.settings.victory_screen).convert()
            self.bg_victory = pygame.transform.scale(victory, (self.settings.screen_width, self.settings.screen_height))

            # Bonus wave backgrounds
            bonus_wave_bg = pygame.image.load(self.settings.bonus_wave_bg_path).convert()
            self.bg_bonus_wave = pygame.transform.scale(bonus_wave_bg, (self.settings.screen_width, self.settings.screen_height))
            
            nyancat_bg = pygame.image.load(self.settings.nyancat_bg_path).convert()
            self.bg_nyancat = pygame.transform.scale(nyancat_bg, (self.settings.screen_width, self.settings.screen_height))

            # Core alien sprites (already scaled for current multiplayer_resizer)
            self.settings.alien_images = {
                1: _load_scaled(self.settings.alien_sprite_paths[1], self.alien1_spritedim),
                2: _load_scaled(self.settings.alien_sprite_paths[2], self.alien2_spritedim),
                3: _load_scaled(self.settings.alien_sprite_paths[3], self.alien3_spritedim),
                4: _load_scaled(self.settings.alien_sprite_paths[4], self.alien4_spritedim),
                5: _load_scaled(self.settings.alien_sprite_paths[5], self.destroyer_spritedim),
                6: _load_scaled(self.settings.alien_sprite_paths[6], self.cruiser_spritedim),
                7: _load_scaled(self.settings.alien_sprite_paths[7], self.laztanker_spritedim),
                # 8: _load_scaled(self.alien_sprite_paths[8], self.gunship_spritesize),
                # interceptors
                #boss
            }

            # Damage frames are preloaded & scaled once so aliens can just swap surfaces when hit.
            self.settings.destroyer_hitframes = [
                _load_scaled(path, self.destroyer_spritedim) for path in self.settings.destroyer_hitframe_paths
            ]
            self.settings.cruiser_hitframes = [
                _load_scaled(path, self.cruiser_spritedim) for path in self.settings.cruiser_hitframe_paths
            ]
            self.settings.laztanker_hitframes = [
                _load_scaled(path, self.laztanker_spritedim) for path in self.settings.laztanker_hitframe_paths
            ]
            #self.gunship_hitframes = [
            #    _load_scaled(path) for path in self.gunship_hitframe_paths
            #]
                

    def _run_menu(self):   #briefly pre-define the run menu function for the main game loop and pause menu to use: 
            # Create wrapper functions for sound callbacks
            def play_sound(key, loop=0):
                return self.audio.play(key, loop=loop)
            
            def stop_sound(channel):
                return self.audio.stop_channel(channel)
            
            menu = MenuMain(self.screen, self.clock, self.settings, 
                          play_sound_callback=play_sound, 
                          stop_sound_callback=stop_sound)
            config = menu.run()
            return config

    def _full_game_initialization(self, config, ShipClass):
        """
        Complete game initialization function. Handles all setup required for a new game session.
        Called both at initial startup and when returning to menu to start a new game.
        """
        # Handle None config (user quit menu)
        if config is None:
            return
        
        # Apply start configuration (player count, starting wave, sprite scaling, etc.)
        self.apply_start_config(config, ShipClass)

        # Defensive: keybindings can be changed in menus before starting a new run.
        # Clear cached HUD/key surfaces so labels always reflect the current settings.
        self._hud_cache = {}
        # Reset background fade state (background surfaces may have been reloaded/rescaled)
        self._bg_last_ref = None
        self._bg_fade_active = False
        self._bg_fade_old = None
        self._bg_fade_new = None
        self._bg_fade_new_ref = None
        
        # Initialize shields if enabled
        self._init_shields_if_needed()

        # ---------- Continue full game initialization ----------
        # Set up VICTORY/DEFEAT, PLAYER DEATH/RESPAWN variables:
        # bonus wave - bonus wave uses different defense system, skip this for bonus wave
        if not self.is_bonus_wave:
            # Ensure current_wave_num is set before using it
            if self.current_wave_num is None:
                self.current_wave_num = 0  # Default to wave 0 if not set
            self.max_breach_tolerance = self.current_wave_num + 2 # the higher the level, the more breach tolerance we have.
            self.breaches_this_wave = 0 #We could have put this above in the __init__, but it seemed tidier to put it here.
            self.current_defense_strength = self.max_breach_tolerance - self.breaches_this_wave
        else:
            # bonus wave - defense strength is set in _start_bonus_wave()
            self.breaches_this_wave = 0

        # Adjust GRAPHICS size and then load sprites and screen backgrounds into the program:
        resize = self.settings.multiplayer_resizer #NOTE: THIS NUM HAS BEEN CHANGED BY gamesetup() and unless only 1p was selected, it's not what it was formerly.
        print("resizer is", resize)
        self.alien1_spritedim = (round(self.settings.alien1_spriteX * resize), round(self.settings.alien1_spriteY * resize))
        self.alien2_spritedim = (round(self.settings.alien2_spriteX * resize), round(self.settings.alien2_spriteY * resize))
        self.alien3_spritedim = (round(self.settings.alien3_spriteX * resize), round(self.settings.alien3_spriteY * resize))
        self.alien4_spritedim = (round(self.settings.alien4_spriteX * resize), round(self.settings.alien4_spriteY * resize))
        self.destroyer_spritedim = (round(self.settings.destroyer_spriteX * resize), round(self.settings.destroyer_spriteY * resize))
        self.cruiser_spritedim = (round(self.settings.cruiser_spriteX * resize), round(self.settings.cruiser_spriteY * resize))
        self.laztanker_spritedim = (round(self.settings.laztanker_spriteX * resize), round(self.settings.laztanker_spriteY * resize))
        #self.gunship_spritedim = (round(self.settings.gunship_spriteX * resize), round(self.settings.gunship_spriteY * resize))
        #self.interceptor_spritedim = etc.

        # Alien sprite sizes(scaled for multiplayer) pushed back to settings object, for alien.py to use when it generates sprites.
        self.settings.alien1_spritesize = self.alien1_spritedim
        self.settings.alien2_spritesize = self.alien2_spritedim
        self.settings.alien3_spritesize = self.alien3_spritedim
        self.settings.alien4_spritesize = self.alien4_spritedim
        self.settings.destroyer_spritesize = self.destroyer_spritedim
        self.settings.cruiser_spritesize = self.cruiser_spritedim
        self.settings.laztanker_spritesize = self.laztanker_spritedim
       #settings for gunship
       #settings for interceptors

        #Alien Damage Graphics:
        self.settings.alien_bullet_width = round(self._base_alien_bullet_width * resize)
        self.settings.alien_bullet_height = round(self._base_alien_bullet_height * resize)
        self.settings.destroyer_bullet_width = round(self._base_destroyer_bullet_width * resize)
        self.settings.destroyer_bullet_height = round(self._base_destroyer_bullet_height * resize)
        self.settings.cruiser_bullet_width = round(self._base_cruiser_bullet_width * resize)
        self.settings.cruiser_bullet_height = round(self._base_cruiser_bullet_height * resize)
        self.settings.laztanker_bullet_width = max(2, round(self._base_laztanker_bullet_width * resize))
        self.settings.laztanker_bullet_height = round(self._base_laztanker_bullet_height * resize)
        self.settings.boss_bullet_width = round(self._base_boss_bullet_width * resize)
        self.settings.boss_bullet_height = round(self._base_boss_bullet_height * resize)
       #self.settings.gunship_bullet_width
       # self.settings.gunship_bullet_width
       # self.settings.interceptor_bullet_width
       # self.settings.interceptor_bullet_height

        # Load all the sounds to pygame.mixer objects, and images to pygame surfaces for quicker rendering.
        self._load_images()
        # Sounds are loaded during __init__ via AudioManager.

        # Set the wave index correctly, ready a new wave, now that the gamesetup() function has gotten everything ready:
        # Skip _new_alien_wave for bonus wave (it has its own initialization)
        if not self.is_bonus_wave:
            self._new_alien_wave(self.current_wave_num)

        # NOW start countdown timer after all initialization is complete
        # This ensures the countdown is visible from the first frame
        self.game_state = "countdown"
        self.countdown_start_time = pygame.time.get_ticks()
        # Play countdown sound synchronized with "3" display
        self.audio.play("countdown")

    def _blit_background_with_fade(self, desired_bg):
        """
        Draw background with an optional crossfade when the wave-based background changes.\n
        Intentionally does NOT apply to defeat/victory/bonus-wave backgrounds unless enabled later.
        """
        if desired_bg is None:
            return

        # Crossfade rules:
        # - Always allow fade for defeat/victory transitions (these are true background swaps).
        # - For non-bonus normal gameplay, allow fade on wave-based swaps.
        # - Keep bonus-wave in-wave backgrounds (bonus/nyancat) snap-only for now.
        fade_enabled = bool(getattr(self.settings, "bg_fade_enabled", True))
        duration_ms = int(getattr(self.settings, "bg_fade_duration_ms", 800))
        allow_fade = False
        if fade_enabled and duration_ms > 0:
            if self.game_state in ("defeat", "victory"):
                allow_fade = True
            elif not self.is_bonus_wave:
                allow_fade = True

        # If a fade is active, continue it (even if desired_bg changed again, we snap to the latest)
        if self._bg_fade_active and self._bg_fade_old is not None and self._bg_fade_new is not None:
            now = pygame.time.get_ticks()
            t = (now - self._bg_fade_start_ms) / float(max(1, self._bg_fade_duration_ms))
            if t >= 1.0:
                self._bg_fade_active = False
                self._bg_last_ref = self._bg_fade_new_ref
                self._bg_fade_old = None
                self._bg_fade_new = None
                self._bg_fade_new_ref = None
                self.screen.blit(desired_bg, (0, 0))
                return

            old_alpha = int(255 * (1.0 - max(0.0, min(1.0, t))))
            new_alpha = int(255 * max(0.0, min(1.0, t)))
            self._bg_fade_old.set_alpha(old_alpha)
            self._bg_fade_new.set_alpha(new_alpha)
            self.screen.blit(self._bg_fade_old, (0, 0))
            self.screen.blit(self._bg_fade_new, (0, 0))
            return

        # Start a new fade if background changed
        if allow_fade and self._bg_last_ref is not None and desired_bg is not self._bg_last_ref:
            self._bg_fade_active = True
            self._bg_fade_start_ms = pygame.time.get_ticks()
            self._bg_fade_duration_ms = duration_ms
            # Use copies so we don't mutate the original background surfaces' alpha
            self._bg_fade_old = self._bg_last_ref.copy()
            self._bg_fade_new = desired_bg.copy()
            self._bg_fade_new_ref = desired_bg
            self._bg_fade_old.set_alpha(255)
            self._bg_fade_new.set_alpha(0)
            self.screen.blit(self._bg_fade_old, (0, 0))
            self.screen.blit(self._bg_fade_new, (0, 0))
            return

        # Default: no fade
        self.screen.blit(desired_bg, (0, 0))
        self._bg_last_ref = desired_bg
        return


#************************DEFINE THE MAIN GAME LOOP***********************************


    def Main_Game_Loop(self):
        """This is the Main Game Loop."""

#STEP 1: SETUP FOR THE MAIN GAME LOOP:

    #starting with the menu screens:  
        if self.game_state == "start_menu":
            setup = self._run_menu() #run the menu, and store all its output in the "setup" variable   
       
        # Perform full game initialization with the menu configuration
        self._full_game_initialization(setup, Ship)



#STEP 2: 
#-------and now the main code of the MAIN GAME LOOP:-------------------------------------------#
        while True: # this means the event loop is always running. It will be what the program uses to watch for keyboard input and other game changes.
            # Handle menu state - menu manages its own drawing and events
            if self.game_state == "start_menu":
                config = self._run_menu()
                if config is None:
                    pygame.quit()
                    sys.exit()
                # Perform full game initialization with the menu configuration
                self._full_game_initialization(config, Ship)
            else:
                self._check_keystroke_events() # reads player input from the pygame.event.get() function, and sets booleans for movement, firing, etc
                self._update_game() # moves ship and game elements based on booleans -
                self._draw_screen() # draws the result
                self.clock.tick(60) # keeps the clock created above ticking 60 times per second.

    #define all helper functions referenced above in the main loop:

#------KEYSTROKE EVENT FUNCTION----------------------
    def _check_keystroke_events(self):
        """helper function for Main_Game_Loop() that checks for keystrokes for the main game loop"""
        for event in pygame.event.get(): # this is the event loop, which moves the game along by using the pygame 'get' function for the pygame 'event' class.
            if event.type == pygame.QUIT: #his if loop is to correlate closing window with the pygame event type 'quit'.
                sys.exit()
            #these elifs direct the _check_event function to its own helper functions, _check_keydown_events and _check_keyup_events.
            elif event.type == pygame.KEYDOWN:
                #first check if need to pause (can only pause during gameplay):
                if event.key == pygame.K_ESCAPE:
                    # Only allow pausing during gameplay states (not during menus)
                    gameplay_states = ("playing", "defeat", "victory", "between_waves", "countdown")
                    if self.game_state in gameplay_states:
                        if self.game_state == "paused":
                            # Reset pause menu state when resuming
                            self.pause_menu_selection = 0
                            self.pause_menu_confirming_quit = False
                            self.pause_menu_quit_selection = 0
                            self.pause_info_selection = -1
                            self.game_state = self._previous_game_state  # Restore previous state
                        else:
                            self._previous_game_state = self.game_state  # Save current state
                            self.game_state = "paused"
                        continue  # Don't process other keys when toggling pause

                # Handle pause menu navigation
                if self.game_state == "paused":
                    if self.pause_menu_confirming_quit:
                        # Quit confirmation dialog
                        if event.key in (pygame.K_LEFT, pygame.K_a):
                            self.pause_menu_quit_selection = 0  # No
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            self.pause_menu_quit_selection = 1  # Yes
                        elif event.key == pygame.K_RETURN:
                            if self.pause_menu_quit_selection == 0:  # No
                                self.pause_menu_confirming_quit = False
                            else:  # Yes - quit to main menu
                                self._reset_game_to_main_menu()
                        continue
                    else:
                        # Main pause menu
                        # Handle UP/DOWN for info items navigation
                        if event.key in (pygame.K_UP, pygame.K_w):
                            if self.pause_info_selection == -1:
                                # Start navigating info items (Sound is index 0)
                                self.pause_info_selection = 0
                                self.audio.play("menu_selection_change")
                            else:
                                # Cycle through info items (currently only Sound at index 0)
                                self.pause_info_selection = 0
                                self.audio.play("menu_selection_change")
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            if self.pause_info_selection >= 0:
                                # Exit info items navigation, return to Resume/Quit
                                self.pause_info_selection = -1
                                self.audio.play("menu_selection_change")
                        
                        # Handle LEFT/RIGHT based on what's selected
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            if self.pause_info_selection == 0:  # Sound selected
                                # Toggle sound OFF
                                self.settings.sounds_enabled = False
                                # Stop all currently playing sounds
                                self.audio.stop_all()
                                # Also stop tracked channels
                                for channel in list(self.audio.active_sound_channels.keys()):
                                    if channel:
                                        channel.stop()
                                self.audio.active_sound_channels.clear()
                                # Stop lasertanker firing sounds
                                for alien, channel in list(self.audio.lasertanker_firing_sound_channels.items()):
                                    if channel:
                                        channel.stop()
                                self.audio.lasertanker_firing_sound_channels.clear()
                            elif self.pause_info_selection == -1:  # Resume/Quit active
                                self.pause_menu_selection = 0  # Resume
                                self.audio.play("menu_selection_change")
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            if self.pause_info_selection == 0:  # Sound selected
                                # Toggle sound ON
                                self.settings.sounds_enabled = True
                            elif self.pause_info_selection == -1:  # Resume/Quit active
                                self.pause_menu_selection = 1  # Quit
                                self.audio.play("menu_selection_change")
                        elif event.key == pygame.K_RETURN:
                            if self.pause_info_selection == -1:  # Resume/Quit active
                                self.audio.play("menu_selection_confirm")
                                if self.pause_menu_selection == 0:  # Resume
                                    self.pause_menu_selection = 0
                                    self.pause_menu_confirming_quit = False
                                    self.pause_menu_quit_selection = 0
                                    self.pause_info_selection = -1
                                    self.game_state = self._previous_game_state
                                else:  # Quit confirmation
                                    self.pause_menu_confirming_quit = True
                            # If info item selected, ENTER does nothing (use LEFT/RIGHT to toggle)
                        continue
                # Don't process game keys during pause or countdown
                if self.game_state not in ("paused", "countdown"):
                    self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event): #
        """helper function for _check_keystroke_events(): checks player keys that ARE pressed; update movement & firing booleans for each ship accordingly"""
        
        for ship in self.players: # for each ship sprite in the self.players group created above at line 25, check to see if any key-press events match its player's keystrokes:
            keys = ship.keys # the keys variable will equal the .keys attribute of the ship under iteration.
            #the following ifs and elifs say:  for that ship's movement (as defined in the settings and referenced in the imported Ship class)-->
            #--> is pushed, 
            if event.key == keys["left"]:#if a key event matches the dictionary entry in the "keys" dictionary
                ship.moving_left = True #then change the boolean for the ship.moving<direction> attribute of that Ship to True.
            if event.key == keys["right"]:
                ship.moving_right = True
            if event.key == keys["up"]:
                ship.moving_up = True
            if event.key == keys["down"]:
                ship.moving_down = True
            if event.key == keys["fire"]:
                # Allow firing during normal-mode victory (for cosmetic fireworks)
                if self.game_state != "victory" or (self.game_state == "victory" and not self.is_bonus_wave):
                    ship.firing = True
            if event.key == keys["squadron"]:
                # Allow summoning squadrons during normal-mode victory (so they can fire fireworks too).
                # Keep other powerups disabled during victory.
                if self.is_bonus_wave:
                    if self.game_state != "victory":
                        self._use_powerup(ship, "dad")  # bonus wave - dad uses squadron key
                else:
                    if self.game_state != "victory" or getattr(self, "victory_fireworks_active", False):
                        self._use_powerup(ship, "squadron")
            if event.key == keys["nanites"]:
                # Disable powerups during victory
                if self.game_state != "victory":
                    if self.is_bonus_wave:
                        self._use_powerup(ship, "mom")  # bonus wave - mom uses nanite key
                    else:
                        self._use_powerup(ship, "nanites")
            if event.key == keys["shockwave"]:
                # Disable powerups during victory
                if self.game_state != "victory":
                    self._use_powerup(ship, "shockwave")
                #self._fire_player_bullet(ship) #if the fire key is pressed, then run the helper function _fire_player_bullet and pass it the ship as its ship parameter..

            # Later: powerup keys go here
            # if event.key == keys["powerup here"]:
            #     self._fire_powerup(ship)
            # etc.

        # Handle lifepod input (same controls as the dead player)
        for lifepod in self.lifepods:
            # Get the keys for this lifepod's player
            lifepod_keys = getattr(self.settings, f"player{lifepod.player_id}_keys")
            if event.key == lifepod_keys["left"]:
                lifepod.moving_left = True
            if event.key == lifepod_keys["right"]:
                lifepod.moving_right = True
            if event.key == lifepod_keys["up"]:
                lifepod.moving_up = True
            if event.key == lifepod_keys["down"]:
                lifepod.moving_down = True
            if event.key == lifepod_keys["fire"]:
                # Allow firing during normal-mode victory (for cosmetic fireworks)
                if self.game_state != "victory" or (self.game_state == "victory" and not self.is_bonus_wave):
                    lifepod.firing = True
    def _fire_player_bullet(self, ship): 
                    """helper function for _check_keydown_events() to fire player bullets."""
                    if ship.player_state != "alive":
                        return
                    
                    self.ship = ship #pass the ship parameter to a variable in the scope of this helper function
                    
                    bullet_count = [] # Initialize an empty list to count bullets: 

                    #Next, the for loop to count bullets (exclude squadron bullets):
                    for b in self.player_bullets: #for every sprite found in the player_bullets group 
                        if b.owner_ref is ship and getattr(b, "squadron_ref", None) is None: #if its owner parameter is the ship in question AND it's not a squadron bullet
                            bullet_count.append(b)
                    
                    # after player fires, resolve any of its squadrons that need to fire:
                    squadron_fired = False  # Track if any squadron fired to play sound only once
                    for s in self.squadrons.sprites():
                        if s.owner is ship:
                            fireworks_group = None
                            if self.game_state == "victory" and not self.is_bonus_wave and getattr(self, "victory_fireworks_active", False):
                                fireworks_group = self.victory_fireworks
                            if s.try_fire(self.player_bullets, fireworks_group=fireworks_group):  # Returns True if fired
                                squadron_fired = True  # Mark that a squadron fired
                    if squadron_fired:
                        # Victory screens: suppress firing sounds (fireworks are cosmetic)
                        if self.game_state != "victory":
                            self.audio.play("squadron_shot")  # Play sound once per player fire event, even if multiple squadrons fired


                    #to allow for ship level to affect max bullets, call values from base_settings
                    """ I used to have a bunch of if statements to parse this (if player_level == 1, etc);  
                    # but I knew there had to be a simpler way, so I described a concept of an iterable variable name lookup to an AI, 
                    # and it explained dynamic attribute lookups to me, which is what I chose to use for this section."""                    
                    #Note: SPEED IS CHANGED IN ship.py update() function, also using getattr.
                    level = ship.player_level
                    max_bullets = getattr(self.settings, f"lvl{level}_bullet_max", 0)
                    
                    #finally, an if statement to enforce the max bullet cap:
                    if len(bullet_count) >= max_bullets: #if the sprite under iteration has its proper max bullets attributed to it:
                        return #limit the function to not fire another bullet, but end here.
                    
                    #otherwise:
                    if self.game_state == "victory" and not self.is_bonus_wave and getattr(self, "victory_fireworks_active", False):
                        bullet = VictoryFireworkShell(
                            settings=self.settings,
                            screen=self.screen,
                            x=ship.rect.centerx,
                            y=ship.rect.top,
                            fireworks_group=self.victory_fireworks,
                            owner_ref=ship
                        )
                    else:
                        bullet = Bullet( settings=self.settings, screen=self.screen, 
                                        x=ship.rect.centerx, y=ship.rect.top, direction=-1,
                                        owner_type="player", owner_level=ship.player_level, owner_ref=ship) #create a bullet object and pass it the right parameters
                    # Play sound: player shot (has files 1-4)
                    self.player_bullets.add(bullet)#add the bullet to the player bullets sprite Group
                    # Victory screens: suppress firing sounds (fireworks are cosmetic)
                    if self.game_state != "victory":
                        self.audio.play("player_shot")
                    # Track bullet fired
                    if ship.player_id in self.player_stats:
                        self.player_stats[ship.player_id]['bullets_fired'] += 1

    def _fire_lifepod_bullet(self, lifepod):
        """Fire a bullet from a lifepod (same properties as player bullets)."""
        if self.game_state == "victory" and not self.is_bonus_wave and getattr(self, "victory_fireworks_active", False):
            bullet = VictoryFireworkShellSmall(
                settings=self.settings,
                screen=self.screen,
                x=lifepod.rect.centerx,
                y=lifepod.rect.top,
                fireworks_group=self.victory_fireworks,
                owner_ref=lifepod
            )
        else:
            bullet = Bullet(settings=self.settings, screen=self.screen,
                           x=lifepod.rect.centerx, y=lifepod.rect.top, direction=-1,
                           owner_type="player", owner_level=1, owner_ref=lifepod)  # Use level 1, reference lifepod
        self.player_bullets.add(bullet)
        # Victory screens: suppress firing sounds (fireworks are cosmetic)
        if self.game_state != "victory":
            self.audio.play("lifepod_shot")
        # Track bullet fired (lifepod bullets are tracked under the lifepod's tracked player)
        if hasattr(lifepod, 'tracked_player') and lifepod.tracked_player:
            player_id = lifepod.tracked_player.player_id
            if player_id in self.player_stats:
                self.player_stats[player_id]['bullets_fired'] += 1

    def _use_powerup(self, ship, ptype: str):
        if ship.powerups.get(ptype, 0) <= 0:
            return

        # Respect OPTIONS toggles
        if ptype == "squadron" and not self.settings.powerup_enable_squadron:
            return
        if ptype == "nanites" and not self.settings.powerup_enable_nanites:
            return
        if ptype == "shockwave" and not self.settings.powerup_enable_shockwave:
            return

        if ptype == "squadron":
            # Check current squadron count
            have_left = bool(ship.squadron_left and ship.squadron_left.alive())
            have_right = bool(ship.squadron_right and ship.squadron_right.alive())
            have_front = bool(getattr(ship, 'squadron_front', None) and getattr(ship, 'squadron_front', None).alive())
            have_back = bool(getattr(ship, 'squadron_back', None) and getattr(ship, 'squadron_back', None).alive())

            # In Hard mode, allow up to 4 squadrons; otherwise max 2
            is_hard = getattr(self.settings, "difficulty_mode", "easy").lower() == "hard"
            max_squadrons = 4 if is_hard else 2

            current_count = sum([have_left, have_right, have_front, have_back])
            if current_count >= max_squadrons:
                return

            # Spend inventory only if we successfully spawn one
            if not have_right:
                s = SquadronShip(self.settings, self.screen, ship, side="right")
                self.squadrons.add(s)
                ship.squadron_right = s
                ship.powerups["squadron"] -= 1
                ship.powerups_used["squadron"] += 1
                self.audio.play("powerup_squadron_hello")
                return
            if not have_left:
                s = SquadronShip(self.settings, self.screen, ship, side="left")
                self.squadrons.add(s)
                ship.squadron_left = s
                ship.powerups["squadron"] -= 1
                ship.powerups_used["squadron"] += 1
                self.audio.play("powerup_squadron_hello")
                return
            # In Hard mode, allow third squadron in front
            if is_hard and not have_front:
                s = SquadronShip(self.settings, self.screen, ship, side="front")
                self.squadrons.add(s)
                ship.squadron_front = s
                ship.powerups["squadron"] -= 1
                ship.powerups_used["squadron"] += 1
                self.audio.play("powerup_squadron_hello")
                return
            # In Hard mode, allow fourth squadron behind player
            if is_hard and not have_back:
                s = SquadronShip(self.settings, self.screen, ship, side="back")
                self.squadrons.add(s)
                ship.squadron_back = s
                ship.powerups["squadron"] -= 1
                ship.powerups_used["squadron"] += 1
                self.audio.play("powerup_squadron_hello")  # Play helper fighter hello sound
                return

        elif ptype == "shockwave":
            sw = Shockwave(self.settings, self.screen, ship)
            self.shockwaves.add(sw)
            ship.powerups["shockwave"] -= 1
            ship.powerups_used["shockwave"] += 1
            self.audio.play("powerup_shockwave")  # Play shockwave sound

        elif ptype == "nanites":
            # One for each player + one for each shield slot (including downed)
            # Assumes you maintain:
            #   self.shields (Group) AND self.shield_slots (list[pygame.Rect])
            ship.powerups["nanites"] -= 1
            self.audio.play("powerup_nanites")  # Play nanites sound

            # Players
            for p in self.players:
                if p.needs_heal:
                    target = p
                    for anchor in ("ship_top_left", "ship_top_right"):
                        n = Nanite(self.settings, self.screen, target, heal_fn=lambda amt, t=target: t.heal(amt), anchor=anchor)
                        self.nanites.add(n)
            ship.powerups_used["nanites"] += 1

            # Squadrons: 1 nanite per live squadron (always, regardless of current hp)
            for squadron in self.squadrons.sprites():
                if not squadron.alive():
                    continue
                n = Nanite(
                    self.settings,
                    self.screen,
                    squadron,
                    heal_fn=lambda amt, t=squadron: (t.heal(amt) if t.alive() else None),
                    anchor="top_center",
                )
                self.nanites.add(n)

            # Shields: ensure shield exists in each slot; then heal it
            if not hasattr(self, 'shield_slots') or not self.shield_slots:
                return  # shields not initialized yet
            for slot_rect in self.shield_slots:
                shield = None
                for s in self.shields.sprites():
                    if s.rect.topleft == slot_rect.topleft:
                        shield = s
                        break
                if shield is None:
                    shield = Shield(self.settings, slot_rect)
                    self.shields.add(shield)

                for anchor in ("top_left", "top_center", "top_right"):
                    # Revive-on-pulse: if a stationary shield gets killed while nanites are in-flight,
                    # re-add the same Shield instance back into self.shields on the next pulse before healing.
                    def _shield_heal_fn(amt, t=shield, shields_group=self.shields):
                        if not t.alive():
                            shields_group.add(t)
                        return t.heal(amt)

                    n = Nanite(self.settings, self.screen, shield, heal_fn=_shield_heal_fn, anchor=anchor)
                    self.nanites.add(n)

        # Bonus wave powerups
        elif ptype == "dad":
            # Start first dad ship run
            dad_ship = DadShip(self.settings, self.screen, run_number=0)
            self.dad_ships.add(dad_ship)
            self._dad_run_number = 0  # Track which run we're on
            ship.powerups["dad"] -= 1
            ship.powerups_used["dad"] = ship.powerups_used.get("dad", 0) + 1

        elif ptype == "mom":
            # Mom powerup effects: spawn mom ship
            # Mom bullets will create shields at empty slots (at max damage) and charge existing shields
            # Spawn mom ship (original functionality - bolts now heal players and charge shields)
            # Pass shield_slots so mom ship can fire at stationary shields
            shield_slots = getattr(self, 'shield_slots', []) if self.settings.orbital_shields_enabled else []
            mom_ship = MomShip(self.settings, self.screen, self.players, shield_slots)
            self.mom_ships.add(mom_ship)
            ship.powerups["mom"] -= 1
            ship.powerups_used["mom"] = ship.powerups_used.get("mom", 0) + 1



    def _check_keyup_events(self, event):
        """helper function to for _check_keystroke_events() - checks for keys NOT pressed; sets applicable motion booleans to false"""
        for ship in self.players:
            keys = ship.keys
            if event.key == keys["left"]:
                ship.moving_left = False
            if event.key == keys["right"]:
                ship.moving_right = False
            if event.key == keys["up"]:
                ship.moving_up = False
            if event.key == keys["down"]:
                ship.moving_down = False
            if event.key == keys["fire"]:
                 ship.firing = False

        # Handle lifepod key up events
        for lifepod in self.lifepods:
            # Get the keys for this lifepod's player
            lifepod_keys = getattr(self.settings, f"player{lifepod.player_id}_keys")
            if event.key == lifepod_keys["left"]:
                lifepod.moving_left = False
            if event.key == lifepod_keys["right"]:
                lifepod.moving_right = False
            if event.key == lifepod_keys["up"]:
                lifepod.moving_up = False
            if event.key == lifepod_keys["down"]:
                lifepod.moving_down = False
            if event.key == lifepod_keys["fire"]:
                lifepod.firing = False
    
#------GAME UPDATE FUNCTION:-----------------------     
    def _update_game(self):
        """helper function for Main_Game_Loop() to update player and alien sprites and bullets, & check wave state.  """
        

        if self.game_state == "paused":
                # Don't update game when paused
                return

        if self.game_state == "start_menu":
                # Don't update game when in start menu
                return
        
        # Handle countdown timer
        if self.game_state == "countdown":
            self._update_countdown()
            return

          
        # Handle defeat/victory screens first (for both normal and bonus wave)
        if self.game_state == "defeat":
            self.aliens.update()
            self.minions.update()
            self.player_bullets.update()
            self.alien_bullets.update()
            self._update_defeat_victory_screens()
            return
    
        if self.game_state == "victory":
            # Bonus-wave victory (if ever used): keep previous behavior.
            if self.is_bonus_wave:
                self.players.update()  # Allow player movement only
                self._update_defeat_victory_screens()
                return

            # Normal-mode victory: allow movement + cosmetic fireworks firing; skip gameplay collisions/scoring.
            now = pygame.time.get_ticks()
            self.players.update()
            self.squadrons.update()
            self.lifepods.update()

            # Player firing (creates fireworks while in victory state)
            for ship in self.players:
                if ship.firing and now >= getattr(ship, "next_fire_time", 0):
                    self._fire_player_bullet(ship)
                    if ship.player_level == 11:
                        ship.next_fire_time = now + self.settings.lvl11_fire_speed
                    else:
                        ship.next_fire_time = now + self.settings.player_fire_speed

            # Lifepod firing during victory: cap at 1 bullet at a time; fireworks use small shell
            lifepod_bullet_counts = {}
            for bullet in self.player_bullets:
                if hasattr(bullet, 'owner_ref') and bullet.owner_ref in self.lifepods:
                    lifepod = bullet.owner_ref
                    lifepod_bullet_counts[lifepod] = lifepod_bullet_counts.get(lifepod, 0) + 1

            for lifepod in self.lifepods:
                if lifepod.firing and lifepod.state == "normal":
                    if lifepod_bullet_counts.get(lifepod, 0) < 1:
                        if now >= getattr(lifepod, "next_fire_time", 0):
                            self._fire_lifepod_bullet(lifepod)
                            lifepod.next_fire_time = now + self.settings.player_fire_speed

            # Update bullets and cosmetic spark blooms
            self.player_bullets.update()
            self.victory_fireworks.update()

            self._update_defeat_victory_screens()
            return

        # Track time in top 33% of screen for each player (Power Forward award)
        # Note: stored under historical key name 'time_in_top_30_percent' for credits compatibility.
        if self.game_state == "playing":
            top_33_percent_y = self.settings.play_height * 0.33
            frame_time_ms = self.clock.get_time()
            for player in self.players.sprites():
                if player.player_state == "alive" and player.player_id in self.player_stats:
                    if player.rect.top <= top_33_percent_y:
                        self.player_stats[player.player_id]["time_in_top_30_percent"] += frame_time_ms

        now = pygame.time.get_ticks()
        # Lifepod firing (works in both normal and bonus wave modes)
        # Count all lifepod bullets once per frame (more efficient than counting per lifepod)
        lifepod_bullet_counts = {}
        for bullet in self.player_bullets:
            if hasattr(bullet, 'owner_ref') and bullet.owner_ref in self.lifepods:
                lifepod = bullet.owner_ref
                lifepod_bullet_counts[lifepod] = lifepod_bullet_counts.get(lifepod, 0) + 1
        
        for lifepod in self.lifepods:
          if lifepod.firing and lifepod.state == "normal":
              # Get bullet count from pre-calculated dictionary
              lifepod_bullet_count = lifepod_bullet_counts.get(lifepod, 0)
              if lifepod_bullet_count < 2:  # Max 2 bullets
                  # Check firing rate timing
                  if now >= getattr(lifepod, "next_fire_time", 0):
                      self._fire_lifepod_bullet(lifepod)
                      lifepod.next_fire_time = now + self.settings.player_fire_speed

        # Bonus wave mode #bonus wave - handle bonus wave updates separately
        if self.is_bonus_wave:
            self._update_bonus_wave()
            return

      # Normal game logic (not bonus wave)
        if self.game_state == "between_waves":
            self.players.update()
            self.player_bullets.update()
            self.alien_bullets.update()
            self.shields.update()  # let shields regen while waiting between waves
            # Keep powerup sprites moving during between waves
            self.squadrons.update()
            self.nanites.update()
            self.shockwaves.update()
            self.powerups.update()  # powerup pickups should continue drifting
            # Allow players to grab powerups between waves
            # Determine inventory cap based on difficulty (Hard mode: 6, others: 3)
            is_hard = getattr(self.settings, "difficulty_mode", "easy").lower() == "hard"
            max_inventory = 6 if is_hard else 3
            for ship in self.players:
                if ship.player_state == "alive":  # Only alive players can grab powerups
                    # Only collide with powerups if inventory not full
                    grabs = pygame.sprite.spritecollide(ship, self.powerups, dokill=False)
                    for powerup in grabs:
                        ptype = getattr(powerup, 'ptype', None)
                        if ptype:
                            current_count = ship.powerups.get(ptype, 0)
                            if current_count < max_inventory:  # Inventory cap: max 6 in Hard mode, 3 otherwise
                                ship.powerups[ptype] = current_count + 1
                                ship.trigger_powerup_flash(ptype, duration_ms=900)
                                powerup.kill()  # Remove powerup only if picked up
            self._update_between_waves()
            return
        #Rest of instructions in this function are for normal gameplay. First, check for aliens that need to be spawned, whether rows or individuals
        self._update_wave_spawning()
        #functions for moving player sprites:
        self.players.update()
        self.lifepods.update()
        self.squadrons.update()
        self.nanites.update()
        self.shockwaves.update()

        for sw in self.shockwaves.sprites():
            # Get collisions, then filter for cruisers
            hits = pygame.sprite.spritecollide(sw, self.aliens, dokill=False)
            for alien in hits:
                # Skip if this shockwave has already hit this alien
                if alien in sw.hit_aliens:
                    continue

                lvl = getattr(alien, "level", 1)
                if lvl <= self.settings.shockwave_kill_max_alien_level:
                        # Instakill level 1-4 aliens (no cruiser collision check needed - cruisers are level 6)
                        # Play death sound based on alien level
                        #if lvl in (1, 2, 3): #this is currently commented out to see if sound works better this way. If you comment it back in, the if statement below for level 4 aliens has to be changed back to an 
                            #self.audio.play("alien_lvl1to3_death")  # Levels 1-3 killed by shockwave
                        if lvl == 4:
                            self.audio.play("alien_lvl1to3_death")  # Level 4 killed by shockwave (not collision)
                            # Stop level 4 hum sound if this alien was playing it
                            if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                                alien.hum_sound_channel.stop()
                                alien.hum_sound_channel = None
                        
                        # Award points to shockwave owner (skip lifepods - they don't earn score)
                        if hasattr(sw, 'owner') and sw.owner and hasattr(sw.owner, 'player_score'):
                            sw.owner.player_score += alien.level * ((alien.level * 1/2) * 20)
                            # Track enemy destroyed by shockwave
                            if hasattr(sw.owner, 'player_id') and sw.owner.player_id in self.player_stats:
                                self.player_stats[sw.owner.player_id]['enemies_destroyed'] += 1
                        
                        alien.kill()
                        self._maybe_spawn_powerup_from_alien(alien)
                        sw.hit_aliens.add(alien)  # Mark as hit (though alien is now dead)
                elif lvl in (5, 6, 7):  # Level 5-7: deal fixed damage
                        # For cruisers, check if collision is valid (not in wing top area)
                        if alien.level == 6:
                            if not self._cruiser_collision_valid(alien, sw.rect):
                                continue  # Skip this collision
                        # For destroyers, exclude front-half outer quarters
                        if alien.level == 5:
                            if not self._destroyer_collision_valid(alien, sw.rect):
                                continue  # Skip this collision

                        # Mark as hit before applying damage to prevent multiple hits
                        sw.hit_aliens.add(alien)

                        # Apply shockwave damage
                        alien.damage_stage += self.settings.shockwave_damage_amount

                        # Get damage frames for this alien type
                        if alien.level == 5:
                            frames = self.settings.destroyer_hitframes
                        elif alien.level == 6:
                            frames = self.settings.cruiser_hitframes
                        elif alien.level == 7:
                            frames = self.settings.laztanker_hitframes
                        else:
                            frames = None

                        # Check if alien is destroyed
                        if frames and alien.damage_stage > len(frames):
                            # Alien is destroyed - create death animation
                            if alien.level == 7:
                                death_anim = LazertankerDeathAnimation(
                                    self.settings,
                                    self.screen,
                                    alien.rect.center,
                                    alien.rect.size
                                )
                                self.lazertanker_death_animations.add(death_anim)
                            elif alien.level == 6:
                                death_anim = CruiserDeathAnimation(
                                    self.settings,
                                    self.screen,
                                    alien.rect.center,
                                    alien.rect.size
                                )
                                self.cruiser_death_animations.add(death_anim)
                            elif alien.level == 5:
                                death_anim = DestroyerDeathAnimation(
                                    self.settings,
                                    self.screen,
                                    alien.rect.center,
                                    alien.rect.size
                                )
                                self.destroyer_death_animations.add(death_anim)
                            
                            # Stop hum sound if this alien was playing it
                            if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                                alien.hum_sound_channel.stop()
                                alien.hum_sound_channel = None
                            # Play death sound based on alien level
                            if alien.level == 5:
                                self.audio.play("alien_destroyer_death")  # Destroyer death
                            elif alien.level == 6:
                                self.audio.play("alien_cruiser_death")  # Cruiser death
                            elif alien.level == 7:
                                self.audio.play("alien_laztanker_death")  # Lasertanker death
                                # Stop lasertanker firing sound
                                if alien in self.audio.lasertanker_firing_sound_channels:
                                    channel = self.audio.lasertanker_firing_sound_channels[alien]
                                    if channel:
                                        channel.stop()
                                    del self.audio.lasertanker_firing_sound_channels[alien]
                            # Track enemy destroyed by shockwave damage
                            if hasattr(sw, 'owner') and sw.owner and hasattr(sw.owner, 'player_id'):
                                if sw.owner.player_id in self.player_stats:
                                    self.player_stats[sw.owner.player_id]['enemies_destroyed'] += 1
                            
                            alien.kill()
                            self._maybe_spawn_powerup_from_alien(alien)
                            
                            # Award points to shockwave owner
                            if hasattr(sw, 'owner') and sw.owner:
                                try:
                                    sw.owner.player_score += alien.level * ((alien.level * 1/2) * 20)
                                except (TypeError, AttributeError):
                                    pass  # Boss alien or other special case
                        elif frames and alien.damage_stage > 0:
                            # Update alien image to show damage
                            frame_index = min(alien.damage_stage - 1, len(frames) - 1)
                            alien.image = frames[frame_index]
                            alien.rect = alien.image.get_rect(center=alien.rect.center)

        self.shields.update()  # tick shield regen/damage timers
        # Check for shield regen improvements and play sound
        for shield in self.shields:
            if hasattr(shield, 'stage_improved') and shield.stage_improved:
                self.audio.play("shield_recharge")  # Play sound when shield regens and stage improves
        self.lazertanker_death_animations.update()  # Update lasertanker death animations
        self.cruiser_death_animations.update()  # Update cruiser death animations
        self.destroyer_death_animations.update()  # Update destroyer death animations
                #quick check, to enable 'hold down' fir
                # e instead of endless button mashing:
        now = pygame.time.get_ticks()
        for ship in self.players:
                if ship.firing and now >= getattr(ship, "next_fire_time", 0): #this if statement allows the loop to check after every time it updates
                                                                            #-->the players, to see if they're still holding down the firing key.
                    self._fire_player_bullet(ship)
                    if ship.player_level == 11:
                        ship.next_fire_time = now + self.settings.lvl11_fire_speed # ships at level 11 fire faster as well. 
                    else:
                        ship.next_fire_time = now + self.settings.player_fire_speed #150 ms is 
                    
                if ship.player_state == "respawning" and ship.respawn_end_time is not None:
                    if now >= ship.respawn_end_time:
                        ship.player_state = "alive"
                        self.audio.play("player_respawn")
                        ship.respawn_end_time = None 

        self.aliens.update()
        self.minions.update()
        self._handle_alien_breaches()
        self.player_bullets.update()
        self.alien_bullets.update()
        #after sprites and bullets are moved, check to see if anyone is on/past the edges, and correct:
        self._check_fleet_edges()
        # allow aliens to execute firing logic
        self._alien_firing_logic()
        self._minion_firing_logic()
        #parse collisions
        self._do_collisions()
        #update powerups
        self.powerups.update()
            #add to player inventory
        # Determine inventory cap based on difficulty (Hard mode: 6, others: 3)
        is_hard = getattr(self.settings, "difficulty_mode", "easy").lower() == "hard"
        max_inventory = 6 if is_hard else 3
        for ship in self.players:
            if ship.player_state == "alive":  # Only alive players can grab powerups
                # Only collide with powerups if inventory not full
                grabs = pygame.sprite.spritecollide(ship, self.powerups, dokill=False)
                powerup_grabbed = False  # Track if any powerup was grabbed to play sound only once
                for powerup in grabs:
                    ptype = powerup.ptype
                    current_count = ship.powerups.get(ptype, 0)
                    if current_count < max_inventory:  # Inventory cap: max 6 in Hard mode, 3 otherwise
                        ship.powerups[ptype] = current_count + 1
                        # Flash that specific inventory value in the HUD
                        ship.trigger_powerup_flash(ptype, duration_ms=900)
                        powerup_grabbed = True  # Mark that a powerup was grabbed
                        powerup.kill()  # Remove powerup only if picked up
                if powerup_grabbed:
                    self.audio.play("powerup_grab")  # Play sound once per frame, even if multiple powerups grabbed


        #If the alien sprite group is empty, and no more are needing to spawn, start a between-wave-pause
        if not self.aliens and self._current_wave_has_finished_spawning():
                self._new_wave_pause()
    
        
    def _reset_game_to_main_menu(self):
        """Reset game state and return to main menu"""
        # Reset all game state variables
        self.game_state = "start_menu"
        self._previous_game_state = "playing"
        self.pause_menu_selection = 0
        self.pause_menu_confirming_quit = False
        self.pause_menu_quit_selection = 0
        self.pause_info_selection = -1

        # Reset wave and game progress
        self.current_wave_num = None
        self.is_bonus_wave = False
        self.breaches_this_wave = 0

        # Reset wave initialization variables to safe defaults
        self.level1_rows_total = 0
        self.level1_rows_spawned = 0
        self.level1_rows_remaining = 0
        self.level2_remaining = 0
        self.level3_remaining = 0
        self.level4_remaining = 0
        self.destroyers_remaining = 0

        # Reset spawn timers to None (safe defaults)
        self.next_level1_row_time = None
        self.next_level2_spawn_time = None
        self.next_level3_spawn_time = None
        self.next_level4_spawn_time = None
        self.next_destroyer_spawn_time = None
        self.next_cruiser_spawn_time = None
        self.next_laztanker_spawn_time = None
        self.next_squadspawn = 0

        # Reset wave banner and between-wave state
        self.wave_banner_active = False
        self.wave_banner_text = ""
        self.wave_banner_x = 0.0
        self.between_wave_phase = None
        self.next_wave_start_time = None

        # Reset bonus wave variables
        self.bonus_wave_start_time = None
        self.bonus_wave_defense_strength = self.settings.bonus_wave_defense_strength

        # Reset initialization flags to allow re-initialization
        self._shields_initialized = False

        # Stop all alien hum sounds before clearing sprites
        # This includes level 4, destroyer, cruiser, and lasertanker hum sounds
        for alien in self.aliens:
            if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                alien.hum_sound_channel.stop()
                alien.hum_sound_channel = None
        # Stop all lasertanker firing sounds
        for alien, channel in list(self.audio.lasertanker_firing_sound_channels.items()):
            if channel:
                channel.stop()
        self.audio.lasertanker_firing_sound_channels.clear()
        # Stop nyancat music
        if self.audio.nyancat_music_channel:
            self.audio.stop_music_channel(self.audio.nyancat_music_channel)
            self.audio.nyancat_music_channel = None

        # Clear all sprites
        self.aliens.empty()
        self.minions.empty()
        self.player_bullets.empty()
        self.alien_bullets.empty()
        self.players.empty()
        self.shields.empty()
        self.powerups.empty()
        self.lifepods.empty()
        self.nanites.empty()
        self.squadrons.empty()
        self.shockwaves.empty()
        self.lazertanker_death_animations.empty()
        self.cruiser_death_animations.empty()
        self.destroyer_death_animations.empty()
        #self.player_death_animations.empty()

        #reset all defense variables
        self.max_breach_tolerance = 0
        self.current_defense_strength = 0
        self.breaches_this_wave = 0

        #Reset bonus wave sprites and states
        self.bonus_wave_enemies.empty()
        self.bonus_wave_fireworks.empty()
        self.dad_shockwaves.empty()
        self.dad_ships.empty()
        self.mom_ships.empty()
        self.mom_bullets.empty()
        self.player_shields.clear()
        self.next_dad_run_time = None

        #reset displays for victory/defeat:
        self.countdown_start_time = None
        self.warp_banner_end_time = None
        self.defeat_banner_x = None
        self.defeat_banner_active = False
        self.victory_banner_x = None
        self.victory_banner_active = False
        self.victory_banner_text = None
        self.credits_y = None
        self.credits_active = False
        self.thanks_active = False
        self.password_phase = None
        self.password_start_time = None
        self.final_player_snapshots = {}
        self.final_player_data = []
        
        # Reset defeat/victory music tracking
        self.defeat_screen_start_time = None
        self.victory_screen_start_time = None
        if self.audio.defeat_music_channel:
            self.audio.stop_music_channel(self.audio.defeat_music_channel)
            self.audio.defeat_music_channel = None
        if self.audio.victory_music_channel:
            self.audio.stop_music_channel(self.audio.victory_music_channel)
            self.audio.victory_music_channel = None
        
        # Reset player statistics
        self.player_stats.clear()

        # Reset player data
        for i in range(4):
            player_num = i + 1
            setattr(self, f'player{player_num}_score', 0)
            setattr(self, f'player{player_num}_level', 1)
            setattr(self, f'player{player_num}_lives', 3)

    def _draw_pause_screen(self):
        overlay = pygame.Surface((self.settings.screen_width, self.settings.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # Translucent black
        self.screen.blit(overlay, (0,0))

        # Load custom font if available
        try:
            font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf'))
            pause_title_font = pygame.font.Font(font_path, int(self.settings.screen_height * 0.14))
            pause_info_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.05))
        except:
            pause_title_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.14))
            pause_info_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.05))
        pause_info_font_italic = pygame.font.SysFont(None, int(self.settings.screen_height * 0.05), italic=True)

        # Title
        title = pause_title_font.render("PAUSED", True, (255, 255, 120))
        title_rect = title.get_rect(center=(self.settings.screen_width // 2, int(self.settings.screen_height * 0.15)))
        self.screen.blit(title, title_rect)

        y_start = int(self.settings.screen_height * 0.25)
        line_height = int(self.settings.screen_height * 0.06)
        x_left = int(self.settings.screen_width * 0.15)
        x_right = int(self.settings.screen_width * 0.65)

        # Helper to get key name
        def get_key_name(key_const):
            name = pygame.key.name(key_const).upper()
            if name == "BACKSPACE": return "BS"
            elif name == "BACKSLASH": return "\\ key"
            elif name == "RETURN": return "ENTER"
            elif name == "BACKQUOTE": return "~"
            elif name == "CAPSLOCK": return "CAPS"
            elif name.startswith("KP"): return name.replace("KP", "KP")
            return name

        def blit_segments(x: int, y: int, segments):
            """Blit (text, font, color) segments left-to-right starting at (x, y)."""
            cur_x = x
            for text, font, color in segments:
                surf = font.render(text, True, color)
                self.screen.blit(surf, (cur_x, y))
                cur_x += surf.get_width()

        # Player Key Bindings
        info_text = pause_info_font.render("Player Key Bindings:", True, (255, 255, 255))
        self.screen.blit(info_text, (x_left, y_start))
        y_start += line_height * 2

        for player_num in range(1, 5):
            if player_num > len(self.players):
                break
            keys = getattr(self.settings, f"player{player_num}_keys")
            c = (230, 230, 230)
            # Line 1: movement + fire
            blit_segments(
                x_left,
                y_start,
                [
                    (f"P{player_num}: ", pause_info_font, c),
                    ("UP:", pause_info_font_italic, c),
                    (get_key_name(keys["up"]) + "  ", pause_info_font, c),
                    ("DWN:", pause_info_font_italic, c),
                    (get_key_name(keys["down"]) + "  ", pause_info_font, c),
                    ("LFT:", pause_info_font_italic, c),
                    (get_key_name(keys["left"]) + "  ", pause_info_font, c),
                    ("RGHT:", pause_info_font_italic, c),
                    (get_key_name(keys["right"]) + "  ", pause_info_font, c),
                    ("FIRE:", pause_info_font_italic, c),
                    (get_key_name(keys["fire"]), pause_info_font, c),
                ],
            )
            y_start += int(line_height * 0.85)

            # Line 2: powerups
            blit_segments(
                x_left,
                y_start,
                [
                    ("  ", pause_info_font, c),
                    ("SQUAD:", pause_info_font_italic, c),
                    (get_key_name(keys["squadron"]) + "  ", pause_info_font, c),
                    ("NANITES:", pause_info_font_italic, c),
                    (get_key_name(keys["nanites"]) + "  ", pause_info_font, c),
                    ("SHOCK:", pause_info_font_italic, c),
                    (get_key_name(keys["shockwave"]), pause_info_font, c),
                ],
            )
            y_start += line_height

        y_start += line_height

        # Difficulty Level
        diff_name = getattr(self.settings, "difficulty_mode", "easy").capitalize()
        diff_text = pause_info_font.render(f"Difficulty Level: {diff_name}", True, (255, 255, 255))
        self.screen.blit(diff_text, (x_left, y_start))
        y_start += line_height * 2

        # Powerup Rarity
        freq_names = {"High": 0.06, "Normal": 0.022, "Rare": 0.01}
        current_chance = self.settings.powerup_drop_chance
        freq_name = "High"
        for name, chance in freq_names.items():
            if abs(current_chance - chance) < 0.001:
                freq_name = name
                break
        rarity_text = pause_info_font.render(f"Powerups: {freq_name}", True, (255, 255, 255))
        self.screen.blit(rarity_text, (x_left, y_start))
        y_start += line_height * 2

        # Powerup Toggles
        toggles_text = pause_info_font.render("Powerup Toggles:", True, (255, 255, 255))
        self.screen.blit(toggles_text, (x_left, y_start))
        y_start += line_height

        nanites_status = "ON" if self.settings.powerup_enable_nanites else "OFF"
        blit_segments(x_left, y_start, [("  ", pause_info_font, (230, 230, 230)), ("Nanites:", pause_info_font_italic, (230, 230, 230)), (" " + nanites_status, pause_info_font, (230, 230, 230))])
        y_start += line_height

        squadrons_status = "ON" if self.settings.powerup_enable_squadron else "OFF"
        blit_segments(x_left, y_start, [("  ", pause_info_font, (230, 230, 230)), ("Squadrons:", pause_info_font_italic, (230, 230, 230)), (" " + squadrons_status, pause_info_font, (230, 230, 230))])
        y_start += line_height

        shockwaves_status = "ON" if self.settings.powerup_enable_shockwave else "OFF"
        blit_segments(x_left, y_start, [("  ", pause_info_font, (230, 230, 230)), ("Shockwaves:", pause_info_font_italic, (230, 230, 230)), (" " + shockwaves_status, pause_info_font, (230, 230, 230))])
        y_start += line_height

        # Sound toggle
        sound_status = "ON" if self.settings.sounds_enabled else "OFF"
        sound_color = (255, 255, 0) if self.pause_info_selection == 0 else (230, 230, 230)
        sound_text = pause_info_font.render(f"  Sound: {sound_status}", True, sound_color)
        self.screen.blit(sound_text, (x_left, y_start))
        y_start += line_height

        # Pause menu buttons (lower right)
        button_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.04))
        button_x = int(self.settings.screen_width * 0.75)
        button_y = int(self.settings.screen_height * 0.75)

        if self.pause_menu_confirming_quit:
            # Quit confirmation dialog
            confirm_text = pause_info_font.render("Are you Sure?", True, (255, 255, 255))
            confirm_rect = confirm_text.get_rect(center=(self.settings.screen_width // 2, button_y - 30))
            self.screen.blit(confirm_text, confirm_rect)

            # Yes/No buttons
            no_color = (255, 255, 0) if self.pause_menu_quit_selection == 0 else (200, 200, 200)
            yes_color = (255, 255, 0) if self.pause_menu_quit_selection == 1 else (200, 200, 200)

            no_text = button_font.render("No", True, no_color)
            yes_text = button_font.render("Yes", True, yes_color)

            no_rect = no_text.get_rect(center=(button_x - 50, button_y))
            yes_rect = yes_text.get_rect(center=(button_x + 50, button_y))

            self.screen.blit(no_text, no_rect)
            self.screen.blit(yes_text, yes_rect)

            # Instructions
            instr_text = pause_info_font.render("←→ Select   ENTER Confirm", True, (180, 180, 180))
            instr_rect = instr_text.get_rect(center=(self.settings.screen_width // 2, button_y + 40))
            self.screen.blit(instr_text, instr_rect)
        else:
            # Main pause menu buttons
            resume_color = (255, 255, 0) if self.pause_menu_selection == 0 else (200, 200, 200)
            quit_color = (255, 255, 0) if self.pause_menu_selection == 1 else (200, 200, 200)

            resume_text = button_font.render("Resume", True, resume_color)
            quit_text = button_font.render("Quit to Main Menu", True, quit_color)

            resume_rect = resume_text.get_rect(center=(button_x - 80, button_y))
            quit_rect = quit_text.get_rect(center=(button_x + 80, button_y))

            self.screen.blit(resume_text, resume_rect)
            self.screen.blit(quit_text, quit_rect)

            # Instructions
            instr_text = pause_info_font.render("←→ Select   ENTER Confirm", True, (180, 180, 180))
            instr_rect = instr_text.get_rect(center=(self.settings.screen_width // 2, button_y + 40))
            self.screen.blit(instr_text, instr_rect)

    def _update_countdown(self):
        """Update countdown timer - transitions to playing state when complete"""
        if self.countdown_start_time is None:
            return
        
        now = pygame.time.get_ticks()
        elapsed = now - self.countdown_start_time
        
        # After 4 seconds, start the game
        if elapsed >= self.countdown_duration_ms:
            self.game_state = "playing"
            self.countdown_start_time = None
            # For bonus wave, reset spawn timers to start after countdown
            if self.is_bonus_wave:
                self.bonus_wave_start_time = now  # Reset start time to now
                self.bonus_loaf_next_spawn = now + self.settings.loafkitty_spawn_delay
                self.bonus_centurion_next_spawn = now + self.settings.centurionkitty_spawn_delay
                self.bonus_emperor_next_spawn = now + self.settings.emperorkitty_spawn_delay
                self.bonus_bluewhale_next_spawn = now + self.settings.bluewhalekitty_spawn_delay
                self.bonus_nyancat_next_spawn = now + self.settings.nyancat_spawn_delay
    
    def _draw_countdown(self):
        """Draw countdown timer with colored backgrounds"""
        if self.countdown_start_time is None:
            return
        
        now = pygame.time.get_ticks()
        elapsed = now - self.countdown_start_time
        
        # Determine current countdown text and colors
        if elapsed < 1000:  # 0-1 second: "3"
            text = "3"
            text_color = (255, 255, 255)  # White text
            bg_color = (255, 0, 0)  # Bright red background
        elif elapsed < 2000:  # 1-2 seconds: "2"
            text = "2"
            text_color = (255, 255, 255)  # White text
            bg_color = (255, 215, 0)  # Gold yellow background
        elif elapsed < 3000:  # 2-3 seconds: "1"
            text = "1"
            text_color = (255, 255, 255)  # White text
            bg_color = (0, 255, 0)  # Green background
        else:  # 3-4 seconds: "GO!"
            text = "GO!"
            text_color = (0, 255, 0)  # Green text
            bg_color = (255, 255, 255)  # White background
        
        # Load custom font (50% smaller than before)
        try:
            font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf'))
            countdown_font = pygame.font.Font(font_path, int(self.settings.screen_height * 0.10))
        except:
            countdown_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.10))
        
        # Render text
        text_surf = countdown_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2))
        
        # Draw background rectangle (backlit effect) - 50% smaller padding
        # Make it larger than text for better visibility
        bg_padding = 30
        bg_rect = pygame.Rect(
            text_rect.left - bg_padding,
            text_rect.top - bg_padding,
            text_rect.width + (bg_padding * 2),
            text_rect.height + (bg_padding * 2)
        )
        pygame.draw.rect(self.screen, bg_color, bg_rect)
        
        # Draw text on top
        self.screen.blit(text_surf, text_rect)

    def _init_defeat_screen(self):
        """Initialize defeat screen state"""
        # Stop all sounds before playing defeat sound
        # Stop all alien hum sounds
        for alien in self.aliens:
            if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                alien.hum_sound_channel.stop()
                alien.hum_sound_channel = None
        # Stop all lasertanker firing sounds
        for alien, channel in list(self.audio.lasertanker_firing_sound_channels.items()):
            if channel:
                channel.stop()
        self.audio.lasertanker_firing_sound_channels.clear()
        # Stop nyancat music
        if self.audio.nyancat_music_channel:
            self.audio.stop_music_channel(self.audio.nyancat_music_channel)
            self.audio.nyancat_music_channel = None
        
        # Set defeat screen start time for delayed music
        self.defeat_screen_start_time = pygame.time.get_ticks()
        
        #play defeat sound
        self.audio.play("announce_defeat")
        # Store player data before they're removed from sprite group
        self._store_final_player_data()
        # Defeat banner scrolls right to left (left edge positioning)
        try:
            font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf'))
            calc_font = pygame.font.Font(font_path, int(self.settings.screen_height * 0.14))
        except:
            calc_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.14))
        banner_text = "You were DEFEATED... better luck next invasion!"
        banner_width = calc_font.size(banner_text)[0]
        self.defeat_banner_x = self.settings.screen_width  # Start off-screen right (left edge at screen_width)
        self.defeat_banner_active = True
        self.credits_y = self.settings.screen_height_total  # Start below screen
        self.credits_active = False
        self.thanks_active = False
        # Initialize credits section tracking (will be initialized in _draw_credits)
        if hasattr(self, 'credits_section_y_positions'):
            del self.credits_section_y_positions
        if hasattr(self, 'credits_section_index'):
            del self.credits_section_index

    def _init_victory_screen(self):
        """Initialize victory screen state"""
        # Stop all sounds before playing victory sound
        # Stop all alien hum sounds
        for alien in self.aliens:
            if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                alien.hum_sound_channel.stop()
                alien.hum_sound_channel = None
        # Stop all lasertanker firing sounds
        for alien, channel in list(self.audio.lasertanker_firing_sound_channels.items()):
            if channel:
                channel.stop()
        self.audio.lasertanker_firing_sound_channels.clear()
        # Stop nyancat music
        if self.audio.nyancat_music_channel:
            self.audio.stop_music_channel(self.audio.nyancat_music_channel)
            self.audio.nyancat_music_channel = None
        
        # Set victory screen start time for delayed music
        self.victory_screen_start_time = pygame.time.get_ticks()
        
        #play victory sound
        self.audio.play("announce_victory")
        # Store player data before they're removed from sprite group
        self._store_final_player_data()
        # Choose random victory message
        victory_messages = [
            "VICTORYYYYYYYYYYYYYYYYYYYYYYYYYYYYY!",
            "YOU... WERE... VICTORIOUS!!!!! HUZZAH!!!!!!",
            "...AND THEY ALL LIVED... HAPPILY EVER AFTER."
        ]
        self.victory_banner_text = random.choice(victory_messages)
        # Victory banner scrolls right to left (left edge positioning)
        try:
            font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf'))
            calc_font = pygame.font.Font(font_path, int(self.settings.screen_height * 0.14))
        except:
            calc_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.14))
        banner_width = calc_font.size(self.victory_banner_text)[0]
        self.victory_banner_x = self.settings.screen_width  # Start off-screen right (left edge at screen_width)
        self.victory_banner_active = True
        self.credits_y = self.settings.screen_height_total  # Start below screen
        self.credits_active = False
        self.thanks_active = False
        # Initialize credits section tracking (will be initialized in _draw_credits)
        if hasattr(self, 'credits_section_y_positions'):
            del self.credits_section_y_positions
        if hasattr(self, 'credits_section_index'):
            del self.credits_section_index
        
        # Check for special password condition (Hard + powerups less than high/All off)
        is_hard = getattr(self.settings, "difficulty_mode", "easy").lower() == "hard"
        is_less_than_high = self.settings.powerup_drop_chance < 0.06  # Anything less than High
        all_off = (not self.settings.powerup_enable_nanites and 
                   not self.settings.powerup_enable_squadron and 
                   not self.settings.powerup_enable_shockwave)
        
        if is_hard and (is_less_than_high or all_off):
            self.password_phase = "transmission"
            self.password_start_time = None  # Will be set when thanks appears
        else:
            self.password_phase = None

        # Victory fireworks (normal mode only): keep ships/lifepods/squadrons and existing bullets,
        # but clear other gameplay sprites so the screen is clean.
        if not self.is_bonus_wave:
            self.victory_fireworks_active = True
            # Clear non-squadron powerup sprites
            self.powerups.empty()
            self.nanites.empty()
            self.shockwaves.empty()
            # Clear aliens/minions and their bullets
            self.aliens.empty()
            self.minions.empty()
            self.alien_bullets.empty()
            # Clear bonus-wave-only powerups/groups (defensive)
            self.dad_ships.empty()
            self.dad_shockwaves.empty()
            self.mom_ships.empty()
            self.mom_bullets.empty()
            # Reset any victory fireworks already present
            self.victory_fireworks.empty()

    def _update_defeat_victory_screens(self):  # bonus wave - handles both normal and bonus wave defeat/victory
        """Update defeat/victory screen animations"""
        now = pygame.time.get_ticks()
        
        if self.game_state == "defeat":
            # Update defeat banner - scrolls right to left (left edge positioning)
            if self.defeat_banner_active:
                self.defeat_banner_x -= self.wave_banner_speed  # Move left (from right)
                # Use same font as drawing to calculate width correctly
                try:
                    font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf'))
                    calc_font = pygame.font.Font(font_path, int(self.settings.screen_height * 0.14))
                except:
                    calc_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.14))
                banner_text = "THE PROPHECY IS... ... ... ... ... TRUE?" if self.is_bonus_wave else "You were DEFEATED... better luck next invasion!"
                banner_width = calc_font.size(banner_text)[0]
                # Banner stays until right edge (left edge + width) is off-screen left
                if self.defeat_banner_x + banner_width < 0:
                    self.defeat_banner_active = False
                    self.credits_active = True
            
            # Update credits scrolling - scrolls bottom to top at 1/4 speed
            if self.credits_active and not self.thanks_active:
                self.credits_y -= (self.wave_banner_speed / 4.0) * 0.75  # Credits scroll 25% slower than before
            
            # Start defeat music 3 seconds after defeat screen displays
            if self.defeat_screen_start_time is not None and self.audio.defeat_music_channel is None:
                elapsed = now - self.defeat_screen_start_time
                if elapsed >= 3000:  # 3 seconds
                    if self.is_bonus_wave:
                        self.audio.defeat_music_channel = self.audio.play("music_defeat_bonus", loop=-1)
                    else:
                        self.audio.defeat_music_channel = self.audio.play("music_defeat_normal", loop=-1)
            
        elif self.game_state == "victory":
            # Update victory banner - scrolls right to left (left edge positioning)
            if self.victory_banner_active:
                self.victory_banner_x -= self.wave_banner_speed  # Move left (from right)
                # Use same font as drawing to calculate width correctly
                try:
                    font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf'))
                    calc_font = pygame.font.Font(font_path, int(self.settings.screen_height * 0.14))
                except:
                    calc_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.14))
                banner_width = calc_font.size(self.victory_banner_text)[0]
                # Banner stays until right edge (left edge + width) is off-screen left
                if self.victory_banner_x + banner_width < 0:
                    self.victory_banner_active = False
                    self.credits_active = True
            
            # Update credits scrolling - scrolls bottom to top at 1/4 speed
            if self.credits_active and not self.thanks_active:
                self.credits_y -= (self.wave_banner_speed / 4.0) * 0.75  # Credits scroll 25% slower than before
            
            # Start victory music 10 seconds after victory screen displays (to allow announce_victory_1.wav to finish)
            if self.victory_screen_start_time is not None and self.audio.victory_music_channel is None:
                elapsed = now - self.victory_screen_start_time
                if elapsed >= 10000:  # 10 seconds
                    difficulty = getattr(self.settings, "difficulty_mode", "normal").lower()
                    if difficulty == "kiddie":
                        self.audio.victory_music_channel = self.audio.play("music_kiddie_victory", loop=-1)
                    elif difficulty == "easy":
                        self.audio.victory_music_channel = self.audio.play("music_easy_victory", loop=-1)
                    elif difficulty == "hard":
                        self.audio.victory_music_channel = self.audio.play("music_victory_hard", loop=-1)
                    else:  # normal or default
                        self.audio.victory_music_channel = self.audio.play("music_normal_victory", loop=-1)
            
            # Handle password sequence
            if self.password_phase == "transmission" and self.thanks_active:
                if self.password_start_time is None:
                    self.password_start_time = now
                elif now - self.password_start_time >= 5000:  # 5 seconds of blinking
                    self.password_phase = "password"
                    self.password_start_time = now
            # Password phase stays active until menu exit (no timeout)

    def _draw_defeat_victory_screens(self):  # bonus wave - handles both normal and bonus wave defeat/victory
        """Draw defeat/victory screen elements"""
        # Load fonts
        try:
            font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf'))
            banner_font = pygame.font.Font(font_path, int(self.settings.screen_height * 0.14))
            credit_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.14 / 3))
            thanks_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.10))
        except:
            banner_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.14))
            credit_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.14 / 3))
            thanks_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.10))

        if self.game_state == "defeat":
            # Draw defeat banner - scrolls right to left (left edge positioning)
            if self.defeat_banner_active:
                # bonus wave - use special defeat message for bonus wave
                if self.is_bonus_wave:
                    banner_text = "The prophecy is ... unfulfilled."
                    banner_surf = banner_font.render(banner_text, True, (255, 255, 0))
                else:
                    banner_text = "You were DEFEATED... better luck next invasion!"
                    banner_surf = banner_font.render(banner_text, True, (255, 0, 0))
                # Use topleft positioning (left edge at defeat_banner_x)
                banner_rect = banner_surf.get_rect(topleft=(int(self.defeat_banner_x), int(self.settings.screen_height * 0.2)))
                self.screen.blit(banner_surf, banner_rect)
            
            # Draw credits
            if self.credits_active:
                self._draw_credits(credit_font, thanks_font)
        
        elif self.game_state == "victory":
            # Draw victory banner - scrolls right to left (left edge positioning)
            if self.victory_banner_active and self.victory_banner_text:
                banner_surf = banner_font.render(self.victory_banner_text, True, (255, 255, 0))
                # Use topleft positioning (left edge at victory_banner_x)
                banner_rect = banner_surf.get_rect(topleft=(int(self.victory_banner_x), int(self.settings.screen_height * 0.2)))
                self.screen.blit(banner_surf, banner_rect)
            
            # Draw credits
            if self.credits_active:
                self._draw_credits(credit_font, thanks_font)
            
            # Draw password sequence or final message if applicable
            if self.thanks_active:
                now = pygame.time.get_ticks()
                
                if self.password_phase == "transmission":
                    # Blink at 1 blink per second (500ms on/off)
                    blink_on = ((now // 500) % 2 == 0)
                    if blink_on:
                        try:
                            font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf'))
                            password_font = pygame.font.Font(font_path, int(self.settings.screen_height * 0.10))
                        except:
                            password_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.10))
                        msg = password_font.render("INCOMING TRANSMISSION...", True, (255, 255, 255))
                        msg_rect = msg.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2))
                        self.screen.blit(msg, msg_rect)
                elif self.password_phase == "password":
                    # Show password solid (not blinking)
                    try:
                        font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf'))
                        password_font = pygame.font.Font(font_path, int(self.settings.screen_height * 0.10))
                    except:
                        password_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.10))
                    msg = password_font.render("SECRET PASSWORD: meowmeowMEOW", True, (255, 255, 0))
                    msg_rect = msg.get_rect(center=(self.settings.screen_width // 2, self.settings.screen_height // 2))
                    self.screen.blit(msg, msg_rect)
                elif self.password_phase is None:
                    # Show final victory message (not password condition)
                    final_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.07))
                    lines = [
                        "You did well! Come back after defeating Hard Mode,",
                        "with powerups on Normal or Rare,",
                        "and this is where the",
                        "SECRET MESSAGE",
                        "will appear..."
                    ]
                    y_start = self.settings.screen_height // 2 - (len(lines) * final_font.get_height() // 2)
                    for i, line in enumerate(lines):
                        msg = final_font.render(line, True, (255, 255, 255))
                        msg_rect = msg.get_rect(center=(self.settings.screen_width // 2, y_start + i * final_font.get_height()))
                        self.screen.blit(msg, msg_rect)

    def _ensure_player_stats(self, player_id):
        """Ensure player_stats entry exists for a player_id, initialize if missing"""
        if player_id not in self.player_stats:
            self.player_stats[player_id] = {
                'damage_taken': 0,
                'lives_lost': 0,
                'bullets_fired': 0,
                'bullets_hit': 0,
                'shield_recharge_shots': 0,
                'alien_collision_kills': 0,
                'time_in_top_30_percent': 0,
                'enemies_destroyed': 0
            }
    
    def _store_final_player_data(self):
        """Store player data for credits display (called before players are removed from sprite group)"""
        # Build a fresh, full set of credit rows (avoid partial/duplicate records).
        self.final_player_data = []
        
        # Get all active player IDs (from active_player_ids if available, otherwise from current players)
        if hasattr(self, 'active_player_ids') and self.active_player_ids:
            all_player_ids = self.active_player_ids
        else:
            # Fallback: get from current players
            all_player_ids = [p.player_id for p in self.players.sprites()]
            # If still empty, try to get from player_stats (players who had stats tracked)
            if not all_player_ids and hasattr(self, 'player_stats') and self.player_stats:
                all_player_ids = list(self.player_stats.keys())
        
        # Store data for all active players (both in sprite group and those that might have been removed)
        for player_id in all_player_ids:
            # Ensure stats exist for this player
            self._ensure_player_stats(player_id)
            
            # Try to get player from sprite group first (for score and powerups)
            player = None
            for p in self.players.sprites():
                if p.player_id == player_id:
                    player = p
                    break
            
            # Get player stats (should always be available now)
            stats = self.player_stats.get(player_id, {})
            
            # Resolve score/powerups:
            # - Prefer live player object if present
            # - Else fall back to snapshot captured at final death
            snapshot = {}
            if hasattr(self, 'final_player_snapshots') and self.final_player_snapshots:
                snapshot = self.final_player_snapshots.get(player_id, {}) or {}

            resolved_score = player.player_score if player else snapshot.get('player_score', 0)
            resolved_powerups_used = dict(player.powerups_used) if player else snapshot.get(
                'powerups_used',
                {"squadron": 0, "shockwave": 0, "nanites": 0, "dad": 0, "mom": 0},
            )

            # Store full credit row
            player_data = {
                'player_id': player_id,
                'player_score': resolved_score,
                'powerups_used': resolved_powerups_used,
                'damage_taken': stats.get('damage_taken', 0),
                'lives_lost': stats.get('lives_lost', 0),
                'bullets_fired': stats.get('bullets_fired', 0),
                'bullets_hit': stats.get('bullets_hit', 0),
                'shield_recharge_shots': stats.get('shield_recharge_shots', 0),
                'alien_collision_kills': stats.get('alien_collision_kills', 0),
                'time_in_top_30_percent': stats.get('time_in_top_30_percent', 0),
                'enemies_destroyed': stats.get('enemies_destroyed', 0)
            }
            self.final_player_data.append(player_data)
    
    def _draw_credits(self, credit_font, thanks_font):
        """Draw scrolling credits for defeat/victory with new format and staggered sections"""
        # Use stored player data if available, otherwise use current players
        if hasattr(self, 'final_player_data') and self.final_player_data:
            player_list = self.final_player_data
        else:
            # Fallback: try to get from current players and merge with stats
            player_list = []
            for p in self.players.sprites():
                player_id = p.player_id
                stats = self.player_stats.get(player_id, {})
                player_data = {
                    'player_id': player_id,
                    'player_score': p.player_score,
                    'powerups_used': p.powerups_used,
                    'damage_taken': stats.get('damage_taken', 0),
                    'lives_lost': stats.get('lives_lost', 0),
                    'bullets_fired': stats.get('bullets_fired', 0),
                    'bullets_hit': stats.get('bullets_hit', 0),
                    'shield_recharge_shots': stats.get('shield_recharge_shots', 0),
                    'alien_collision_kills': stats.get('alien_collision_kills', 0),
                    'time_in_top_30_percent': stats.get('time_in_top_30_percent', 0),
                    'enemies_destroyed': stats.get('enemies_destroyed', 0)
                }
                player_list.append(player_data)
        
        # Get all players that were in the game (use active_player_ids if available, otherwise extract from player_list)
        if hasattr(self, 'active_player_ids') and self.active_player_ids:
            active_ids = sorted(self.active_player_ids)
        else:
            active_ids = sorted([p['player_id'] for p in player_list])
        
        # Create a lookup dict for player data
        player_dict = {p['player_id']: p for p in player_list}
        
        # Load ship images for player icons (cache them, only load once) - 30w x 20h
        if self.credits_ship_images is None:
            from ship import ship1_path, ship2_path, ship3_path, ship4_path
            ship_paths = {1: ship1_path, 2: ship2_path, 3: ship3_path, 4: ship4_path}
            self.credits_ship_images = {}
            for player_id_iter, path in ship_paths.items():
                try:
                    img = pygame.image.load(path).convert_alpha()
                    # Scale to fixed 30w x 20h
                    self.credits_ship_images[player_id_iter] = pygame.transform.smoothscale(img, (30, 20))
                except:
                    self.credits_ship_images[player_id_iter] = None
        ship_images = self.credits_ship_images
        
        # Define sections in order
        sections = []
        
        # Get players sorted by score (for sections that need score sorting)
        players_by_score = sorted([player_dict[pid] for pid in active_ids if pid in player_dict], 
                                  key=lambda p: p.get('player_score', 0), reverse=True)
        
        # Section 1: ENEMIES DESTROYED (sorted by score, highest first)
        section1_items = []
        section1_items.append(("ENEMIES DESTROYED:", credit_font, (255, 255, 255)))
        for player_data in players_by_score:
            enemies = player_data.get('enemies_destroyed', 0)
            section1_items.append((f"Player {player_data['player_id']}: {enemies}", credit_font, (230, 230, 230), player_data['player_id']))
        sections.append(section1_items)
        
        # Section 2: DAMAGE TAKEN (sorted by score, highest first)
        section2_items = []
        section2_items.append(("DAMAGE TAKEN", credit_font, (255, 255, 255)))
        for player_data in players_by_score:
            damage = player_data.get('damage_taken', 0)
            section2_items.append((f"Player {player_data['player_id']}: {damage}", credit_font, (230, 230, 230), player_data['player_id']))
        sections.append(section2_items)
        
        # Section 3: LIVES LOST (sorted by score, highest first)
        section3_items = []
        section3_items.append(("LIVES LOST", credit_font, (255, 255, 255)))
        for player_data in players_by_score:
            lives_lost = player_data.get('lives_lost', 0)
            section3_items.append((f"Player {player_data['player_id']}: {lives_lost}", credit_font, (230, 230, 230), player_data['player_id']))
        sections.append(section3_items)
        
        # Section 4: ACCURACY (sorted by score, highest first)
        section4_items = []
        section4_items.append(("ACCURACY", credit_font, (255, 255, 255)))
        for player_data in players_by_score:
            bullets_fired = player_data.get('bullets_fired', 0)
            bullets_hit = player_data.get('bullets_hit', 0)
            if bullets_fired > 0:
                accuracy = round((bullets_hit / bullets_fired) * 100)
                section4_items.append((f"Player {player_data['player_id']}: {accuracy}%", credit_font, (230, 230, 230), player_data['player_id']))
            else:
                section4_items.append((f"Player {player_data['player_id']}: N/A", credit_font, (230, 230, 230), player_data['player_id']))
        sections.append(section4_items)
        
        # Section 5: TOTAL PLAYER SCORE (sorted by score, highest first)
        section5_items = []
        section5_items.append(("TOTAL PLAYER SCORE", credit_font, (255, 255, 255)))
        for player_data in players_by_score:
            score = player_data.get('player_score', 0)
            section5_items.append((f"Player {player_data['player_id']}: {score}", credit_font, (230, 230, 230), player_data['player_id']))
        sections.append(section5_items)
        
        # Section 6: POWERUP AWARDS (sorted 1-4)
        section6_items = []
        section6_items.append(("POWERUP AWARDS:", credit_font, (255, 255, 255)))
        # Get players in order 1-4
        ordered_players = [player_dict[pid] for pid in active_ids if pid in player_dict]
        if len(ordered_players) > 0:
            # Squadron Leader
            squadron_leader = max(ordered_players, key=lambda p: p['powerups_used'].get("squadron", 0))
            if squadron_leader['powerups_used'].get("squadron", 0) > 0:
                section6_items.append(("Squadron Leader:", credit_font, (255, 255, 255), squadron_leader['player_id']))
            
            # Biggest Shocker
            shocker = max(ordered_players, key=lambda p: p['powerups_used'].get("shockwave", 0))
            if shocker['powerups_used'].get("shockwave", 0) > 0:
                section6_items.append(("Biggest Shocker:", credit_font, (255, 255, 255), shocker['player_id']))
            
            # Handy Dandy Nanite Nanny
            nanite_nanny = max(ordered_players, key=lambda p: p['powerups_used'].get("nanites", 0))
            if nanite_nanny['powerups_used'].get("nanites", 0) > 0:
                section6_items.append(("Handy Dandy Nanite Nanny:", credit_font, (255, 255, 255), nanite_nanny['player_id']))
        sections.append(section6_items)
        
        # Section 7: CONDUCT AWARDS (sorted 1-4)
        section7_items = []
        section7_items.append(("CONDUCT AWARDS:", credit_font, (255, 255, 255)))
        if len(ordered_players) > 0:
            # Selfless Hero (most alien collision kills)
            collision_kills = [p.get('alien_collision_kills', 0) for p in ordered_players]
            if max(collision_kills) > 0:
                selfless_hero = max(ordered_players, key=lambda p: p.get('alien_collision_kills', 0))
                section7_items.append(("Selfless Hero:", credit_font, (255, 255, 255), selfless_hero['player_id']))
            
            # Shield Master (most shield recharge shots)
            shield_shots = [p.get('shield_recharge_shots', 0) for p in ordered_players]
            if max(shield_shots) > 0:
                shield_master = max(ordered_players, key=lambda p: p.get('shield_recharge_shots', 0))
                section7_items.append(("Shield Master:", credit_font, (255, 255, 255), shield_master['player_id']))
            
            # Power Forward (most time in top 30%)
            top_30_times = [p.get('time_in_top_30_percent', 0) for p in ordered_players]
            if max(top_30_times) > 0:
                power_forward = max(ordered_players, key=lambda p: p.get('time_in_top_30_percent', 0))
                section7_items.append(("Power Forward:", credit_font, (255, 255, 255), power_forward['player_id']))
        sections.append(section7_items)
        
        # Add "THANK YOU FOR PLAYING" as a scrolling section
        section8_items = []
        try:
            font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf'))
            thanks_banner_font = pygame.font.Font(font_path, int(self.settings.screen_height * 0.14))
        except:
            thanks_banner_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.14))
        section8_items.append(("THANK YOU FOR PLAYING!", thanks_banner_font, (255, 255, 255)))
        sections.append(section8_items)
        
        # Staggered scrolling: track each section's current Y position independently
        if not hasattr(self, 'credits_section_y_positions'):
            # Initialize: track current Y position for each active section
            self.credits_section_y_positions = {}  # {section_index: current_y_position}
            self.credits_section_index = 0
            # Start first section at bottom of screen
            self.credits_section_y_positions[0] = self.settings.screen_height_total
        
        # Get scroll speed (same speed used in _update_defeat_victory_screens)
        scroll_speed = (self.wave_banner_speed / 4.0) * 0.75
        
        # Check if we should advance to next section
        screen_midpoint = self.settings.screen_height * 0.5
        
        # Check if current section header has reached midpoint, and start next section
        if self.credits_section_index < len(sections):
            # Get current section's header position
            if self.credits_section_index in self.credits_section_y_positions:
                current_header_y = self.credits_section_y_positions[self.credits_section_index]
                
                # If header reached midpoint, start next section
                if current_header_y <= screen_midpoint and self.credits_section_index < len(sections) - 1:
                    self.credits_section_index += 1
                    # Start new section at bottom of screen
                    self.credits_section_y_positions[self.credits_section_index] = self.settings.screen_height_total
        
        # Update all active sections' positions (they all scroll at the same speed)
        for section_idx in self.credits_section_y_positions:
            self.credits_section_y_positions[section_idx] -= scroll_speed
        
        # Draw ALL active sections (all sections from 0 to credits_section_index)
        for section_idx in range(self.credits_section_index + 1):
            if section_idx >= len(sections):
                continue
            if section_idx not in self.credits_section_y_positions:
                continue
                
            # Get this section's current position
            current_section_y = self.credits_section_y_positions[section_idx]
            
            current_section = sections[section_idx]
            section_y = current_section_y
            
            for item in current_section:
                if len(item) == 4:  # Has player_id for icon
                    text, font, color, player_id = item
                else:
                    text, font, color = item
                    player_id = None
                
                if -50 < section_y < self.settings.screen_height_total + 50:  # Only draw if visible
                    # Render text first to get its width
                    surf = font.render(text, True, color)
                    text_width, text_height = surf.get_size()
                    
                    # Draw player icon if available (30x20 size) - to the RIGHT of text
                    if player_id and player_id in ship_images and ship_images[player_id]:
                        icon = ship_images[player_id]
                        # Position icon to the right of the text
                        icon_x = self.settings.screen_width // 2 + text_width // 2 + 10
                        icon_y = section_y - icon.get_height() // 2
                        self.screen.blit(icon, (icon_x, icon_y))
                    
                    # Draw text centered
                    rect = surf.get_rect(center=(self.settings.screen_width // 2, int(section_y)))
                    self.screen.blit(surf, rect)
                
                section_y += font.get_height() * 1.5
        
        # Check if credits are done scrolling (last section has scrolled off screen)
        if self.credits_section_index >= len(sections) - 1:
            # Calculate last section end position
            last_section_idx = len(sections) - 1
            if last_section_idx in self.credits_section_y_positions:
                current_last_section_y = self.credits_section_y_positions[last_section_idx]
                
                # Calculate where the end of the last section is
                last_section_y = current_last_section_y
                for item in sections[-1]:
                    if len(item) == 4:
                        text, font, color, player_id = item
                    else:
                        text, font, color = item
                    last_section_y += font.get_height() * 1.5
                
                if last_section_y < -100 and not self.thanks_active:
                    self.thanks_active = True
                    if self.password_phase == "transmission":
                        self.password_start_time = pygame.time.get_ticks()


    def _new_alien_wave(self, next_wave_num: int):
        """helper function for update_game() to spawn an new wave of aliens"""
        # Skip wave setup for bonus wave (bonus wave has its own initialization)
        if self.is_bonus_wave:
            return
        
        #first: if we reach the end of the wave index, we have no more weaves to spawn, and we end the game.""
        if next_wave_num >= len(self.settings.wave_master_index):
            self.game_state = "victory" #set the game state to finish,
            self._init_victory_screen()
            return #ignore the rest of the function. 
        
        #otherwise start a new wave:
        else:
            self.breaches_this_wave = 0
            self.current_wave_num = next_wave_num # set the current wave number. Above, this variable was received by the _new_alien_wave() helper function from the update_game() function.
            # Reset defense strength for new wave (scales per wave: wave_num + 2)
            self.max_breach_tolerance = self.current_wave_num + 2
            self.current_defense_strength = self.max_breach_tolerance - self.breaches_this_wave
            current_wave = self.settings.wave_master_index[self.current_wave_num] #set the variable "wave" to reference the dictionary corresponding with the correct index number -->
                                                            #--> in the wave_master_index in the base_settings file.
            
            # Apply wave-based difficulty scaling (steeper scaling per wave)
            # Scale speeds, spawn rates, and fire rates based on wave number
            # Only apply if baseline values exist (they should be set in apply_start_config)
            if hasattr(self, '_base_level2_minspawntime'):
                wave_scale = 1.0 + (self.current_wave_num * 0.06)  # 6% increase per wave (reduced from 8%)
                
                # Scale alien speeds
                self.settings.alien2_speed = self._base_alien2_speed * wave_scale
                self.settings.alien3_speed = self._base_alien3_speed * wave_scale
                self.settings.alien4_speed = self._base_alien4_speed * wave_scale
                self.settings.destroyer_speed = self._base_destroyer_speed * wave_scale
                self.settings.cruiser_speed = self._base_cruiser_speed * wave_scale
                self.settings.laztanker_speed = self._base_laztanker_speed * wave_scale
                self.settings.fleet_advance_speed = self._base_fleet_advance_speed * wave_scale
                
                # Scale spawn intervals (lower = faster spawning)
                spawn_interval_scale = 1.0 - (self.current_wave_num * 0.05)  # 5% faster spawning per wave (reduced from 7%)
                spawn_interval_scale = max(0.5, spawn_interval_scale)  # Cap at 50% of original
                
                self.level2_minspawntime = max(1, int(self._base_level2_minspawntime * spawn_interval_scale))
                self.level2_maxspawntime = max(1, int(self._base_level2_maxspawntime * spawn_interval_scale))
                self.level3_minspawntime = max(1, int(self._base_level3_minspawntime * spawn_interval_scale))
                self.level3_maxspawntime = max(1, int(self._base_level3_maxspawntime * spawn_interval_scale))
                self.level4_minspawntime = max(1, int(self._base_level4_minspawntime * spawn_interval_scale))
                self.level4_maxspawntime = max(1, int(self._base_level4_maxspawntime * spawn_interval_scale))
                self.destroyer_minspawntime = max(1, int(self._base_destroyer_minspawntime * spawn_interval_scale))
                self.destroyer_maxspawntime = max(1, int(self._base_destroyer_maxspawntime * spawn_interval_scale))
                self.cruiser_minspawntime = max(1, int(self._base_cruiser_minspawntime * spawn_interval_scale))
                self.cruiser_maxspawntime = max(1, int(self._base_cruiser_maxspawntime * spawn_interval_scale))
                self.laztanker_minspawntime = max(1, int(self._base_laztanker_minspawntime * spawn_interval_scale))
                self.laztanker_maxspawntime = max(1, int(self._base_laztanker_maxspawntime * spawn_interval_scale))
                
                # Scale fire intervals (lower = faster firing)
                fire_interval_scale = 1.0 - (self.current_wave_num * 0.05)  # 5% faster firing per wave (reduced from 6%)
                fire_interval_scale = max(0.4, fire_interval_scale)  # Cap at 40% of original
                
                self.settings.alien2_min_fire_interval = max(100, int(self._base_alien2_min_fire_interval * fire_interval_scale))
                self.settings.alien2_max_fire_interval = max(100, int(self._base_alien2_max_fire_interval * fire_interval_scale))
                self.settings.alien3_min_fire_interval = max(100, int(self._base_alien3_min_fire_interval * fire_interval_scale))
                self.settings.alien3_max_fire_interval = max(100, int(self._base_alien3_max_fire_interval * fire_interval_scale))
                self.settings.destroyer_min_fire_interval = max(50, int(self._base_destroyer_min_fire_interval * fire_interval_scale))
                self.settings.destroyer_max_fire_interval = max(50, int(self._base_destroyer_max_fire_interval * fire_interval_scale))
                self.settings.cruiser_min_fire_interval = max(50, int(self._base_cruiser_min_fire_interval * fire_interval_scale))
                self.settings.cruiser_max_fire_interval = max(50, int(self._base_cruiser_max_fire_interval * fire_interval_scale))
                self.settings.laztanker_min_fire_interval = max(50, int(self._base_laztanker_min_fire_interval * fire_interval_scale))
                self.settings.laztanker_max_fire_interval = max(50, int(self._base_laztanker_max_fire_interval * fire_interval_scale))
            
            #clear any leftover aliens - ChatGPT recommended I do this; I suppose its good to clean things up just in case?
            # Stop all alien hum sounds before clearing (level 4, destroyer, cruiser, lasertanker)
            for alien in self.aliens:
                if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                    alien.hum_sound_channel.stop()
                    alien.hum_sound_channel = None
            self.aliens.empty()
            if self.settings.shields_respawn_each_wave:
                self._create_shields()  # refresh shields for new wave
            # In Kiddie mode, recharge shields at new wave (heal all shields to full, respawn dead ones)
            elif hasattr(self.settings, 'difficulty_mode') and self.settings.difficulty_mode.lower() == "kiddie":
                # Respawn dead shields
                if len(self.shields) < self.settings.shield_count:
                    self._create_shields()  # This will recreate all shields
                # Heal all shields to full
                for shield in self.shields:
                    if shield.alive():  # Only heal shields that still exist
                        shield.heal(len(self.settings.shield_colors))  # Heal to full (index 0)

            #get alien counts for this wave:
            self.level1_rows_total = current_wave["rows_level1"] #get the number of total lvl 1 rows from the dictionary in base_settings.py
            self.level1_rows_spawned = 0 #set number of rows spawned to 0
            self.level1_rows_remaining = self.level1_rows_total #assign a variable to count how many rows remain
            print("Starting wave", self.current_wave_num, "with rows_level1 = ", self.level1_rows_total)
            self.level2_remaining = current_wave["count_level2"] #set a counter for the number of lvl 2 aliens to spawn ()"note that counters are currently defunct; they are functioning as an 'on/off' switch")
            self.level3_remaining = current_wave["count_level3"] #"" ""  for level 3 """"
            self.level4_remaining = current_wave["count_level4"]
            self.destroyers_remaining = current_wave["count_destroyers"]

            #start alien spawning using pygame timer/clock:
            now = pygame.time.get_ticks()
            self.next_level1_row_time = now #spawn a row of lvl 1 aliens immediately.
            self.next_level2_spawn_time = now + self.settings.alien2_spawn_delay #set a timer to spawn first lvl 2 alien in ~3 sec
            self.next_level3_spawn_time = now + self.settings.alien3_spawn_delay # " " lvl 3 " " 
            self.next_level4_spawn_time = now + self.settings.alien4_spawn_delay # " " lvl 4 " " 
            self.next_destroyer_spawn_time = now + self.settings.destroyer_spawn_delay
            self.next_cruiser_spawn_time = now + self.settings.cruiser_spawn_delay
            self.next_laztanker_spawn_time = now + self.settings.laztanker_spawn_delay

            self.next_squadspawn = 0

        
            # Spawn initial visible rows immediately, on-screen
            rows_to_spawn_now = min(self.settings.level1_alien_starting_rows, self.level1_rows_total, self.max_visible_level1_rows)
            for row_iteration in range(rows_to_spawn_now):
                        # First visible rows start at some y offset, e.g. 60, then spaced out
                        base_y = 60
                        row_spacing = 70  # pixels between level 1 rows
                        row_y = base_y + row_iteration * row_spacing
                        self._spawn_level1_row(row_y, warp_in=True)
                        self.level1_rows_spawned += 1

            self.level1_rows_remaining = self.level1_rows_total - self.level1_rows_spawned
            self.level1_reinforcements_threshhold = base_y + 10
            self.game_state = "playing"
        


    def _spawn_level1_row(self, row_y: int, warp_in: bool = False):
            """helper function for _new_alien_wave() function; spawns a row of level1 aliens"""
            tailor_alien1 = Alien(self.settings, self.screen, level=1) #create a little tailor alien for measuring.
            alien1_width = tailor_alien1.rect.width

            margin_x = self.settings.fleet_margin_x
            spacing_x = self.settings.fleet_spacing_x
            battlefield_width = self.settings.screen_width - (2 * margin_x)
            lvl1_aliens_per_row = (battlefield_width // ( spacing_x + alien1_width)) #floor division to find the nearest lesser integer, which will give us how many lvl1 aliens can fit in the screen space.

            total_row_width = lvl1_aliens_per_row*alien1_width + (lvl1_aliens_per_row - 1)*spacing_x # count up the alien widths plus the spaces, to determine the length of the row for centering
            start_x = (self.settings.screen_width - total_row_width) // 2 # clever way of keeping the row centered: find the difference between the total row width and the screen width; split that effectively in two, and stick half of it as a buffer before the first alien.
            #use a for loop to place the aliens:
            for i in range(lvl1_aliens_per_row): 
                fleet_alien_iter = Alien(self.settings, self.screen, level=1)
                x = start_x + i*(fleet_alien_iter.rect.width + spacing_x)
                spawn_y = -fleet_alien_iter.rect.height if warp_in else row_y
                fleet_alien_iter.spawn_pos(x, spawn_y) #call the spawn_pos() function from alien.py to help determine spawn positions.
                if warp_in:
                    fleet_alien_iter.warping_in = True
                    fleet_alien_iter.warp_target_y = row_y
                self.aliens.add(fleet_alien_iter) # add the new alien to the aliens sprite group.


                            
    def _update_wave_spawning(self):
                    """helper function for _update_game() function - spawns level 1 and lvls 2-4 aliens. 
                    Draws adjusted spawn interval info from menu_helpers.py."""
                    # Safety check: ensure current_wave_num is valid
                    if self.current_wave_num is None or self.current_wave_num < 0 or self.current_wave_num >= len(self.settings.wave_master_index):
                        return
                    now = pygame.time.get_ticks() #hook into the clock with a now variable to store get_ticks()
                    
                    #spawning lvl 1 aliens
                    if self.level1_rows_remaining > 0 and now >=self.next_level1_row_time:
                        level_1_aliens = [alien for alien in self.aliens if alien.level ==1]
                        
                        if level_1_aliens:
                            top_y = min(alien.rect.top for alien in level_1_aliens)
                            
                        else:
                            top_y = self.settings.screen_height # if no level 1 aliens are on the screen, tell the spawner "the last level 1 alien is as far away as the bottom of the screen" - most future-tweak-foolproof way of keeping this rule in effect.y

                        if top_y > self.level1_reinforcements_threshhold:
                             tailor_alien = Alien(self.settings, self.screen, level=1)
                             self._spawn_level1_row(-tailor_alien.rect.height, warp_in=False) 

                             self.level1_rows_remaining -= 1
                             self.level1_rows_spawned += 1
                             self.next_level1_row_time = now + self.level1_row_spawn_delay_ms
                    
                    #spawning lvl 2 aliens - the following statements used to use a countdown based on the numbers in the wave_master_index list in base_settings; 
                    #-->but currently the setup of the following statement says: if the master index is greater than zero for this type of alien AND there are
                    #more than 0 level 1 aliens left, and the next spawn time for this type of alien has been reached,then spawn an alien.
                    if self.settings.wave_master_index[self.current_wave_num]["count_level2"]>0 and self.level1_rows_remaining > 0 and now >= self.next_level2_spawn_time:
                         self._spawn_single_alien(level=2)
                         #self.level2_remaining -=1
                         self.next_level2_spawn_time = (now + random.randint
                                                        (self.level2_minspawntime, #as mentioned in the function descriptions, these adjusted max/minspawntimes are from menu_helpers gamesetup() function.
                                                        self.level2_maxspawntime)
                                                            )
                    #spawning lvl 3 aliens:
                    if self.settings.wave_master_index[self.current_wave_num]["count_level3"]>0 and self.level1_rows_remaining > 0 and now>=self.next_level3_spawn_time:
                         self._spawn_single_alien(level=3)
                         #self.level3_remaining -= 1
                         self.next_level3_spawn_time = (now + random.randint
                                                        (self.level3_minspawntime, 
                                                         self.level3_maxspawntime)
                                                            )
                    #spawning lvl 4 aliens:
                    if self.settings.wave_master_index[self.current_wave_num]["count_level4"]>0 and self.level1_rows_remaining > 0 and now>=self.next_level4_spawn_time:
                         self._spawn_single_alien(level=4)
                         #self.level4_remaining -= 1
                         self.next_level4_spawn_time = (now + random.randint
                                                        (self.level4_minspawntime, 
                                                         self.level4_maxspawntime)
                                                            )                      
                    #spawning destroyers:
                    if (self.settings.wave_master_index[self.current_wave_num]["count_destroyers"]>0 
                        and self.level1_rows_remaining > 0 
                        and now>=self.next_destroyer_spawn_time):
                         
                         self._spawn_single_alien(level=5) #destroyer
                         #self.destroyers_remaining -= 1
                         self.next_destroyer_spawn_time = (now + random.randint
                                                        (self.destroyer_minspawntime, 
                                                         self.destroyer_maxspawntime)
                                                            )

                  #spawning cruisers:
                    if (self.settings.wave_master_index[self.current_wave_num]["count_cruisers"]>0 
                        and self.level1_rows_remaining > 0 
                        and now>=self.next_cruiser_spawn_time):
                         
                         self._spawn_single_alien(level=6) #cruisers
                         #self.cruisers_remaining -= 1
                         self.next_cruiser_spawn_time = (now + random.randint
                                                        (self.cruiser_minspawntime, 
                                                         self.cruiser_maxspawntime)
                                                            )
                    #spawning laser tankers:
                    if (self.settings.wave_master_index[self.current_wave_num]["count_laz0rtankers"]>0 
                        and self.level1_rows_remaining > 0 
                        and now>=self.next_laztanker_spawn_time):
                         
                         self._spawn_single_alien(level=7) #laser tanker
                         #self.cruisers_remaining -= 1
                         self.next_laztanker_spawn_time = (now + random.randint
                                                        (self.laztanker_minspawntime, 
                                                         self.laztanker_maxspawntime)
                                                            )
                    
                    #In future: add cruisers, laser tankers, and gunships to this list.                                            
                    
                    #Interceptor spawns, to keep players from choking spawn 
                    #if self.current_wave_num >5:
                     #   for player in self.players:
                      #       if player.rect.top < self.settings.screen_height // 3: # if the player is more than 2/3 of the way up the screen
                       #           self._spawn_alien_interceptor(player.player_id) #spawn an interceptor alien to harass them.
                     
    #FOR SPAWNING NON-FLEET ALIENS
    def _spawn_single_alien(self, level: int):
                    """helper function for _update_wave_spawning() - spawns any aliens that are ready to spawn."""
                    new_alien = Alien(self.settings, self.screen, level=level)

                    if new_alien.level == 2: #spawn level 2 aliens so that their zigzagging won't get them stuck against the side of the screen.
                        min_x = new_alien.zig_amplitude + new_alien.rect.width
                        max_x = self.settings.screen_width - (new_alien.zig_amplitude + new_alien.rect.width)
                    
                    elif new_alien.level == 6: #cruiser - I don't want these too close to the edge either b/c of their firing pattern.
                         min_x = int(self.settings.screen_width * 0.3)
                         max_x = int(self.settings.screen_width * 0.7)
                    
                    else:
                        min_x = new_alien.rect.width
                        max_x = self.settings.screen_width - new_alien.rect.width
                    
                    x = random.randint(min_x, max_x)
                    y = -new_alien.rect.height #start just off screen
                    new_alien.spawn_pos(x,y)
                    
                    # Play hum sounds for level 4, destroyer (5), cruiser (6), and tanker (7)
                    if new_alien.level == 4:
                        if "alien_lvl4_hum" in self.audio.sounds and self.audio.sounds["alien_lvl4_hum"]:
                            hum_sound = self.audio.sounds["alien_lvl4_hum"][0]
                            new_alien.hum_sound_channel = hum_sound.play(-1)  # Loop indefinitely (-1 means loop)
                        else:
                            new_alien.hum_sound_channel = None
                    elif new_alien.level == 5:  # Destroyer
                        if "alien_destroyer_hum" in self.audio.sounds and self.audio.sounds["alien_destroyer_hum"]:
                            hum_sound = self.audio.sounds["alien_destroyer_hum"][0]
                            new_alien.hum_sound_channel = hum_sound.play(-1)
                        else:
                            new_alien.hum_sound_channel = None
                    elif new_alien.level == 6:  # Cruiser
                        if "alien_cruiser_hum" in self.audio.sounds and self.audio.sounds["alien_cruiser_hum"]:
                            hum_sound = self.audio.sounds["alien_cruiser_hum"][0]
                            new_alien.hum_sound_channel = hum_sound.play(-1)
                        else:
                            new_alien.hum_sound_channel = None
                    elif new_alien.level == 7:  # Lasertanker
                        if "alien_tanker_hum" in self.audio.sounds and self.audio.sounds["alien_tanker_hum"]:
                            hum_sound = self.audio.sounds["alien_tanker_hum"][0]
                            new_alien.hum_sound_channel = hum_sound.play(-1)
                        else:
                            new_alien.hum_sound_channel = None
                    else:
                        new_alien.hum_sound_channel = None

                    # lock a target player for destroyers and cruisers to list toward
                    if level in (5, 6) and self.players:
                        target_player = min(
                            self.players,
                            key=lambda p: abs(p.rect.centerx - new_alien.rect.centerx)
                        )
                        new_alien.set_target_player(target_player)

                    # Lazertankers spawn with laserminions on wave 8 and higher (not in Kiddie mode)
                    # Note: current_wave_num is 0-indexed (wave 8 = index 7, wave 9 = index 8)
                    if level == 7 and self.current_wave_num >= 7 and (self.settings.difficulty_mode.lower() != "kiddie"):
                    
                        self._spawn_laserminions_for_lazertanker(new_alien, new_alien)
                    
                    self.aliens.add(new_alien)

    def _spawn_laserminions_for_lazertanker(self, lazertanker, owner_tanker):
        """Spawn laserminions positioned around the lazertanker. Number depends on difficulty mode."""

        tanker_width = lazertanker.rect.width
        tanker_bottom = lazertanker.rect.bottom

        # Determine number of minions based on difficulty
        difficulty = getattr(self.settings, 'difficulty_mode', 'easy').lower()

        if difficulty == "hard":
            # Hard mode: 6 minions (2 columns × 3 rows)
            num_rows = 3
            num_cols = 2
        elif difficulty == "normal":
            # Normal mode: 4 minions (2 columns × 2 rows)
            num_rows = 2
            num_cols = 2
        else:
            # Easy mode: 2 minions (2 columns × 1 row)
            num_rows = 1
            num_cols = 2

        # Column positions: evenly distributed across the lazertanker
        column_positions = []
        for i in range(num_cols):
            # Distribute columns evenly (25%, 75% for 2 cols; centered for 1 col)
            if num_cols == 1:
                col_x = lazertanker.rect.centerx
            else:
                col_x = lazertanker.rect.left + int(tanker_width * (0.25 + (i * 0.5 / (num_cols - 1))))
            column_positions.append(col_x)

        # Vertical positions: bottom-aligned, then stack up with 5px spacing
        # Each minion is 25px tall, so spacing between them is 5px
        y_positions = []
        for i in range(num_rows):
            y_positions.append(tanker_bottom - (i * (25 + 5)))

        # Spawn minions in specified number of columns
        spawn_positions = []
        for col_x in column_positions:
            for y_pos in y_positions:
                spawn_positions.append((col_x, y_pos))

        for col_x, y_pos in spawn_positions:
            minion = Laserminion(self.settings, self.screen, owner_tanker)
            minion.spawn_pos(col_x, y_pos)
            self.minions.add(minion)  # Add to minions group

    if False: #add back in once the code for interceptors is complete.
        def _spawn_alien_interceptor (self, player_id): 
            """if players are choking toward the top of the screen, squadron members begin to spawn - level '30' aliens -  just needed a placeholder number."""
            self.player_id = player_id
            now = pygame.time.get_ticks()
            if 0!= self.next_interceptor_spawn <= now:
                    new_alien = Alien(self.settings, self.screen, level=30)
                    y = int(player_id.rect.y) #starts even with the player
                    #TODO: consider changing the x so that spawner selects the side of the screen farther from the player at time of spawn. Avoids invisible collisions. current code is random.choice(self.settings.screen_width+ new_alien.rect.width, -new_alien.rect.width) #start just off screen
                    if x == (self.settings.screen_width+ new_alien.rect.width):
                        new_alien.speed = self.settings.interceptor_speed
                    elif x == (-new_alien.rect.width):
                        new_alien.speed = -self.settings.interceptor_speed

                    new_alien.spawn_pos(x,y)
                    self.aliens.add(new_alien)
                    self.next_interceptor_spawn = now + (self.settings.interceptor_spawn_interval_base - self.current_wave_num*1000)
            
         
                    
            x = self.player_id.rect.midtop #start facing the player.
            y = -new_alien.rect.height #start just off screen
            new_alien.spawn_pos(x,y)

            self.aliens.add(new_alien)



    def fire_alien_bullet(self, alien, alien_level, level1_3_already_fired=False):
        """helper function  for update_game() to fire alien bullets.
        level1_3_already_fired: If True, a level 1-3 alien already fired this frame (prevents sound overlap).""" 
        bullet_count = [] # Initialize an empty list to count bullets: 
        
        if alien_level == 1:
            max_bullets = self.settings.alien1_bullet_max
            owner_type = "alien"
        elif alien_level == 2:
            max_bullets = self.settings.alien2_bullet_max
            owner_type = "alien"
        elif alien_level == 3:
            max_bullets = self.settings.alien3_bullet_max
            owner_type = "alien"
        #alien level 4 is not listed, since it does not fire any bullets.
        elif alien_level == 5: #destroyer
            max_bullets = self.settings.destroyer_bullet_max
            owner_type ="alien"
        elif alien_level == 6: #and element == "main": #cruisers have three parts; core, left wing, right wing. wings die if core dies; wings stop firing if they die, but core survives
            max_bullets = self.settings.cruiser_bullet_max
            owner_type = "alien"
        #elif alien_level == 6 and element == "addon":
            #max_bullets = self.settings_cruiser_wings_bullet_max # this should be set in settings to whatever will allow the wing to fire two tiny bullets side-by-side.
            #owner_type = "alien"
        elif alien_level == 7: #lazertanker still operates as one big thing.
            max_bullets = self.settings.laztanker_bullet_max
            owner_type = "alien"
        #eventually add higher classes of alien here, and finally, the boss alien. 
        #elif alien_level == 8: #and element == "main":
          #  max_bullets = self.settings.gunship_bullet_max
         #   owner_type = "alien"
        #elif alien_level == 8 and element == "plasma_gun": #FOR THE BIG PLASMA CANNON
        #elif alien_level ==8 and element == addon: #FOR THE SMALL TURRETS
        
        else: #for boss alien or other levels
             max_bullets=self.settings.boss_bullet_max
             owner_type = "alien"

        #The for loop to count bullets:
        for b in self.alien_bullets: #for every sprite found in the alien_bullets group 
            if hasattr(b, 'owner_ref') and b.owner_ref == alien: #if its owner parameter is the alien in question
                bullet_count.append(b)
        #if statement to enforce bullet cap:
        if len(bullet_count) >= max_bullets: #if the sprite under iteration has its proper max bullets attributed to it:
            # Stop lasertanker firing sound if bullet cap reached
            if alien_level == 7 and alien in self.audio.lasertanker_firing_sound_channels:
                channel = self.audio.lasertanker_firing_sound_channels[alien]
                if channel:
                    channel.stop()
                del self.audio.lasertanker_firing_sound_channels[alien]
            return #limit the function to not fire another bullet, but end here.
        #otherwise, mmake a new bullet for that alien:
        bullet = Bullet(settings=self.settings, screen=self.screen, 
                        x=alien.rect.centerx, y=alien.rect.bottom, direction=1,
                        owner_type=owner_type, owner_level=alien_level, owner_ref=alien)
        self.alien_bullets.add(bullet) #add the bullet to the Alien Bullets sprite group.

        #take care of sound effects:
        if alien_level == 1 and not level1_3_already_fired:
            self.audio.play("alien_lvl1_shot")  # Level 1 aliens fire
        elif alien_level == 2 and not level1_3_already_fired:
            self.audio.play("alien_lvl2_shot")  # Level 2 aliens fire
        elif alien_level == 3 and not level1_3_already_fired:
            self.audio.play("alien_lvl3_shot")  # Level 3 aliens fire
        elif alien_level == 5:
            self.audio.play("alien_destroyer_shot")  # Destroyers fire
        elif alien_level == 6:
            self.audio.play("alien_cruiser_center_shot")  # Cruiser center body fires
        elif alien_level == 7:
            # Start constant firing sound if not already playing
            if alien not in self.audio.lasertanker_firing_sound_channels:
                channel = self.audio.play("alien_laztanker_shot", loop=-1)
                if channel:
                    self.audio.lasertanker_firing_sound_channels[alien] = channel
            else:
                # Check if channel is still playing, restart if not
                channel = self.audio.lasertanker_firing_sound_channels[alien]
                if not channel or not channel.get_busy():
                    channel = self.audio.play("alien_laztanker_shot", loop=-1)
                    if channel:
                        self.audio.lasertanker_firing_sound_channels[alien] = channel


    def _check_fleet_edges(self):
        """a helper function for update_game() to check the screen edges and make sure the level one fleet aliens don't go off screen."""
        for alien in self.aliens:
            if alien.level == 1 and alien.check_edge_for_fleet(): #If the alien class method ".check_edge_for_fleet" returns the boolean "True,"
                 self._change_fleet_direction() #execute a direction change for the fleet.
                 break
    
    
    def _change_fleet_direction(self):
        """helper function for _check_fleet_edges() - the motor that bounces level1 fleets them back from edges"""
        self.settings.fleet_direction *= -1 #crucial: the point of all this. If ay lvl 1 alien has hit an edge, then the whole fleet changes direction. 
    

    def _alien_firing_logic(self):
        """helper function for _update_game() - check if each alien is ready to fire, and if so, create a bullet object at the appropriate level."""
        now = pygame.time.get_ticks() #get current time
        level1_3_fired_this_frame = False  # Track if any level 1-3 alien fired to limit sound overlap
        for alien in self.aliens:
             if alien.ready_to_fire(now): #is alien fire timer set to current time?
                  self.fire_alien_bullet(alien, alien.level, level1_3_fired_this_frame) #then fire a bullet
                  if alien.level in (1, 2, 3):
                      level1_3_fired_this_frame = True  # Mark that a level 1-3 alien fired
             # Check for cruiser wing firing (independent of main gun)
             # Wings stop firing when cruiser reaches 3rd damage image (cruiser_dmg3.png) or higher
             if alien.level == 6 and hasattr(alien, 'next_wing_fire_time') and now >= alien.next_wing_fire_time:
                 # Check if cruiser is on 3rd damage image or higher (damage_stage >= 13 for cruiser_dmg3.png)
                 if alien.damage_stage < 13:  # cruiser_dmg3.png starts at damage_stage 13
                     self._fire_cruiser_wing_bullets(alien, first_shot=True)  # Fire first shot immediately
                     # Schedule second shot 1 second (1000ms) later
                     alien.next_wing_second_shot_time = now + 1000
                 alien.next_wing_fire_time = now + random.randint(self.settings.cruiser_wing_min_fire_interval, self.settings.cruiser_wing_max_fire_interval)
             # Check for second wing shot (1 second after first)
             if alien.level == 6 and hasattr(alien, 'next_wing_second_shot_time') and alien.next_wing_second_shot_time is not None and now >= alien.next_wing_second_shot_time:
                 if alien.damage_stage < 13 and alien.alive():  # Only fire if cruiser still alive
                     self._fire_cruiser_wing_bullets(alien, first_shot=False)  # Fire second shot
                 alien.next_wing_second_shot_time = None  # Clear the timer
    
    def _minion_firing_logic(self):
        """helper function for _update_game() - check if each minion is ready to fire, and if so, create appropriate projectiles."""
        now = pygame.time.get_ticks() #get current time
        for minion in self.minions:
            if minion.ready_to_fire(now): #is minion fire timer set to current time?
                if minion.minion_type == "laser":
                    # Play laserminion firing sound
                    self.audio.play("alien_laserminion_shot")
                    # Create LaserminionBomb
                    bomb = LaserminionBomb(self.settings, self.screen,
                                          minion.rect.centerx, minion.rect.bottom)
                    self.alien_bullets.add(bomb) #add to alien bullets group

    def _cruiser_collision_valid(self, alien, bullet_rect):
        """Check if a bullet's rect collision with a cruiser (level 6) is valid.
        Returns False if bullet overlaps wing bottom area (left/right thirds, bottom half).
        Returns True otherwise."""
        if alien.level != 6:
            return True  # Not a cruiser, always valid
        
        alien_left = alien.rect.left
        alien_right = alien.rect.right
        alien_width = alien.rect.width
        alien_top = alien.rect.top
        alien_height = alien.rect.height
        
        # Calculate thirds
        left_third_end = alien_left + (alien_width / 3)
        right_third_start = alien_right - (alien_width / 3)
        wing_midpoint = alien_top + (alien_height / 2)  # Middle of sprite
        
        # Check if bullet rect overlaps with the invalid wing bottom areas
        # Invalid areas: left third (bottom half) and right third (bottom half)
        bullet_left = bullet_rect.left
        bullet_right = bullet_rect.right
        bullet_top = bullet_rect.top
        bullet_bottom = bullet_rect.bottom
        
        # Check if other rect overlaps center third (valid area - any Y position)
        overlaps_center = bullet_right > left_third_end and bullet_left < right_third_start
        
        # Check if other rect overlaps top half (valid area - any X position)
        overlaps_top = bullet_bottom > alien_top and bullet_top < wing_midpoint
        
        # If overlaps center third OR top half, collision is valid
        if overlaps_center or overlaps_top:
            return True
        
        # Check if other rect overlaps left wing bottom area (invalid)
        overlaps_left_wing_bottom = (
            bullet_right > alien_left and 
            bullet_left < left_third_end and
            bullet_bottom > wing_midpoint and
            bullet_top < alien.rect.bottom
        )
        
        # Check if other rect overlaps right wing bottom area (invalid)
        overlaps_right_wing_bottom = (
            bullet_right > right_third_start and
            bullet_left < alien_right and
            bullet_bottom > wing_midpoint and
            bullet_top < alien.rect.bottom
        )
        
        # If only overlaps wing bottom areas, collision is invalid
        if overlaps_left_wing_bottom or overlaps_right_wing_bottom:
            return False
        
        # Default: valid (shouldn't reach here if rects overlap)
        return True

    def _destroyer_collision_valid(self, alien, other_rect):
        """
        Destroyer (level 5) custom hitbox filter.

        Excludes collisions in the two outer 25% bands of the *front half* of the sprite.
        (Aliens approach from top, so we treat \"front\" as the LOWER half of the sprite.)

        Returns True if other_rect overlaps the *allowed* collision area.
        Returns False if other_rect overlaps only the excluded zones.
        """
        if getattr(alien, "level", None) != 5:
            return True

        w = alien.rect.width
        h = alien.rect.height
        half_h = int(h * 0.5)
        outer_w = int(w * 0.28)

        # Allowed collision area:
        # - Back half: full width
        # - Front half: center 50% width (exclude outer 25% on each side)
        back_half = pygame.Rect(alien.rect.left, alien.rect.top, w, half_h)
        front_center = pygame.Rect(
            alien.rect.left + outer_w,
            alien.rect.top + half_h,
            max(1, w - (2 * outer_w)),
            max(1, h - half_h),
        )

        return other_rect.colliderect(back_half) or other_rect.colliderect(front_center)

    def _fire_cruiser_wing_bullets(self, alien, first_shot=True):
        """Fire small ordinary alien bullets from cruiser wing positions.
        Bullets originate from the forward (bottom) midpoints of each wing.
        first_shot: If True, this is the first shot; if False, this is the second shot 1 second later."""
        if alien.level != 6:
            return  # Only for cruisers
        
        # Calculate wing firing positions based on collision box logic
        alien_left = alien.rect.left
        alien_right = alien.rect.right
        alien_width = alien.rect.width
        alien_top = alien.rect.top
        alien_height = alien.rect.height
        
        # Left wing: move outward from center (further left) and downward toward nose
        # Start at left third boundary, then move outward by 5% of width
        left_wing_x = alien_left + (alien_width / 6)
        # Right wing: move outward from center (further right) and downward toward nose
        # Start at right third boundary, then move outward by 5% of width
        right_wing_x = alien_right - (alien_width / 6)
        # Move downward toward nose: from midpoint, move down by 10% of height
        wing_y = alien_top + (alien_height / 2) + (alien_height * 0.10)
        
        # Fire from left wing
        left_bullet = Bullet(
            settings=self.settings, 
            screen=self.screen,
            x=left_wing_x, 
            y=wing_y,
            direction=1,
            owner_type="alien",
            owner_level=5,  # Use level 5 for destroyer bullets (size and color)
            owner_ref=alien
        )
        self.alien_bullets.add(left_bullet)
        
        # Fire from right wing
        right_bullet = Bullet(
            settings=self.settings,
            screen=self.screen,
            x=right_wing_x,
            y=wing_y,
            direction=1,
            owner_type="alien",
            owner_level=5,  # Use level 5 for destroyer bullets (size and color)
            owner_ref=alien
        )
        self.alien_bullets.add(right_bullet)
        # Play sound for each shot (both first and second)
        self.audio.play("alien_cruiser_wing_shot")  # Cruiser wing bullets 

    def _do_collisions(self):
        """Helper for update_game() that handles collisions between shields, player bullets/alien ships, alien bullets/player ship, and alien ships/player ships, in that order."""
        # Shields absorb/regen if enabled
        if self.settings.orbital_shields_enabled and self.shields:
            # player bullets charge shields toward regen
            # Mobile shields: owner's bullets pass through, other players' bullets recharge
            hits = pygame.sprite.groupcollide(self.player_bullets, self.shields, False, False)
            bullets_to_kill = []
            for bullet, shields_hit in hits.items():
                hit_shield = False
                for shield in shields_hit:
                    # Check if this is a mobile shield (mom-created)
                    if hasattr(shield, 'tracked_player') and shield.tracked_player:
                        # Mobile shield: check if bullet owner matches shield owner
                        if (hasattr(bullet, 'owner_ref') and bullet.owner_ref and 
                            hasattr(bullet.owner_ref, 'player_id') and
                            bullet.owner_ref.player_id == shield.tracked_player.player_id):
                            # Owner's bullet passes through
                            continue
                        else:
                            # Other player's bullet recharges the shield
                            if shield.heal(1):  # Recharge by 1 stage, returns True if stage improved
                                self.audio.play("shield_recharge")  # Play sound when shield stage improves
                            # Track shield recharge shot
                            if hasattr(bullet, 'owner_ref') and hasattr(bullet.owner_ref, 'player_id'):
                                player_id = bullet.owner_ref.player_id
                                if player_id in self.player_stats:
                                    self.player_stats[player_id]['shield_recharge_shots'] += 1
                            hit_shield = True
                    else:
                        # Stationary shield - recharge it
                        if shield.register_recharge_hit():  # Returns True if stage improved
                            self.audio.play("shield_recharge")  # Play sound when shield stage improves
                        # Track shield recharge shot
                        if hasattr(bullet, 'owner_ref') and hasattr(bullet.owner_ref, 'player_id'):
                            player_id = bullet.owner_ref.player_id
                            if player_id in self.player_stats:
                                self.player_stats[player_id]['shield_recharge_shots'] += 1
                        hit_shield = True
                # Kill bullet if it hit a shield (and wasn't owner's bullet on mobile shield)
                if hit_shield:
                    bullets_to_kill.append(bullet)
            # Remove bullets that hit shields
            for bullet in bullets_to_kill:
                bullet.kill()

            # alien bullets damage shields
            hits = pygame.sprite.groupcollide(self.alien_bullets, self.shields, True, False)
            for bullet, shields_hit in hits.items():
                # Check for NyancatBullet (double damage to shields)
                is_nyancat_bullet = isinstance(bullet, NyancatBullet)
                is_laserminion_bomb = isinstance(bullet, LaserminionBomb)
                
                # Determine sound based on bullet owner level
                bullet_owner_level = getattr(bullet, 'owner_level', 1)
                bullet_owner_type = getattr(bullet, 'owner_type', 'alien')
                if bullet_owner_type == "kitty":
                    # Kitty bullets: bluewhale (13) is large, others are small
                    if bullet_owner_level == 13:  # Bluewhalekitty
                        self.audio.play("shield_hit_big_bullet")
                    else:
                        self.audio.play("shield_hit_small_bullet")  # Loafkitty, centurion, emperor
                elif bullet_owner_level in (1, 2, 3):
                    self.audio.play("shield_hit_small_bullet")  # Bullets from levels 1-3
                elif bullet_owner_level in (5, 6):  # Destroyer (5) or cruiser wing/main (6)
                    self.audio.play("shield_hit_big_bullet")  # Bullets from destroyer/cruiser
                # Note: Cruiser center bullet (level 6 main) will use big_bullet sound
                
                # Determine damage (NyancatBullet does double damage)
                damage = 2 if is_nyancat_bullet else 1
                for shield in shields_hit:
                    shield.take_damage(damage)
                
                # Kill bullet after impact (NyancatBullet and LaserminionBomb disappear after impact)
                if (is_nyancat_bullet or is_laserminion_bomb) and bullet.alive():
                    bullet.kill()
                # Note: Normal bullets are already killed by groupcollide (dokill=True)

            # big aliens collide with shields
            hits = pygame.sprite.groupcollide(self.aliens, self.shields, False, False)
            for alien, shields_hit in hits.items():
                # For cruisers, check if collision is valid (not in wing top area)
                if alien.level == 6:
                    # Check collision using shield rect (use first shield's rect as approximation)
                    if shields_hit:
                        shield_rect = shields_hit[0].rect
                        if not self._cruiser_collision_valid(alien, shield_rect):
                            continue  # Skip this collision
                    else:
                        continue  # No shields, skip
                # For destroyers, exclude front-half outer quarters
                if alien.level == 5:
                    if shields_hit:
                        shield_rect = shields_hit[0].rect
                        if not self._destroyer_collision_valid(alien, shield_rect):
                            continue
                    else:
                        continue
                
                dmg = None  # level-based damage
                if alien.level in (1, 2, 3):
                    dmg = 1
                elif alien.level == 4:
                    dmg = 3
                elif alien.level == 5:
                    dmg = 4
                elif alien.level == 6:
                    dmg = 5
                elif alien.level == 7:
                    dmg = 100  # lazertankers obliterate shields completely

                if dmg is not None:
                    for shield in shields_hit:
                        shield.take_damage(dmg)  # apply collision damage
                    # Play appropriate collision sound based on alien level
                    if alien.level in (1, 2, 3):
                        self.audio.play("shield_collide_small_alien")  # Levels 1-3 collide with shield
                    elif alien.level == 4:
                        self.audio.play("alien_lvl4_collision")  # Level 4 collision sound
                        # Stop level 4 hum sound if this alien was playing it
                        if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                            alien.hum_sound_channel.stop()
                            alien.hum_sound_channel = None
                    elif alien.level == 5:
                        self.audio.play("alien_destroyer_death")  # Destroyer death sound
                        # Stop hum sound if this alien was playing it
                        if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                            alien.hum_sound_channel.stop()
                            alien.hum_sound_channel = None
                    elif alien.level == 6:
                        self.audio.play("alien_cruiser_death")  # Cruiser death sound
                        # Stop hum sound if this alien was playing it
                        if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                            alien.hum_sound_channel.stop()
                            alien.hum_sound_channel = None
                    elif alien.level == 7:
                        self.audio.play("alien_laztanker_death")  # Lasertanker death sound
                        # Stop hum sound if this alien was playing it
                        if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                            alien.hum_sound_channel.stop()
                            alien.hum_sound_channel = None
                        # Stop lasertanker firing sound
                        if alien in self.audio.lasertanker_firing_sound_channels:
                            channel = self.audio.lasertanker_firing_sound_channels[alien]
                            if channel:
                                channel.stop()
                            del self.audio.lasertanker_firing_sound_channels[alien]
                    # Create death animations for big aliens
                    if alien.level == 7:
                        death_anim = LazertankerDeathAnimation(
                            self.settings,
                            self.screen,
                            alien.rect.center,
                            alien.rect.size
                        )
                        self.lazertanker_death_animations.add(death_anim)
                    elif alien.level == 6:
                        death_anim = CruiserDeathAnimation(
                            self.settings,
                            self.screen,
                            alien.rect.center,
                            alien.rect.size
                        )
                        self.cruiser_death_animations.add(death_anim)
                    elif alien.level == 5:
                        death_anim = DestroyerDeathAnimation(
                            self.settings,
                            self.screen,
                            alien.rect.center,
                            alien.rect.size
                        )
                        self.destroyer_death_animations.add(death_anim)
                    # Stop level 4 hum sound if this alien was playing it
                    if alien.level == 4 and hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                        alien.hum_sound_channel.stop()
                        alien.hum_sound_channel = None
                    alien.kill()  # shield collision destroys these alien types

        #-----Tracking collisions betweel PLAYER BULLETS and ALIEN SHIPS:
        # For cruisers, we need custom collision checking, so we'll handle them separately
        # First, get collisions without killing bullets yet
        alien_is_hit = pygame.sprite.groupcollide(self.player_bullets, self.aliens, False, False)
        for bullet, aliens_hit in alien_is_hit.items():
                # Filter out invalid cruiser collisions before processing
                valid_aliens = []
                for alien in aliens_hit:
                    # Custom collision check for cruisers (level 6) - wings only collide in bottom half
                    if alien.level == 6:
                        # Check if bullet rect collision is valid (not in wing top area)
                        if not self._cruiser_collision_valid(alien, bullet.rect):
                            continue  # Skip this collision - don't add to valid_aliens
                    # Custom collision check for destroyers (level 5) - exclude front-half outer quarters
                    if alien.level == 5:
                        if not self._destroyer_collision_valid(alien, bullet.rect):
                            continue
                    valid_aliens.append(alien)
                
                # Only process collision if there are valid aliens
                if not valid_aliens:
                    continue  # No valid collisions, bullet continues
                
                # Track bullet hit (for accuracy calculation) - track once per bullet hit
                if hasattr(bullet, 'owner_ref') and hasattr(bullet.owner_ref, 'player_id'):
                    player_id = bullet.owner_ref.player_id
                    if player_id in self.player_stats:
                        self.player_stats[player_id]['bullets_hit'] += 1
                
                # Play bullet hit sound
                self.audio.play("bullet_hit")
                
                # Now kill the bullet since we have valid collisions
                bullet.kill()
                
                # Process collisions with valid aliens only
                for alien in valid_aliens:
                    destroyed = False
                    if alien.level in (1,2,3,4): #aliens at levels 1-4 only need 1 hit to destroy them.
                        #TODO: make this a menu option: remove level 2 aliens from the possibility of bullets hitting them; but make them cause 0 damage to players if players collide with them - meaning, you have to collide with them to kill them)
                        destroyed = True
                    elif alien.level in (5,6,7,8): #aliens at levels 5-8 need multiple hits; a function in the alien.py file allows variety based on class.
                        destroyed = alien.check_destruction() #for aliens with hitpoints, the .destroyed() function in alien.py will return a True or False depending on -->
                                                    #--> how many times the alien has been hit.
                   #TODO: make level 2 aliens impervious to bullets, but deal 0 damage when colllided with - in effect, you ahve to mop them up. 
                    #kill the alien, if the above code determines it has been destroyed. Play the appropriate sound for each kind of death:
                    if destroyed:
                        # Death by bullet (this section handles bullet kills)
                        #if alien.level in (1, 2, 3): #commented out to see if sound runs better. If commented back in, 
                            #self.audio.play("alien_lvl1to3_death")  # Levels 1-3 killed by bullet
                        if alien.level == 4:
                            self.audio.play("alien_lvl1to3_death")  # Level 4 killed by bullet (not collision)
                            # Stop level 4 hum sound if this alien was playing it
                            if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                                alien.hum_sound_channel.stop()
                                alien.hum_sound_channel = None
                        # Note: Level 4 collision deaths use alien_lvl4_collision (handled in collision section)
                        elif alien.level == 5:
                            self.audio.play("alien_destroyer_death")  # Destroyer death
                            # Stop hum sound if this alien was playing it
                            if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                                alien.hum_sound_channel.stop()
                                alien.hum_sound_channel = None
                        elif alien.level == 6:
                            self.audio.play("alien_cruiser_death")  # Cruiser death
                            # Stop hum sound if this alien was playing it
                            if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                                alien.hum_sound_channel.stop()
                                alien.hum_sound_channel = None
                        elif alien.level == 7:
                            self.audio.play("alien_laztanker_death")  # Lasertanker death
                            # Stop hum sound if this alien was playing it
                            if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                                alien.hum_sound_channel.stop()
                                alien.hum_sound_channel = None
                            # Stop lasertanker firing sound
                            if alien in self.audio.lasertanker_firing_sound_channels:
                                channel = self.audio.lasertanker_firing_sound_channels[alien]
                                if channel:
                                    channel.stop()
                                del self.audio.lasertanker_firing_sound_channels[alien]
                              # elif alien.level == 8:
                              #   self.audio.play("gunship_explosion")
                        # else:
                        #   self.audio.play("boss_explosion")  # Commented out - sound not loaded

                        # Create lasertanker death animation if it's a lasertanker
                        if alien.level == 7:
                            death_anim = LazertankerDeathAnimation(
                                self.settings,
                                self.screen,
                                alien.rect.center,
                                alien.rect.size
                            )
                            self.lazertanker_death_animations.add(death_anim)
                        # Create cruiser death animation if it's a cruiser
                        elif alien.level == 6:
                            death_anim = CruiserDeathAnimation(
                                self.settings,
                                self.screen,
                                alien.rect.center,
                                alien.rect.size
                            )
                            self.cruiser_death_animations.add(death_anim)
                        # Create destroyer death animation if it's a destroyer
                        elif alien.level == 5:
                            death_anim = DestroyerDeathAnimation(
                                self.settings,
                                self.screen,
                                alien.rect.center,
                                alien.rect.size
                            )
                            self.destroyer_death_animations.add(death_anim)

                        alien.kill()
                        self._maybe_spawn_powerup_from_alien(alien)

                        #after the alien is killed, take care of incrementing player score up - in order to make "boss" level work, I use a try+except; the try requires-->
                        # -->that the alien level be a number that can run through a scoring equation.        
                        # Only award points if bullet has an owner_ref (player bullets should always have one, but check for safety)
                        # Skip scoring for lifepod kills - lifepods don't earn points
                        if bullet.owner_ref is not None and hasattr(bullet.owner_ref, 'player_score'):
                            # Track enemy destroyed (works for both player bullets and squadron bullets)
                            if hasattr(bullet.owner_ref, 'player_id') and bullet.owner_ref.player_id in self.player_stats:
                                self.player_stats[bullet.owner_ref.player_id]['enemies_destroyed'] += 1
                            try:
                                bullet.owner_ref.player_score += alien.level * ((alien.level* 1/2)*20) #scoring equation - note it has to have an integer as the alien level.
                            except (TypeError, AttributeError): #since "boss" level is a string, a try/except works well here to score the boss, without having to change the overall scoring equation above.
                                #player who killed boss alien gets 50,000 points;
                                bullet.owner_ref.player_score += 50000
                                #other players get 10,000 points
                                for player in self.players:
                                    if player.player_id != bullet.owner_ref.player_id:
                                        player.player_score += 10000

        #-----Tracking collisions between PLAYER BULLETS and MINIONS:
        minion_is_hit = pygame.sprite.groupcollide(self.player_bullets, self.minions, False, False)
        for bullet, minions_hit in minion_is_hit.items():
            # Track bullet hit (for accuracy calculation) - track once per bullet hit
            if hasattr(bullet, 'owner_ref') and hasattr(bullet.owner_ref, 'player_id'):
                player_id = bullet.owner_ref.player_id
                if player_id in self.player_stats:
                    self.player_stats[player_id]['bullets_hit'] += 1
            
            # Kill the bullet
            bullet.kill()

            # Process collisions with minions
            for minion in minions_hit:
                destroyed = minion.check_destruction()
                if destroyed:
                    # Score based on minion level
                    if hasattr(bullet, 'owner_ref') and hasattr(bullet.owner_ref, 'player_score'):
                        bullet.owner_ref.player_score += minion.level * 10  # 10 points per minion level
                        # Track enemy destroyed (minion)
                        if hasattr(bullet.owner_ref, 'player_id') and bullet.owner_ref.player_id in self.player_stats:
                            self.player_stats[bullet.owner_ref.player_id]['enemies_destroyed'] += 1

                    # Play explosion sound
                    # self.audio.play("medium_explosion")  # Commented out - no sound files available

                    # Kill the minion
                    minion.kill()

        # Lifepod-alien collisions (trigger respawn animation)
        lifepod_hits = pygame.sprite.groupcollide(self.lifepods, self.aliens, False, False)
        for lifepod, aliens_hit in lifepod_hits.items():
            if lifepod.state == "normal":  # Only trigger if not already respawning
                for alien in aliens_hit:
                    # Trigger lifepod respawn animation
                    lifepod.start_respawn()
                    break  # Only trigger once per collision

        # Lifepod-alien bullet collisions (trigger respawn animation)
        lifepod_bullet_hits = pygame.sprite.groupcollide(self.lifepods, self.alien_bullets, False, True)
        for lifepod, bullets_hit in lifepod_bullet_hits.items():
            if lifepod.state == "normal" and bullets_hit:  # Only trigger if not already respawning
                # Trigger lifepod respawn animation
                lifepod.start_respawn()
                break  # Only trigger once per collision

        #laser_hits_alien = pygame.sprite.groupcollide(self.aliens, self.laser, True, False)
        #laser_hits_minion = pygame.sprite.groupcollide(self.minions, self.laser, True, False)
        #shockwave_hits_alien = pygame.sprite.groupcollide(self.aliens, self.shockwaves, True, False) #shockwaves tear through aliens.
        shockwave_hits_minion = pygame.sprite.groupcollide(self.minions, self.shockwaves, True, False)  # shockwaves destroy minions 

    #-----Tracking collisions between ALIEN BULLETS and SQUADRONS:
        squadron_is_hit = pygame.sprite.groupcollide(self.alien_bullets, self.squadrons, True, False)
        for bullet, squadrons_hit in squadron_is_hit.items():
            # Play bullet hit sound
            self.audio.play("bullet_hit")
            is_laserminion_bomb = isinstance(bullet, LaserminionBomb)
            for squadron in squadrons_hit:
                was_alive = squadron.alive()  # Check if squadron was alive before taking hit
                squadron.take_hit(1)
                # Play death sound if squadron just died
                if was_alive and not squadron.alive():
                    self.audio.play("powerup_squadron_death")
                
                # Apply LaserminionBomb knockback
                if is_laserminion_bomb:
                    # LaserminionBomb: sideways knockback (1/2 squadron width)
                    # Direction: if bomb hits LEFT of centerx, bump RIGHT; if RIGHT of centerx, bump LEFT
                    if bullet.rect.centerx < squadron.rect.centerx:
                        direction = 1  # Bump right
                    else:
                        direction = -1  # Bump left
                    bump_distance = squadron.rect.width // 2
                    squadron.rect.x += direction * bump_distance
                    # Clamp to screen bounds
                    if squadron.rect.left < 0:
                        squadron.rect.left = 0
                    if squadron.rect.right > self.settings.screen_width:
                        squadron.rect.right = self.settings.screen_width
                    # Update squadron's internal position if it has one
                    if hasattr(squadron, 'x'):
                        squadron.x = float(squadron.rect.x)
            # Kill bullet after impact (LaserminionBomb disappears, normal bullets already killed by groupcollide)
            if is_laserminion_bomb and bullet.alive():
                bullet.kill()

    #-----Tracking collisions between LEVEL 4 ALIENS and SQUADRONS:
        for alien in self.aliens:
            if alien.level == 4:
                hits = pygame.sprite.spritecollide(alien, self.squadrons, dokill=False)
                if hits:
                    self.audio.play("alien_lvl4_collision")  # Level 4 collision sound
                    # Stop level 4 hum sound if this alien was playing it
                    if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                        alien.hum_sound_channel.stop()
                        alien.hum_sound_channel = None
                    for squadron in hits:
                        # Play death sound for each squadron killed
                        if squadron.alive():
                            self.audio.play("powerup_squadron_death")
                        squadron.kill()  # Level 4 aliens instantly kill squadrons
                    alien.kill()  # Level 4 aliens also die on collision

    #-----Tracking collisions between an ALIEN BULLETS and PLAYER SHIPS:
        player_is_hit = pygame.sprite.groupcollide(self.alien_bullets, self.players, False, False)
        if player_is_hit:
             # Play bullet hit sound
             self.audio.play("bullet_hit")
             for bullet, ships_hit in player_is_hit.items(): #note that in this for loop, the order of the two iterating variables has to match the -->
                                                            #--> Order of their corresponding parameter in the collision parameters.
                # Check for special bullet types (once per bullet, not per ship)
                is_nyancat_bullet = isinstance(bullet, NyancatBullet)
                is_laserminion_bomb = isinstance(bullet, LaserminionBomb)
             
                for ship in ships_hit:
                  #If ship is respawning:
                  if ship.player_state in ("between_lives", "respawning"): 
                        continue #skip that ship and continue to the next one if it's not alive. Respawning ships cannot fire bullets.
                
                  #otherwise, go through all the needed rigmarole to figure out if the player just died, adjust player health, announce, etc. 
                  else: 
                    # Determine damage
                    if is_nyancat_bullet:
                        damage = 2  # Double damage for NyancatBullet
                    else:
                        damage = 1  # Normal damage
                    
                    ship.player_health -= damage
                    # Track damage taken
                    if ship.player_id in self.player_stats:
                        self.player_stats[ship.player_id]['damage_taken'] += damage
                    self._trigger_hud_flash(ship, "hp")
                    self.audio.play("bullet_hit")
                    ship.trigger_hit_animation(350)  # Trigger hit animation (shorter than HUD flash duration)
#                    print (f"PLAYER ID {ship.player_id}, your ship was just hit and you now have {ship.player_health} health left!") #print announcement in log
                    
                    # Apply knockback effects
                    if is_nyancat_bullet:
                        # NyancatBullet: knockback downward by ship height
                        knockback_distance = ship.rect.height
                        ship.rect.y += knockback_distance
                        # Clamp to screen bounds
                        if ship.rect.bottom > self.settings.play_height:
                            ship.rect.bottom = self.settings.play_height
                        ship.y = float(ship.rect.y)
                    elif is_laserminion_bomb:
                        # LaserminionBomb: sideways knockback (1/2 ship width)
                        # Direction: if bomb hits LEFT of centerx, bump RIGHT; if RIGHT of centerx, bump LEFT
                        if bullet.rect.centerx < ship.rect.centerx:
                            direction = 1  # Bump right
                        else:
                            direction = -1  # Bump left
                        bump_distance = ship.rect.width // 2
                        ship.rect.x += direction * bump_distance
                        # Clamp to screen bounds
                        if ship.rect.left < 0:
                            ship.rect.left = 0
                        if ship.rect.right > self.settings.screen_width:
                            ship.rect.right = self.settings.screen_width
                        ship.x = float(ship.rect.x)
                    
                    #if that hit took your last health, you lose a life"
                    if ship.player_health <= 0:
                        ship.player_lives -= 1
                        # Track lives lost
                        if ship.player_id in self.player_stats:
                            self.player_stats[ship.player_id]['lives_lost'] += 1
                        self._trigger_hud_flash(ship, "lives")
                        self.audio.play("player_life_lost")
#                        print (f"Player {ship.player_id} has lost a life and now has {ship.player_lives} lives left!")
                        
                        ship.player_health = ship.current_max_health #reset player health.
                        #if you've not lost your last life, respawn timer starts for you:
                        if ship.player_lives >= 0:
                             self._start_player_respawn_timer(ship) #takes care of the animation and timing of respawn
                        #if you are out of lives, you die.
                        elif ship.player_lives < 0:
                            self._player_death(ship)
                           # self.audio.play("player_dead") #commented this out for now, since we dont' ahve separate player death sounds. Using life lost for now.
                            self.audio.play("player_life_lost")
                            #TODO: get a way to do life_lost messages that vary based on player name.
                # Kill bullet after processing all ships (NyancatBullet and LaserminionBomb disappear after impact)
                if (is_nyancat_bullet or is_laserminion_bomb) and bullet.alive():
                    bullet.kill()
                elif bullet.alive():
                    bullet.kill()  # Normal bullets also get killed        


        #-----Tracking collisions between ALIEN SHIPS and PLAYER SHIPS
        alien_collideswith_player = pygame.sprite.groupcollide(self.aliens, self.players, False, False)
        if alien_collideswith_player:
             for collided_alien, collided_player in list(alien_collideswith_player.items()):  
                  # For cruisers, check if collision is valid (not in wing top area)
                  if collided_alien.level == 6:
                      # Check collision using player rect
                      if collided_player:
                          player = collided_player[0]
                          if not self._cruiser_collision_valid(collided_alien, player.rect):
                              continue  # Skip this collision
                      else:
                          continue  # No player, skip
                  # For destroyers, exclude front-half outer quarters
                  if collided_alien.level == 5:
                      if collided_player:
                          player = collided_player[0]
                          if not self._destroyer_collision_valid(collided_alien, player.rect):
                              continue
                      else:
                          continue
                  self._player_alien_collision(collided_alien, collided_player)

    #helper:              
    def _player_alien_collision(self, collided_alien, collided_player):
                """helper for _do_collisions() to resolve alien/player ship collisions"""
                for player in collided_player:

                    #first check to see if they are respawning, and make collisions impossible:
                  if player.player_state in ("respawning", "between_lives"):
                         continue
                  else:
                    # Level 4 alien collision: 3 damage + knockback
                    if collided_alien.level == 4:
                        self.audio.play("alien_lvl4_collision")  # Level 4 collision sound
                        # Stop level 4 hum sound if this alien was playing it
                        if hasattr(collided_alien, 'hum_sound_channel') and collided_alien.hum_sound_channel:
                            collided_alien.hum_sound_channel.stop()
                            collided_alien.hum_sound_channel = None
                        
                        # Deal 3 damage
                        damage = 3
                        player.player_health -= damage
                        # Track damage taken
                        if player.player_id in self.player_stats:
                            self.player_stats[player.player_id]['damage_taken'] += damage
                        self._trigger_hud_flash(player, "hp")
                        player.trigger_hit_animation(450)  # Trigger hit animation
                        
                        # Knockback: move player backwards by their own ship length
                        ship_length = player.rect.height
                        # Move backwards (down the screen, towards bottom)
                        player.rect.y += ship_length
                        # Clamp to screen bounds
                        if player.rect.bottom > self.settings.play_height:
                            player.rect.bottom = self.settings.play_height
                        player.y = float(player.rect.y)
                        
                        # Level 4 alien dies on collision
                        collided_alien.kill()
                        # Track alien collision kill and enemy destroyed
                        if player.player_id in self.player_stats:
                            self.player_stats[player.player_id]['alien_collision_kills'] += 1
                            self.player_stats[player.player_id]['enemies_destroyed'] += 1
                        player.player_score += 300
                        
                        # Check if player died from this damage
                        if player.player_health <= 0:
                            player.player_lives -= 1
                            # Track lives lost
                            if player.player_id in self.player_stats:
                                self.player_stats[player.player_id]['lives_lost'] += 1
                            self._trigger_hud_flash(player, "lives")
                            self.audio.play("player_life_lost")
                            player.player_health = player.current_max_health  # Reset health
                            if player.player_lives >= 0:
                                self._start_player_respawn_timer(player)
                            elif player.player_lives < 0:
                                self._player_death(player)
                        continue  # Skip to next player
                    
                    # Big alien collision handling (levels 5-7): damage + knockback, alien takes 5 damage
                    if collided_alien.level in (5, 6, 7, 8):
                        damage = 2 if collided_alien.level == 5 else 4
                        player.player_health -= damage
                        self._trigger_hud_flash(player, "hp")
                        player.trigger_hit_animation(450)  # Trigger hit animation (matches HUD flash duration)
                        self.audio.play("player_collide")
                        bump_distance = (collided_alien.rect.width // 2) + (player.rect.width // 2) + 4
                        direction = -1 if player.rect.centerx < collided_alien.rect.centerx else 1
                        player.rect.x += direction * bump_distance
                        # clamp to screen bounds and sync float position
                        if player.rect.left < 0:
                            player.rect.left = 0
                        if player.rect.right > self.settings.screen_width:
                            player.rect.right = self.settings.screen_width
                        player.x = float(player.rect.x)
                        
                        # Apply 5 damage to the alien
                        collided_alien.damage_stage += 5
                        # Check if alien is destroyed
                        if collided_alien.level == 5:
                            frames = self.settings.destroyer_hitframes
                        elif collided_alien.level == 6:
                            frames = self.settings.cruiser_hitframes
                        elif collided_alien.level == 7:
                            frames = self.settings.laztanker_hitframes
                        else:
                            frames = None
                        
                        if frames and collided_alien.damage_stage > len(frames):
                            # Alien is destroyed
                            # Play death sound based on alien level
                            if collided_alien.level == 5:
                                self.audio.play("alien_destroyer_death")  # Destroyer death
                            elif collided_alien.level == 6:
                                self.audio.play("alien_cruiser_death")  # Cruiser death
                            elif collided_alien.level == 7:
                                self.audio.play("alien_laztanker_death")  # Lasertanker death
                            # Stop hum sound if this alien was playing it
                            if hasattr(collided_alien, 'hum_sound_channel') and collided_alien.hum_sound_channel:
                                collided_alien.hum_sound_channel.stop()
                                collided_alien.hum_sound_channel = None
                            # Stop lasertanker firing sound
                            if collided_alien in self.audio.lasertanker_firing_sound_channels:
                                channel = self.audio.lasertanker_firing_sound_channels[collided_alien]
                                if channel:
                                    channel.stop()
                                del self.audio.lasertanker_firing_sound_channels[collided_alien]
                            # Create lasertanker death animation if it's a lasertanker
                            if collided_alien.level == 7:
                                death_anim = LazertankerDeathAnimation(
                                    self.settings, 
                                    self.screen, 
                                    collided_alien.rect.center, 
                                    collided_alien.rect.size
                                )
                                self.lazertanker_death_animations.add(death_anim)
                            # Create cruiser death animation if it's a cruiser
                            elif collided_alien.level == 6:
                                death_anim = CruiserDeathAnimation(
                                    self.settings,
                                    self.screen,
                                    collided_alien.rect.center,
                                    collided_alien.rect.size
                                )
                                self.cruiser_death_animations.add(death_anim)
                            # Create destroyer death animation if it's a destroyer
                            elif collided_alien.level == 5:
                                death_anim = DestroyerDeathAnimation(
                                    self.settings,
                                    self.screen,
                                    collided_alien.rect.center,
                                    collided_alien.rect.size
                                )
                                self.destroyer_death_animations.add(death_anim)
                            collided_alien.kill()
                            self._maybe_spawn_powerup_from_alien(collided_alien)
                        elif frames and collided_alien.damage_stage > 0:
                            # Update alien image to show damage
                            frame_index = min(collided_alien.damage_stage - 1, len(frames) - 1)
                            collided_alien.image = frames[frame_index]
                            collided_alien.rect = collided_alien.image.get_rect(center=collided_alien.rect.center)
                    else:
                        player.player_health -= 1
                        self._trigger_hud_flash(player, "hp")
                        player.trigger_hit_animation(450)  # Trigger hit animation (matches HUD flash duration)
#                        print (f"Player {player.player_id} and a level {collided_alien.level} alien collided! Player {player.player_id}'s health is now {player.player_health}")
                        #self.audio.play("medium_explosion") 
                        self.audio.play("bullet_hit")
                        if collided_alien.level == 4:
                            player.player_health -= 3
                            player.player_score += 300
                            # Track alien collision kill
                            if player.player_id in self.player_stats:
                                self.player_stats[player.player_id]['alien_collision_kills'] += 1
                                self.player_stats[player.player_id]['enemies_destroyed'] += 1
                            # Note: hit animation already triggered above, no need to trigger again
#                            print (f"Player {player.player_id} used their ship as a shield, reducing them to {player.player_health} health. Their score is now {player.player_score}")

                                

              #handle any life losses or dead players..
                    if player.player_health <= 0: #begin by checking player health
                        player.player_lives -= 1 #drop a life if health is below zero.
                        # Track lives lost
                        if player.player_id in self.player_stats:
                            self.player_stats[player.player_id]['lives_lost'] += 1
                        self._trigger_hud_flash(player, "lives")
                        self.audio.play("player_life_lost")
#                        print (f"Player {player.player_id} has lost a life and now has {player.player_lives} lives left!")
                        player.player_health = player.current_max_health #reset player health.

                        #if the player still has lives left after colliding with an alien ship, start a respawn cycle
                        if player.player_lives >= 0:
                            self._start_player_respawn_timer(player)
                        #if they have no lives left, they die:
                        else:
                            self._player_death(player)   
                
                #level 1-4 aliens are destroyed by impact; bigger ones are not.
                    if collided_alien.level <= 4:
                          #TODO: add loud explosion kill sound here
                          collided_alien.kill()
                      
    def _trigger_hud_flash(self, ship, kind: str) -> None:
        """Start a short HUD flash for hp or lives."""
        now = pygame.time.get_ticks()
        if kind == "hp":
            ship.hp_flash_until_ms = now + 450
        elif kind == "lives":
            ship.lives_flash_until_ms = now + 1800

    def _player_death(self, player):
                        """Helper function for _do_collisions() and _player_alien_collisions() to execute player death tasks."""
                        player.player_state = "dead"
                        print(f"Player {player.player_id} has been killed!!!")
                        #self.audio.play("player_dead") TODO: elifs to say which sound to pick depending on player Name (could add name field for Eli, Audrey, Jakey, Etc.)
                        self.audio.play("player_life_lost") # for now, just use life lost for player death. TODO: differentiate. 
                        # Snapshot this player's score/powerups before removing them from the sprite group.
                        # Credits are built later by _store_final_player_data() (single source of truth).
                        if not hasattr(self, 'final_player_snapshots') or self.final_player_snapshots is None:
                            self.final_player_snapshots = {}
                        self.final_player_snapshots[player.player_id] = {
                            'player_score': player.player_score,
                            'powerups_used': dict(player.powerups_used),
                        }
                        
                        # Create lifepod if escape pods are enabled
                        if getattr(self.settings, 'enable_escape_pods', True):
                            lifepod = Lifepod_Squadron(self.settings, self.screen, player.player_id)
                            self.lifepods.add(lifepod)
                        
                        player.kill()
                        if len(self.players) <= 0:
                             self.game_state = "defeat"     
                             # bonus wave - use bonus wave defeat screen initialization
                             if self.is_bonus_wave:
                                 self._init_bonus_wave_defeat_screen()
                             else:
                                 self._init_defeat_screen()     
    
    def _start_player_respawn_timer(self, player):
        """Helper method for _do_collisions(); Begin a respawn cycle for the player's ship. This will shunt them to the bottom of the screen, make their sprite transparent and unhittable, and keep them from firing"""
        now = pygame.time.get_ticks()

        player.player_state = "between_lives"
        player.respawn_end_time = now + self.settings.player_respawn_time_ms
        player.y +=3
    
#-------WAVE DYNAMICS FUNCTIONS:    
    def _current_wave_has_finished_spawning(self) -> bool:
        """helper function for _update_game() - boolean function that returns 'True' 
        if there are no more aliens left to spawn for this wave and all aliens are dead."""
        done = (self.level1_rows_remaining == 0 and len(self.aliens)==0)
        return done
        #TODO: Drop "wave passed" animation here.
    

    def _new_wave_pause(self):
        """helper function for _update_game() to create a small breather between levels."""
        # Safety check: should not be called during bonus wave
        if self.is_bonus_wave or self.current_wave_num is None:
            return
        base_pause = self.settings.new_wave_pause
        growing_pause = (self.current_wave_num + 1) * 1000
        pause_ms = max(base_pause, growing_pause) #call up the predetermined pause length from base_settings, compare to current wave number and pick larger. -->
                                                                #-->This gives longer breaks at higher levels;  min break is 5 seconds.)
        now = pygame.time.get_ticks()
        self.next_wave_start_time = None # handled by phase machine now

        self.current_wave_num += 1 # CRUCIAL: HERE WE INCREMENT THE WAVE NUMBER UP by ONE!
        completed_wave_display = self.current_wave_num
        self.wave_banner_text = f"Wave {completed_wave_display} Complete!"
        banner_width = self.wave_complete_font.size(self.wave_banner_text)[0]
        self.wave_banner_x = -banner_width
        self.wave_banner_active = True
        self.between_wave_phase = "complete_banner"
        self.warp_banner_end_time = None

        if self.current_wave_num >=len(self.settings.wave_master_index):
             self.game_state = "victory"
             self._init_victory_screen()
             #self.audio.play("victory)")
             self.wave_banner_active = False
        else:
             self.game_state = "between_waves" #put the game state in 'between wave break' for the time determined above. 
             self.audio.play("announce_wave_clear")  # Play wave clear sound when banner appears          


    def _update_between_waves(self):
          """State machine to manage between-wave banners and progression."""
          if self.between_wave_phase is None:
               return
          now = pygame.time.get_ticks()

          if self.between_wave_phase == "complete_banner":
               if self.wave_banner_active:
                    self.wave_banner_x += self.wave_banner_speed
                    if self.wave_banner_x > self.settings.screen_width:
                         self.wave_banner_active = False
                         self.between_wave_phase = "warp_banner"
                         self.warp_banner_end_time = now + 3000
               return

          if self.between_wave_phase == "warp_banner":
               if self.warp_banner_end_time is not None and now >= self.warp_banner_end_time:
                    for ship in self.players: #first position all player ships toward the bottom of the screen, so they are not where aliens will spawn
                          ship.rect.bottom = int(self.settings.screen_height * 0.9)
                          ship.y = float(ship.rect.y)
                    self.audio.play("announce_new_wave")  # Play new wave sound when next wave starts
                    self._new_alien_wave(self.current_wave_num) #CREATE THE NEXT WAVE!
                    self.between_wave_phase = None
                    self.warp_banner_end_time = None
                    self.game_state = "playing" #CHANGE GAME STATE TO "PLAYING!"

    def _handle_alien_breaches(self):
         """helper function for the update_game() function to trigger defeat if we let too many aliens through."""
         for given_alien in self.aliens: #cycle through all aliens
              if given_alien.rect.top > self.settings.screen_height: #check if they've made it off the screen
                    if given_alien.level in (1,2,3,4):
                        self.breaches_this_wave += 1 #aliens level 1 - 4 count for a single breach each.
                    elif given_alien.level == 5:
                        self.breaches_this_wave += 3 #destroyers are a triple breach - introduces urgency to deal with them.
                    elif given_alien.level == 6:
                        self.breaches_this_wave += 4 #cruisers are a quadruple breach
                    elif given_alien.level == 7: 
                        self.breaches_this_wave += 5 #laser tankers are a quintuple breach
                    self.current_defense_strength = self.max_breach_tolerance - self.breaches_this_wave
                    #self.audio.play("alien_breach")
                    #gunships never move downscreen; so no need to account for their breachiness.
                    #TODO: Drop breach alert sound and/or animation (screen flash) in here
                    # Stop hum sound if this alien was playing it (levels 4-7) - fadeout when exiting screen
                    if given_alien.level in (4, 5, 6, 7) and hasattr(given_alien, 'hum_sound_channel') and given_alien.hum_sound_channel:
                        self.audio.stop_hum_channel(given_alien.hum_sound_channel)
                        given_alien.hum_sound_channel = None
                    given_alien.kill() #kill the alien once it's off screen and its breach has been registered.
                    
                    
                    if self.breaches_this_wave > self.max_breach_tolerance:
                        self.game_state = "defeat"
                        self._init_defeat_screen()
                        #self.audio.play("defeat")

    def _reset_to_menu_baselines(self) -> None:
        """Reset any settings that menu config will modify, to avoid compounding."""
        self.settings.wave_master_index = copy.deepcopy(self._base_wave_master_index)
        self.settings.level1_alien_starting_rows = self._base_level1_alien_starting_rows
        self.settings.fleet_advance_speed = self._base_fleet_advance_speed
        self.level1_reinforcements_threshhold = self._base_level1_reinforce_threshold
        self.settings.alien_bullet_width = self._base_alien_bullet_width
        self.settings.alien_bullet_height = self._base_alien_bullet_height
        self.settings.destroyer_bullet_width = self._base_destroyer_bullet_width
        self.settings.destroyer_bullet_height = self._base_destroyer_bullet_height
        self.settings.cruiser_bullet_width = self._base_cruiser_bullet_width
        self.settings.cruiser_bullet_height = self._base_cruiser_bullet_height
        self.settings.laztanker_bullet_width = self._base_laztanker_bullet_width
        self.settings.laztanker_bullet_height = self._base_laztanker_bullet_height
        self.settings.boss_bullet_width = self._base_boss_bullet_width
        self.settings.boss_bullet_height = self._base_boss_bullet_height

    def _starting_player_level_for_wave(self, wave_index) -> int:  # bonus wave - removed int type hint to allow None
        """
        Your existing rule:
        - starting wave 1–2 => level 0
        - starting wave 3   => level 1
        - starting wave 4   => level 2
        - starting wave 5   => level 2 (level 3 if Hard difficulty)
        - bonus wave => level 0 (wave_index is None)
        """
        # bonus wave - handle None case first (bonus wave mode)
        if wave_index is None or not isinstance(wave_index, int):
            return 0
        starting_wave_num = wave_index + 1
        if starting_wave_num == 3:
            return 1
        elif starting_wave_num == 4:
            return 2
        elif starting_wave_num == 5:
            # Wave 5: level 3 if Hard difficulty, otherwise level 2
            if hasattr(self.settings, 'difficulty_mode') and self.settings.difficulty_mode.lower() == "hard":
                return 3
            else:
                return 2
        return 0

    def _create_shields(self) -> None:
        """Build orbital shield sprites from settings."""
        self.shields.empty()  # clear any existing shields
        self.shield_slots = [] #create shield slots list for memory of where they are.  
        count = self.settings.shield_count  # number of shields to place
        w = self.settings.screen_width // (2 * count + 1)  # shield width based on screen slots
        gap = w  # horizontal gap equals shield width for even spacing
        h = int(self.settings.screen_height * self.settings.shield_height_ratio)  # shield height in pixels
        y = int(self.settings.screen_height * self.settings.shield_y_ratio)  # vertical position for shields
        start_x = gap  # leave a margin on the left
        step = w + gap  # move by one shield plus one gap each time
        for idx in range(count):
            rect = pygame.Rect(start_x + idx * step, y, w, h)  # place shield rectangle
            self.shield_slots.append(rect.copy()) #store shield information in shield slots list.
            self.shields.add(Shield(self.settings, rect))  # create and store shield sprite

    def _init_shields_if_needed(self) -> None:
        """Spawn shields once if the feature is enabled."""
        if not self.settings.orbital_shields_enabled:
            return  # shields globally disabled
        if not self._shields_initialized:
            self._create_shields()  # seed shields at game start
            self._shields_initialized = True  # prevent duplicate initialization

    def _create_players_from_count(self, number_players: int, ShipClass) -> None:
        """Create player ships and populate self.players group."""
        self.players.empty()

        # In Kiddie mode, players always start at level 10
        if hasattr(self.settings, 'difficulty_mode') and self.settings.difficulty_mode.lower() == "kiddie":
            player_starting_level = 10
            # For level 10, get the minimum XP required (range start)
            starting_score = getattr(self.settings, 'lvl10_xp_requirement').start #the .start attribute of a range is a built in way to choose its lowest possible value from its range.
        #otherwise their starting level is defined by the _starting_player_level_for_wave function receiving the current wave number
        else:
            player_starting_level = self._starting_player_level_for_wave(self.current_wave_num)
            # Get the minimum XP required for this level (range start)
            xp_range = getattr(self.settings, f'lvl{player_starting_level}_xp_requirement')
            if hasattr(xp_range, 'start'):  # It's a range object
                starting_score = xp_range.start
            else:  # It's a single integer (level 11)
                starting_score = min(xp_range) #the min function is here used as an alternative built in way to choose the lowest possible value from a list or range.
        for pid in range(1, number_players + 1):
            ship_attr = f"p{pid}ship"
            ship = ShipClass(
                self.settings,
                self.screen,
                player_id=pid,
                player_health=self.settings.player_starting_health,
                player_lives=self.settings.player_starting_lives,
                player_level=player_starting_level,
                player_score=starting_score,
                sound_callback=lambda: self.audio.play("player_level_up", priority=self.audio.SOUND_PRIORITY["player"]),
            )
            setattr(self, ship_attr, ship)
            self.players.add(ship)
            # Initialize player statistics tracking
            self.player_stats[pid] = {
                'damage_taken': 0,
                'lives_lost': 0,
                'bullets_fired': 0,
                'bullets_hit': 0,
                'shield_recharge_shots': 0,
                'alien_collision_kills': 0,
                'time_in_top_30_percent': 0,
                'enemies_destroyed': 0
            }
            # Track active players for credits
            if pid not in self.active_player_ids:
                self.active_player_ids.append(pid)

    def apply_start_config(self, start_config: dict, ShipClass) -> None:
        """
        Helper function for Main_Game_Loop to apply the Start-menu selections into the game.
        Expected keys (use whatever your menu emits):
          - "starting_wave": 1 through 5
          - "number_players": 1 through 4
        
        Note: start_config can be None if user quits the menu.
        Note: Difficulty and powerup settings (from MenuOptions) are applied directly
        to the shared settings object and persist across game sessions, so they don't
        need to be passed through start_config or applied here.
        """
        # Handle None config (user quit menu)
        if start_config is None:
            return
        # 1) Reset anything that could have been modified by a previous menu run
        self._reset_to_menu_baselines()

        # 2) Check for bonus wave mode #bonus wave - check if secret wave was selected
        if start_config and start_config.get("secret_wave"):
            self.is_bonus_wave = True  # bonus wave - set flag
            self.current_wave_num = 0  # bonus wave - set dummy wave number to avoid None errors
            num_players = int(start_config.get("num_players", 1))
            num_players = max(1, min(4, num_players))
            
            # Set multiplayer sprite resizer for bonus wave (same formula as regular game)
            self.settings.multiplayer_resizer = 1 - (0.075 * (num_players - 1))
            print("resizer is", self.settings.multiplayer_resizer)
            
            self._create_players_from_count(num_players, ShipClass)
            self._start_bonus_wave()
            return

        # 2) Pull values from config with safe defaults
        starting_wave = int(start_config.get("starting_wave", 1))
        num_players = int(start_config.get("num_players", start_config.get("number_players", 1)))

        # Clamp to legal ranges (prevents crashes if menu ever returns odd values)
        starting_wave = max(1, min(5, starting_wave))
        num_players = max(1, min(4, num_players))

        # 3) Convert starting wave (1..5) to your internal wave index (0..4)
        self.current_wave_num = starting_wave - 1

        # 4) Multiplayer sprite resizer (same formula as your old CLI setup)
        self.settings.multiplayer_resizer = 1 - (0.075 * (num_players - 1))
        print("resizer is", self.settings.multiplayer_resizer)
        
        # --- IMPORTANT: sprite sizes must be set BEFORE any Alien() is instantiated ---
        resize = self.settings.multiplayer_resizer

        self.settings.alien1_spritesize = (
            max(1, round(self.settings.alien1_spriteX * resize)),
            max(1, round(self.settings.alien1_spriteY * resize)),
        )
        self.settings.alien2_spritesize = (
            max(1, round(self.settings.alien2_spriteX * resize)),
            max(1, round(self.settings.alien2_spriteY * resize)),
        )
        self.settings.alien3_spritesize = (
            max(1, round(self.settings.alien3_spriteX * resize)),
            max(1, round(self.settings.alien3_spriteY * resize)),
        )
        self.settings.alien4_spritesize = (
            max(1, round(self.settings.alien4_spriteX * resize)),
            max(1, round(self.settings.alien4_spriteY * resize)),
        )
        self.settings.destroyer_spritesize = (
            max(1, round(self.settings.destroyer_spriteX * resize)),
            max(1, round(self.settings.destroyer_spriteY * resize)),
        )
        self.settings.cruiser_spritesize = (
            max(1, round(self.settings.cruiser_spriteX * resize)),
            max(1, round(self.settings.cruiser_spriteY * resize)),
        )
        self.settings.laztanker_spritesize = (
            max(1, round(self.settings.laztanker_spriteX * resize)),
            max(1, round(self.settings.laztanker_spriteY * resize)),
        )

        # 5) Create ships
        self._create_players_from_count(num_players, ShipClass)

        # 6) Spawn timing scaling (mirrors your old gamesetup)
        pcount = num_players
        scale = (pcount * 0.15)

        self.level2_minspawntime = round(self.settings.alien2_min_spawn_interval - (self.settings.alien2_min_spawn_interval * scale))
        self.level2_maxspawntime = round(self.settings.alien2_max_spawn_interval - (self.settings.alien2_max_spawn_interval * scale))

        self.level3_minspawntime = round(self.settings.alien3_min_spawn_interval - (self.settings.alien3_min_spawn_interval * scale))
        self.level3_maxspawntime = round(self.settings.alien3_max_spawn_interval - (self.settings.alien3_max_spawn_interval * scale))

        self.level4_minspawntime = round(self.settings.alien4_min_spawn_interval - (self.settings.alien4_min_spawn_interval * scale))
        self.level4_maxspawntime = round(self.settings.alien4_max_spawn_interval - (self.settings.alien4_max_spawn_interval * scale))

        self.destroyer_minspawntime = round(self.settings.destroyer_min_spawn_interval - (self.settings.destroyer_min_spawn_interval * scale))
        self.destroyer_maxspawntime = round(self.settings.destroyer_max_spawn_interval - (self.settings.destroyer_max_spawn_interval * scale))

        self.cruiser_minspawntime = round(self.settings.cruiser_min_spawn_interval - (self.settings.cruiser_min_spawn_interval * scale))
        self.cruiser_maxspawntime = round(self.settings.cruiser_max_spawn_interval - (self.settings.cruiser_max_spawn_interval * scale))

        self.laztanker_minspawntime = round(self.settings.laztanker_min_spawn_interval - (self.settings.laztanker_min_spawn_interval * scale))
        self.laztanker_maxspawntime = round(self.settings.laztanker_max_spawn_interval - (self.settings.laztanker_max_spawn_interval * scale))
        
        # Store baseline spawn times for wave scaling
        self._base_level2_minspawntime = self.level2_minspawntime
        self._base_level2_maxspawntime = self.level2_maxspawntime
        self._base_level3_minspawntime = self.level3_minspawntime
        self._base_level3_maxspawntime = self.level3_maxspawntime
        self._base_level4_minspawntime = self.level4_minspawntime
        self._base_level4_maxspawntime = self.level4_maxspawntime
        self._base_destroyer_minspawntime = self.destroyer_minspawntime
        self._base_destroyer_maxspawntime = self.destroyer_maxspawntime
        self._base_cruiser_minspawntime = self.cruiser_minspawntime
        self._base_cruiser_maxspawntime = self.cruiser_maxspawntime
        self._base_laztanker_minspawntime = self.laztanker_minspawntime
        self._base_laztanker_maxspawntime = self.laztanker_maxspawntime

        # 7) Fleet/wave scaling for multiplayer (also mirrors old logic, but non-compounding)
        if pcount > 1:
            self.settings.fleet_advance_speed += (pcount * 0.01)

            for wave in self.settings.wave_master_index:
                wave["rows_level1"] += pcount

        # Reinforcement gate should always be: (fleet sprite height + 10)
        self.level1_reinforcements_threshhold = self.settings.alien1_spritesize[1] + 10



        desired_visible_rows = 5 if pcount >= 3 else 4
        self.max_visible_level1_rows = desired_visible_rows
        self.settings.level1_alien_starting_rows = desired_visible_rows
        self.settings.level1_warp_rows = desired_visible_rows
        self.level1_reinforcements_threshhold = max(30, self.level1_reinforcements_threshhold)

        # 8) Ensure each ship has correct screen reference (useful if you changed mode/resolution)
        for ship in self.players:
            ship.screen = self.screen


    def _maybe_spawn_powerup_from_alien(self, alien):
        if not self.settings.powerups_enabled:
            return

    # Lazertanker/gunship: guaranteed spawn
        kind = getattr(alien, "level", None)
        guaranteed = kind in (7,8)

        if not guaranteed:
            if random.random() > self.settings.powerup_drop_chance:
                    return

        ptype = choose_powerup_type(self.settings, is_bonus_wave=self.is_bonus_wave)
        if not ptype:
            return

        pu = PowerUpPickup(self.settings, self.screen, ptype, alien.rect.centerx, alien.rect.centery)
        self.powerups.add(pu)
    


                   


#------and now, drawing everything to the screen:
    def _draw_screen(self):
        """helper function for Main Game Loop to (re)draw the screen and ships"""
        
        #First a set of ifs to handle changing background screens, and defeat/victory screens.
        bg_ref = None

        if self.is_bonus_wave:  # bonus wave - use bonus wave background
            if self.game_state == "defeat":
                bg_ref = self.bg_defeat
            elif self.game_state == "victory":
                bg_ref = self.bg_victory
            else:
                # Check if nyancat is alive - if so, use nyancat background
                nyancat_alive = any(enemy.enemy_type == "nyancat" for enemy in self.bonus_wave_enemies)
                if nyancat_alive:
                    bg_ref = self.bg_nyancat
                else:
                    bg_ref = self.bg_bonus_wave
        elif self.game_state == "defeat":
            bg_ref = self.bg_defeat
        elif self.game_state == "victory":
            bg_ref = self.bg_victory
        else:
            # In Kiddie mode, always use levels 1-2 background
            if hasattr(self.settings, 'difficulty_mode') and self.settings.difficulty_mode.lower() == "kiddie":
                bg_ref = self.bg_starter
            elif self.current_wave_num is None:
                # During startup or menu transitions, use starter background
                bg_ref = self.bg_starter
            elif self.current_wave_num <= 2:
                bg_ref = self.bg_starter
            elif self.current_wave_num in range (3,5):
                bg_ref = self.bg_3to4
            elif self.current_wave_num in range (5,7):
                bg_ref = self.bg_5to6
            elif self.current_wave_num in range (7,9):
                bg_ref = self.bg_7to8
            elif self.current_wave_num in range (9,11):
                bg_ref = self.bg_9to10
        
        self._blit_background_with_fade(bg_ref)  # redraw the background (with optional crossfade)
        
        
 
        #draw shields 'under" all player and alien movement.'
        for shield in self.shields:
            self.screen.blit(shield.image, shield.rect)
        #redraw the player ships
        
        for ship in self.players:
            ship.draw()

        # Draw lifepods
        for lifepod in self.lifepods:
            lifepod.draw()

        #redraw aliens - first create reference lists, so that we can blit them in the right layers.
        laztankers = [alien for alien in self.aliens if alien.level == 7] #create list of lazertankers to be drawn, 
        # gunships = [alien for alien in self.aliens if alien.level == 8] #spawn gunships next, so they spawn above Laser tankers, but below other sprites. 
        fleet = [alien for alien in self.aliens if alien.level == 1]
        cruisers = [alien for alien in self.aliens if alien.level == 6]
        rest_of_aliens = [alien for alien in self.aliens if alien.level not in (1,4,6,7,8)]
        comet_kazes = [alien for alien in self.aliens if alien.level == 4] 
        


        for alien in laztankers: #spawn laser tankers first, so they are always under all other sprites.
            alien.draw()
        # Draw lasertanker death animations
        for anim in self.lazertanker_death_animations:
            self.screen.blit(anim.image, anim.rect)
        # Draw cruiser death animations
        for anim in self.cruiser_death_animations:
            self.screen.blit(anim.image, anim.rect)
        # Draw destroyer death animations
        for anim in self.destroyer_death_animations:
            self.screen.blit(anim.image, anim.rect)
        # for alien in gunships: #spawn gunships next, so they spawn above Laser tankers, but below other sprites. 
        #     alien.draw()
        # Draw bonus wave enemies if in bonus wave mode #bonus wave - draw bonus wave enemies
        if self.is_bonus_wave:
            self._draw_bonus_wave()
        else:
            for alien in fleet: #spawn fleets at bottom, but above the two biggies.
                alien.draw()
            for alien in cruisers: #spawn cruisers over fleets, gunships, laser tankers, but under everything else.
                alien.draw()
            for alien in rest_of_aliens: #spawn all but level 4 aliens next, so they are in a jumble depending on when they spawned, with lvl1's generally at bottom.
                alien.draw()
            for minion in self.minions: # Draw minions with regular aliens
                minion.draw()
        for alien in comet_kazes: # level 4 aliens should always be on top of stack, so they are always visible. 
            alien.draw()



        #redraw player and then alien bullets
        for bullet in self.player_bullets:
            bullet.draw()
        for bullet in self.alien_bullets:
            bullet.draw()
        
        # powerup pickups (draw explicitly to ensure visibility)
        for powerup in self.powerups.sprites():
            self.screen.blit(powerup.image, powerup.rect)

        # nanites (since they have a beam overlay, do them explicitly)
        for nanite in self.nanites.sprites():
          self.screen.blit(nanite.image, nanite.rect)
          nanite.draw_beam()  # pass screen if your method needs it

        # squadrons (draw after players so they appear on top)
        for squadron in self.squadrons.sprites():
            self.screen.blit(squadron.image, squadron.rect)

        # shockwaves
        for shockwave in self.shockwaves.sprites():
            self.screen.blit(shockwave.image, shockwave.rect)
        
        # Draw bonus wave powerups
        if self.is_bonus_wave:
            for dad_ship in self.dad_ships.sprites():
                self.screen.blit(dad_ship.image, dad_ship.rect)
            for dad_shockwave in self.dad_shockwaves.sprites():
                self.screen.blit(dad_shockwave.image, dad_shockwave.rect)
            for mom_ship in self.mom_ships.sprites():
                self.screen.blit(mom_ship.image, mom_ship.rect)
            for mom_bullet in self.mom_bullets.sprites():
                self.screen.blit(mom_bullet.image, mom_bullet.rect)
        
        # Draw bonus wave firework effects #bonus wave - draw firework effects on top
        if self.is_bonus_wave:
            for firework in self.bonus_wave_fireworks:
                firework.draw()
        # Draw normal-mode victory fireworks (cosmetic sparks) on top
        if (not self.is_bonus_wave) and self.game_state == "victory" and getattr(self, "victory_fireworks_active", False):
            for spark in self.victory_fireworks.sprites():
                spark.draw()

        #draw the Heads Up Display last, so it is on top of anything else

        self._draw_hud() #note that _draw_hud_strip() is called as part of this function

        # Draw countdown timer (on top of everything except pause)
        if self.game_state == "countdown":
            self._draw_countdown()

        # Draw pause screen (on top of everything)
        if self.game_state == "paused":
            self._draw_pause_screen()

        # Draw defeat/victory screens
        if self.game_state in ("defeat", "victory"):
            self._draw_defeat_victory_screens()

        if self.game_state == "between_waves":
            if self.between_wave_phase == "complete_banner" and self.wave_banner_active:
                banner_surf = self.wave_complete_font.render(self.wave_banner_text, True, self.settings.hud_text_color)
                banner_rect = banner_surf.get_rect(midleft=(int(self.wave_banner_x), self.wave_banner_y))
                self.screen.blit(banner_surf, banner_rect)

            elif self.between_wave_phase == "warp_banner":
                upcoming_wave_display = (self.current_wave_num + 1) if self.current_wave_num is not None else 1
                warp_text = f"Wave {upcoming_wave_display} Warping In!"
                warp_surf = self.warping_font.render(warp_text, True, self.settings.hud_text_color)
                warp_rect = warp_surf.get_rect(center=(self.settings.screen_width // 2, int(self.settings.screen_height * 0.12)))
                blink_on = ((pygame.time.get_ticks() // self.warp_blink_period_ms) % 2) == 0
                if blink_on:
                    pygame.draw.rect(self.screen, (255, 0, 0), warp_rect.inflate(20, 10))
                self.screen.blit(warp_surf, warp_rect)

        pygame.display.flip() #flip the display!!!
    
    def _update_hud_font_size(self):
        """Update HUD font size based on current resolution - scales proportionally to screen size"""
        # Base font size for Normal resolution (1200x580)
        base_size = 23
        # Reference resolution (Normal)
        reference_width = 1200
        # Scale factor is proportional to screen width relative to reference
        scale = self.settings.screen_width / reference_width
        font_size = int(base_size * scale)
        self.hud_font = pygame.font.SysFont(None, font_size)
        # Wave/defense strength font is 4 points larger
        self.wave_hud_font = pygame.font.SysFont(None, font_size + 4)
        # Clear HUD cache when font changes (surfaces need to be re-rendered)
        self._hud_cache = {}
    
    def _get_key_name_cached(self, key_constant):
        """Cached version of get_key_name - avoids repeated pygame.key.name() calls"""
        if key_constant not in self._key_name_cache:
            name = pygame.key.name(key_constant).upper()
            # Clean up key names for display
            if name == "BACKSPACE":
                result = "BS"
            elif name == "BACKSLASH":
                result = "\\"
            elif name == "RETURN":
                result = "ENTER"
            elif name == "BACKQUOTE":
                result = "`"
            elif name == "CAPSLOCK":
                result = "CAPS"
            elif name.startswith("KP"):
                result = name.replace("KP", "KP")
            else:
                result = name
            self._key_name_cache[key_constant] = result
        return self._key_name_cache[key_constant]
    
    def _draw_text(self, text: str, x: int, y: int, color, font=None):
        """Small HUD helper: render and blit a single string."""
        if font is None:
            font = self.hud_font
        surf = font.render(text, True, color)
        rect = surf.get_rect(topleft=(x, y))
        self.screen.blit(surf, rect)
        return rect


    def _calculate_powerup_inventory_width(self, player_id: int, ship):
        """Calculate the actual width of the powerup inventory text without drawing it"""
        keys_dict = getattr(self.settings, f"player{player_id}_keys")
        
        # Calculate prefix width
        prefix = f"P{player_id}: "
        prefix_width = self.hud_font.size(prefix)[0]
        
        total_width = prefix_width
        powerup_order = ["nanites", "squadron", "shockwave"]
        
        for i, ptype in enumerate(powerup_order):
            # Icon width
            total_width += 14  # icon width + small gap
            
            # Key name width (use cached version)
            key_const = keys_dict.get(ptype)
            if key_const:
                key_name = self._get_key_name_cached(key_const)
                key_text = f"({key_name}):"
                total_width += self.hud_font.size(key_text)[0]
            
            # Number width
            num_text = str(ship.powerups.get(ptype, 0))
            total_width += self.hud_font.size(num_text)[0]
            
            # Separator width (except for last item)
            if i < len(powerup_order) - 1:
                total_width += self.hud_font.size(" | ")[0]
        
        return total_width

    def _draw_powerup_inventory(self, player_id: int, ship, x: int, y: int, base_color):
        """
        Draw powerup inventory in format: "Player #: [icon](key):[number] | [icon](key):[number] | [icon](key):[number]"
        Uses ship.powerups keys: 'nanites', 'squadron', 'shockwave' (in that order)
        Uses ship.powerup_flash_until_ms[ptype] timers for flashing numbers.
        """
        now = pygame.time.get_ticks()
        
        # Get player keys
        keys_dict = getattr(self.settings, f"player{player_id}_keys")
        
        # Blink behavior for flashing numbers
        def should_flash(ptype: str):
            until = getattr(ship, "powerup_flash_until_ms", {}).get(ptype, 0)
            return now < until and (now // 120) % 2 == 0
        
        # Load mini powerup icons if not already loaded
        if not hasattr(self, '_powerup_icons'):
            self._powerup_icons = {}
            icon_size = (12, 12)  # Small icon size
            bonus_icon_size = (round(12 * 2.0), round(12 * 2.0))  # 100% larger for mom/dad = 24x24
            try:
                nanite_img = pygame.image.load(self.settings.powerup_nanite_path).convert_alpha()
                self._powerup_icons["nanites"] = pygame.transform.smoothscale(nanite_img, icon_size)
                
                squadron_img = pygame.image.load(self.settings.powerup_squadron_path).convert_alpha()
                self._powerup_icons["squadron"] = pygame.transform.smoothscale(squadron_img, icon_size)
                
                shockwave_img = pygame.image.load(self.settings.powerup_shockwave_path).convert_alpha()
                self._powerup_icons["shockwave"] = pygame.transform.smoothscale(shockwave_img, icon_size)
                
                # Bonus wave icons (20% larger)
                dad_img = pygame.image.load(self.settings.powerup_dad_path).convert_alpha()
                self._powerup_icons["dad"] = pygame.transform.smoothscale(dad_img, bonus_icon_size)
                
                mom_img = pygame.image.load(self.settings.powerup_mom_path).convert_alpha()
                self._powerup_icons["mom"] = pygame.transform.smoothscale(mom_img, bonus_icon_size)
            except Exception:
                # Fallback if images can't load
                self._powerup_icons = {"nanites": None, "squadron": None, "shockwave": None, "dad": None, "mom": None}

        cur_x = x
        
        # Start with "Player #: "
        prefix = f"P{player_id}: "
        prefix_surf = self.hud_font.render(prefix, True, base_color)
        self.screen.blit(prefix_surf, (cur_x, y))
        cur_x += prefix_surf.get_width()
        
        # Powerup order: nanites, squadron, shockwave (or dad, mom for bonus wave)
        if self.is_bonus_wave:
            powerup_order = ["dad", "mom"]
        else:
            powerup_order = ["nanites", "squadron", "shockwave"]
        
        for i, ptype in enumerate(powerup_order):
            # Draw icon
            icon = self._powerup_icons.get(ptype)
            if icon:
                # Position icon so its bottom aligns with the text baseline
                font_height = self.hud_font.get_height()
                if ptype in ("dad", "mom"):
                    # 24x24 icons: position so bottom aligns with text bottom
                    icon_y = y + font_height - 24
                    icon_x = cur_x
                    cur_x += 26  # icon width (24) + small gap (2)
                else:
                    # 12x12 icons: position so bottom aligns with text bottom
                    icon_y = y + font_height - 12
                    icon_x = cur_x
                    cur_x += 14  # icon width (12) + small gap (2)

                self.screen.blit(icon, (icon_x, icon_y))
            
            # Draw key name in parentheses (use cached key name and cache rendered surface)
            # For bonus wave, dad uses squadron key, mom uses nanite key
            if self.is_bonus_wave:
                if ptype == "dad":
                    key_const = keys_dict.get("squadron")
                elif ptype == "mom":
                    key_const = keys_dict.get("nanites")
                else:
                    key_const = keys_dict.get(ptype)
            else:
                key_const = keys_dict.get(ptype)
            if key_const:
                key_name = self._get_key_name_cached(key_const)
                key_text = f"({key_name}):"
                # Cache key text surface (static, doesn't change)
                cache_key = f"key_{player_id}_{ptype}"
                if player_id not in self._hud_cache:
                    self._hud_cache[player_id] = {'powerups': {}}
                elif 'powerups' not in self._hud_cache[player_id]:
                    self._hud_cache[player_id]['powerups'] = {}
                if cache_key not in self._hud_cache[player_id]['powerups']:
                    self._hud_cache[player_id]['powerups'][cache_key] = self.hud_font.render(key_text, True, base_color)
                key_surf = self._hud_cache[player_id]['powerups'][cache_key]
                self.screen.blit(key_surf, (cur_x, y))
                cur_x += key_surf.get_width()
            
            # Draw number with flash support (cache rendered surface, re-render when value changes)
            num_value = ship.powerups.get(ptype, 0)
            num_text = str(num_value)
            flash = should_flash(ptype)
            num_color = (255, 255, 255) if flash else base_color
            # Cache key for this powerup number
            num_cache_key = f"num_{player_id}_{ptype}"
            # Check if we need to re-render (value changed or flashing state changed)
            if num_cache_key not in self._hud_cache[player_id]['powerups']:
                # First time rendering
                self._hud_cache[player_id]['powerups'][num_cache_key] = (self.hud_font.render(num_text, True, num_color), num_value, flash)
            else:
                cached_surf, cached_value, cached_flash = self._hud_cache[player_id]['powerups'][num_cache_key]
                # Re-render if value changed or flash state changed
                if cached_value != num_value or cached_flash != flash:
                    self._hud_cache[player_id]['powerups'][num_cache_key] = (self.hud_font.render(num_text, True, num_color), num_value, flash)
            num_surf = self._hud_cache[player_id]['powerups'][num_cache_key][0]
            num_rect = num_surf.get_rect(topleft=(cur_x, y))
            
            # Draw flash background if flashing
            if flash:
                pygame.draw.rect(self.screen, (255, 255, 255), num_rect.inflate(4, 2))
            
            self.screen.blit(num_surf, num_rect)
            cur_x += num_surf.get_width()
            
            # Draw separator (except for last item) - cache separator surface (static)
            if i < len(powerup_order) - 1:
                if player_id not in self._hud_cache:
                    self._hud_cache[player_id] = {'powerups': {}}
                elif 'powerups' not in self._hud_cache[player_id]:
                    self._hud_cache[player_id]['powerups'] = {}
                if 'separator' not in self._hud_cache[player_id]['powerups']:
                    self._hud_cache[player_id]['powerups']['separator'] = self.hud_font.render(" | ", True, base_color)
                sep_surf = self._hud_cache[player_id]['powerups']['separator']
                self.screen.blit(sep_surf, (cur_x, y))
                cur_x += sep_surf.get_width()


    def _draw_hud(self):  
            """Draws the Heads Up Display for players - inventory, player health, lives remaining, and wave+scoring info"""
            self._draw_hud_strip()
            # bonus wave - use bonus_wave_defense_strength for bonus wave, current_defense_strength for normal waves
            if self.is_bonus_wave:
                defense_strength = self.bonus_wave_defense_strength
                current_wave_text = f"Bonus Wave || Defense Strength: {defense_strength}"
            else:
                defense_strength = getattr(self, 'current_defense_strength', 0)
                current_wave_text = f"Wave{self.current_wave_num + 1} || Defense Strength: {defense_strength}" if self.current_wave_num is not None else "Wave ?" # tells the program" set the text to display the current wave; unless current wave is none; in which case, and in all other cases; show debut text "Wave ?""
            wave_surf = self.wave_hud_font.render(current_wave_text, True, self.settings.hud_text_color)
            wave_rect = wave_surf.get_rect(center=(self.settings.screen_width // 2, 15))
            self.screen.blit(wave_surf, wave_rect)
            now = pygame.time.get_ticks()
                # Player info at bottom
            # Spread across the bottom of the screen
            if self.players:
                hud_x_placements = {1:int(self.settings.screen_width * 0.60), 
                                2:int(self.settings.screen_width * 0.35), 
                                3:int(self.settings.screen_width *0.85), 
                                4:int(self.settings.screen_width * 0.15)}
                
                for ship in self.players:
                    hud_color = getattr(self.settings, f"player{ship.player_id}_hud_color", 
                                        self.settings.hud_text_color #as a fallback option if the first one should fail
                                        )
                    hud_x = hud_x_placements.get(ship.player_id, self.settings.screen_width // 2) #for later tests on more than 4 ships, this has a built in default-->
                                                                                                #--> to place the ship at screen center if the id has no corresponding placement.

                    # Initialize cache for this player if needed
                    if ship.player_id not in self._hud_cache:
                        self._hud_cache[ship.player_id] = {}
                    
                    # Cache prefix and mid (static text)
                    if 'prefix' not in self._hud_cache[ship.player_id]:
                        prefix = f"P{ship.player_id}: HP "
                        self._hud_cache[ship.player_id]['prefix'] = self.hud_font.render(prefix, True, hud_color)
                    if 'mid' not in self._hud_cache[ship.player_id]:
                        mid = " | Lives "
                        self._hud_cache[ship.player_id]['mid'] = self.hud_font.render(mid, True, hud_color)
                    
                    prefix_surf = self._hud_cache[ship.player_id]['prefix']
                    mid_surf = self._hud_cache[ship.player_id]['mid']
                    
                    # Cache HP, Lives, and Level (re-render when values change)
                    hp_value = ship.player_health
                    lives_value = ship.player_lives
                    level_value = ship.player_level
                    
                    # HP surface caching
                    if 'hp' not in self._hud_cache[ship.player_id] or self._hud_cache[ship.player_id]['hp'][1] != hp_value:
                        hp_text = str(hp_value)
                        self._hud_cache[ship.player_id]['hp'] = (self.hud_font.render(hp_text, True, hud_color), hp_value)
                    hp_surf = self._hud_cache[ship.player_id]['hp'][0]
                    
                    # Lives surface caching
                    if 'lives' not in self._hud_cache[ship.player_id] or self._hud_cache[ship.player_id]['lives'][1] != lives_value:
                        lives_text = str(lives_value)
                        self._hud_cache[ship.player_id]['lives'] = (self.hud_font.render(lives_text, True, hud_color), lives_value)
                    lives_surf = self._hud_cache[ship.player_id]['lives'][0]
                    
                    # Level surface caching
                    if 'level' not in self._hud_cache[ship.player_id] or self._hud_cache[ship.player_id]['level'][1] != level_value:
                        suffix = f" | Lvl {level_value}"
                        self._hud_cache[ship.player_id]['level'] = (self.hud_font.render(suffix, True, hud_color), level_value)
                    suffix_surf = self._hud_cache[ship.player_id]['level'][0]

                    line_height = prefix_surf.get_height()
                    total_width = (
                        prefix_surf.get_width()
                        + hp_surf.get_width()
                        + mid_surf.get_width()
                        + lives_surf.get_width()
                        + suffix_surf.get_width()
                    )
                    start_x = int(hud_x - (total_width // 2))
                    # Position HUD flush at bottom of playable screen
                    y = int(self.settings.play_height - line_height)

                    prefix_rect = prefix_surf.get_rect(topleft=(start_x, y))
                    hp_rect = hp_surf.get_rect(topleft=(prefix_rect.right, y))
                    mid_rect = mid_surf.get_rect(topleft=(hp_rect.right, y))
                    lives_rect = lives_surf.get_rect(topleft=(mid_rect.right, y))
                    suffix_rect = suffix_surf.get_rect(topleft=(lives_rect.right, y))

                    blink_on = (now // 80) % 2 == 0
                    if ship.hp_flash_until_ms > now and blink_on:
                        pygame.draw.rect(self.screen, (255, 255, 255), hp_rect.inflate(6, 4))
                    if ship.lives_flash_until_ms > now and blink_on:
                        if ship.player_id == 2: #player 2's background blink for lost lives can't be red, or it woudl obscure the number
                          pygame.draw.rect(self.screen, (255, 200, 200), lives_rect.inflate(6, 4))
                        else:
                          pygame.draw.rect(self.screen, (255, 0, 0), lives_rect.inflate(6, 4))

                    self.screen.blit(prefix_surf, prefix_rect)
                    self.screen.blit(hp_surf, hp_rect)
                    self.screen.blit(mid_surf, mid_rect)
                    self.screen.blit(lives_surf, lives_rect)
                    self.screen.blit(suffix_surf, suffix_rect)

                    # RENDER THE POWERUP INVENTORY STRIP BELOW THE HUD:
                    y2 = int(self.settings.play_height + 22)  # 2nd line sits under first HUD line
                    # Powerup inventory x positions: P4 and P3 flush against edges, P1 and P2 evenly distributed
                    powerup_x_placements = {
                        4: 5,  # Flush left with small padding
                        2: int(self.settings.screen_width * 0.20),  # Evenly spaced
                        1: int(self.settings.screen_width * 0.50),  # Evenly spaced
                        3: int(self.settings.screen_width * 0.99)  # Near right edge (will be adjusted if text too wide)
                    }
                    powerup_x = powerup_x_placements.get(ship.player_id, start_x)
                    # For player 3, position from right edge to keep it flush against the window edge
                    if ship.player_id == 3:
                        # Calculate actual width of the powerup inventory text
                        actual_width = self._calculate_powerup_inventory_width(ship.player_id, ship)
                        # Position so right edge is flush with screen edge (with small padding)
                        powerup_x = self.settings.screen_width - actual_width - 5
                    self._draw_powerup_inventory(ship.player_id, ship, powerup_x, y2, hud_color)

    def _draw_hud_strip(self):
        # draw theBlack strip beneath playfield
        strip = pygame.Rect(0, self.settings.play_height, self.settings.screen_width, self.settings.hud_strip_height)
        pygame.draw.rect(self.screen, (0, 0, 0), strip)


    # ---------- Bonus Wave Methods ---------- #bonus wave - custom secret wave implementation
    def _start_bonus_wave(self):
        """Initialize bonus wave mode"""
        # Don't set game_state here - countdown will handle transition to playing
        self.bonus_wave_start_time = pygame.time.get_ticks()
        self.bonus_wave_defense_strength = self.settings.bonus_wave_defense_strength
        self.bonus_wave_enemies.empty()
        self.bonus_wave_fireworks.empty()
        
        # Spawn timing variables (offset by countdown duration so they start after countdown)
        countdown_offset = self.countdown_duration_ms
        self.bonus_loaf_next_spawn = pygame.time.get_ticks() + self.settings.loafkitty_spawn_delay + countdown_offset
        self.bonus_centurion_next_spawn = pygame.time.get_ticks() + self.settings.centurionkitty_spawn_delay + countdown_offset
        self.bonus_ninja_next_spawn = pygame.time.get_ticks() + self.settings.ninjakitty_spawn_delay + countdown_offset
        self.bonus_emperor_next_spawn = pygame.time.get_ticks() + self.settings.emperorkitty_spawn_delay + countdown_offset
        self.bonus_bluewhale_next_spawn = pygame.time.get_ticks() + self.settings.bluewhalekitty_spawn_delay + countdown_offset
        self.bonus_nyancat_next_spawn = pygame.time.get_ticks() + self.settings.nyancat_spawn_delay + countdown_offset
    
    def _update_bonus_wave(self):
        """Update bonus wave enemies, spawning, and collisions"""
        now = pygame.time.get_ticks()
        elapsed_ms = now - self.bonus_wave_start_time
        
        # Track time in top 33% of screen for each player (Power Forward award)
        # Note: stored under historical key name 'time_in_top_30_percent' for credits compatibility.
        if self.game_state == "playing":
            top_33_percent_y = self.settings.play_height * 0.33
            frame_time_ms = self.clock.get_time()  # Get time since last frame in milliseconds
            for player in self.players.sprites():
                if player.player_state == "alive" and player.player_id in self.player_stats:
                    if player.rect.top <= top_33_percent_y:
                        self.player_stats[player.player_id]['time_in_top_30_percent'] += frame_time_ms
        
        # Check for 20-minute victory or defeat
        if elapsed_ms >= self.settings.bonus_wave_duration_ms:
            self.game_state = "victory"
            self._init_bonus_wave_victory_screen()
            return
        
        # Check for defeat conditions:
        # 1) Defense strength depleted (starts at 10, decreases when enemies breach)
        if self.bonus_wave_defense_strength <= 0:
            self.game_state = "defeat"
            self._init_bonus_wave_defeat_screen()
            return
        
        # 2) All players have lost all their lives (truly dead, not respawning)
        # Check if any players are still alive, respawning, or between lives
        # Note: When players die completely, player.kill() removes them from self.players
        # So we need to check both: if group is empty OR all remaining players are dead
        if len(self.players) == 0:
            # All players have been killed and removed
            self.game_state = "defeat"
            self._init_bonus_wave_defeat_screen()
            return
        
        # Check if all remaining players have lost all lives (player_lives < 0)
        all_players_dead = True
        for ship in self.players:
            # Player is still in the game if they have lives remaining OR are respawning
            if ship.player_lives >= 0 or ship.player_state in ("between_lives", "respawning", "alive"):
                all_players_dead = False
                break
        
        # Only trigger defeat if all players have truly lost all lives
        if all_players_dead:
            self.game_state = "defeat"
            self._init_bonus_wave_defeat_screen()
            return
        
        # Calculate scaling (linearly increase over 15 minutes)
        scale_time = min(elapsed_ms, 900000)  # Cap at 15 minutes
        spawn_scale = 1.0 + (scale_time / 900000.0) * (self.settings.bonus_wave_max_spawn_scale - 1.0)
        speed_scale = 1.0 + (scale_time / 900000.0) * (self.settings.bonus_wave_max_speed_scale - 1.0)
        
        # Apply player count scaling to spawn rates (4 players = 50% faster = 1.5x rate)
        num_players = len(self.players)
        if num_players > 1:
            # Scale: 1 player = 1.0, 2 players = 1.1667, 3 players = 1.3333, 4 players = 1.5
            # Linear scaling: 50% increase (1.5x rate) over 3 steps (1->2, 2->3, 3->4)
            # Since intervals are divided by spawn_scale, higher values = faster spawning
            player_spawn_scale = 1.0 + ((num_players - 1) / 3.0) * 0.5
            spawn_scale *= player_spawn_scale
        
        # Update players
        self.players.update()
        self.squadrons.update()
        self.nanites.update()
        self.shockwaves.update()
        self.shields.update()
        
        # Update bonus wave powerups
        # Check for dad ship next run times BEFORE update (to capture before ships are killed)
        for dad_ship in list(self.dad_ships.sprites()):  # Use list() to avoid modification during iteration
            if hasattr(dad_ship, 'next_run_time') and dad_ship.next_run_time:
                if self.next_dad_run_time is None or dad_ship.next_run_time < self.next_dad_run_time:
                    self.next_dad_run_time = dad_ship.next_run_time
        
        self.dad_ships.update()
        
        # Also check AFTER update in case next_run_time was set during update
        for dad_ship in list(self.dad_ships.sprites()):  # Use list() to avoid modification during iteration
            if hasattr(dad_ship, 'next_run_time') and dad_ship.next_run_time:
                if self.next_dad_run_time is None or dad_ship.next_run_time < self.next_dad_run_time:
                    self.next_dad_run_time = dad_ship.next_run_time
        self.dad_shockwaves.update()
        self.mom_ships.update()
        self.mom_bullets.update()
        self.lifepods.update()  # Update lifepod positions
        
        # Handle dad ship shockwave firing
        for dad_ship in self.dad_ships.sprites():
            if dad_ship.shockwave_fired and not hasattr(dad_ship, '_shockwave_created'):
                shockwave = dad_ship._fire_shockwave()
                if shockwave:
                    self.dad_shockwaves.add(shockwave)
                    # Play dad shockwave sound
                    self.audio.play("dad_shockwave")
                dad_ship._shockwave_created = True
        
        # Handle mom ship bullet firing
        for mom_ship in self.mom_ships.sprites():
            if hasattr(mom_ship, 'bullets_to_fire') and mom_ship.bullets_to_fire:
                for bullet in mom_ship.bullets_to_fire:
                    self.mom_bullets.add(bullet)
                mom_ship.bullets_to_fire = []
        
        # Schedule next dad ship run
        if self.next_dad_run_time and now >= self.next_dad_run_time:
            # Check if we need to start run 1 or 2
            if not hasattr(self, '_dad_run_number'):
                self._dad_run_number = 0
            
            # Check if all current ships are complete (runs 0 and 1 mark is_complete instead of killing)
            active_ships = [s for s in self.dad_ships.sprites() if not getattr(s, 'is_complete', False)]
            if len(active_ships) == 0:  # All ships are complete or killed
                self._dad_run_number += 1
                if self._dad_run_number <= 2:
                    dad_ship = DadShip(self.settings, self.screen, run_number=self._dad_run_number)
                    self.dad_ships.add(dad_ship)
            self.next_dad_run_time = None
        
        # Player firing
        for ship in self.players:
            if ship.firing and now >= getattr(ship, "next_fire_time", 0):
                self._fire_player_bullet(ship)
                if ship.player_level == 11:
                    ship.next_fire_time = now + self.settings.lvl11_fire_speed
                else:
                    ship.next_fire_time = now + self.settings.player_fire_speed

            if ship.player_state == "respawning" and ship.respawn_end_time is not None:
                if now >= ship.respawn_end_time:
                    ship.player_state = "alive"
                    self.audio.play("player_respawn")
                    ship.respawn_end_time = None

        
        # Update bullets
        self.player_bullets.update()
        self.alien_bullets.update()
        self.bonus_wave_fireworks.update()

        # Spawn enemies
        self._spawn_bonus_wave_enemies(now, elapsed_ms, spawn_scale)
        
        # Update enemies
        for enemy in self.bonus_wave_enemies:
            enemy.update(elapsed_ms, speed_scale, self.players)
            
            # Assign target player for tracking enemies
            if enemy.enemy_type in ("emperor", "bluewhale") and enemy.target_player is None:
                if len(self.players) > 0:
                    enemy.set_target_player(random.choice(list(self.players)))
            
            # Enemy firing
            # Pass alien_bullets group to ready_to_fire for different peculiar bullet specs, incl bullet caps and special class bullets for bonus wave, minions, etc.
            if enemy.ready_to_fire(now, self.alien_bullets):
                if isinstance(enemy, Laserminion):
                    # Laserminion fires accelerating bomb from bottom center
                    bomb = LaserminionBomb(self.settings, self.screen,
                                         enemy.rect.centerx, enemy.rect.bottom)
                    self.alien_bullets.add(bomb)
                elif enemy.enemy_type == "bluewhale":
                    # Continuous laser beam (like lazertanker) - fires every 120-121ms
                    self._fire_bluewhale_laser(enemy)
                elif enemy.enemy_type == "emperor":
                    # Emperorkitty bullets - bright purple, fires every ~0.5s until cap of 3
                    bullet = Bullet(
                        self.settings, self.screen,
                        enemy.rect.centerx, enemy.rect.bottom,
                        direction=1,
                        owner_type="kitty",
                        owner_level=12,  # Emperorkitty
                        owner_ref=enemy
                    )
                    self.alien_bullets.add(bullet)
                elif enemy.enemy_type == "loaf":
                    # Loafkitty bullet - custom 15x2 size
                    bullet = Bullet(
                        self.settings, self.screen,
                        enemy.rect.centerx, enemy.rect.bottom,
                        direction=1,
                        owner_type="kitty",
                        owner_level=10,  # Loafkitty
                        owner_ref=enemy
                    )
                    self.alien_bullets.add(bullet)
                elif enemy.enemy_type == "nyancat":
                    # Nyancat fires rainbow-flashing square bullet
                    # Fire position: 30% up from bottom, 12% from right edge (88% from left when normal, 12% from left when flipped)
                    if hasattr(enemy, 'direction') and enemy.direction == -1:  # Flipped (moving left)
                        fire_x = enemy.rect.left + int(enemy.rect.width * 0.12)  # 12% from left
                    else:  # Normal (moving right)
                        fire_x = enemy.rect.left + int(enemy.rect.width * 0.88)  # 88% from left (12% from right)
                    fire_y = enemy.rect.bottom - int(enemy.rect.height * 0.30)

                    # Create special rainbow bullet
                    bullet = NyancatBullet(
                        self.settings, self.screen,
                        fire_x, fire_y,
                        direction=1,
                        owner_ref=enemy
                    )
                    self.alien_bullets.add(bullet)
                elif enemy.enemy_type == "centurion":
                    # Regular bullet (centurion)
                    bullet = Bullet(
                        self.settings, self.screen,
                        enemy.rect.centerx, enemy.rect.bottom,
                        direction=1,
                        owner_type="kitty",
                        owner_level=11,  # Centurionkitty
                        owner_ref=None
                    )
                    self.alien_bullets.add(bullet)
        
        # Handle collisions
        self._do_bonus_wave_collisions()

        # Lifepod firing (max 2 bullets at a time) - bonus wave support
        # Count all lifepod bullets once per frame (more efficient than counting per lifepod)
        lifepod_bullet_counts = {}
        for bullet in self.player_bullets:
            if hasattr(bullet, 'owner_ref') and bullet.owner_ref in self.lifepods:
                lifepod = bullet.owner_ref
                lifepod_bullet_counts[lifepod] = lifepod_bullet_counts.get(lifepod, 0) + 1
        
        for lifepod in self.lifepods:
            if lifepod.firing and lifepod.state == "normal":
                # Get bullet count from pre-calculated dictionary
                lifepod_bullet_count = lifepod_bullet_counts.get(lifepod, 0)
                if lifepod_bullet_count < 2:  # Max 2 bullets
                    # Check firing rate timing
                    if now >= getattr(lifepod, "next_fire_time", 0):
                        self._fire_lifepod_bullet(lifepod)
                        lifepod.next_fire_time = now + self.settings.player_fire_speed

        # Update powerups
        self.powerups.update()
        # Determine inventory cap based on difficulty (Hard mode: 6, others: 3)
        is_hard = getattr(self.settings, "difficulty_mode", "easy").lower() == "hard"
        max_inventory = 6 if is_hard else 3
        powerup_grabbed = False  # Track if any powerup was grabbed to play sound only once
        for ship in self.players:
            if ship.player_state == "alive":  # Only alive players can grab powerups
                # Only collide with powerups if inventory not full
                grabs = pygame.sprite.spritecollide(ship, self.powerups, dokill=False)
                for powerup in grabs:
                    ptype = powerup.ptype
                    current_count = ship.powerups.get(ptype, 0)
                    if current_count < max_inventory:  # Inventory cap: max 6 in Hard mode, 3 otherwise
                        ship.powerups[ptype] = current_count + 1
                        ship.trigger_powerup_flash(ptype, duration_ms=900)
                        powerup.kill()  # Remove powerup only if picked up
                        powerup_grabbed = True  # Mark that a powerup was grabbed
        if powerup_grabbed:
            self.audio.play("powerup_grab")  # Play sound once per frame, even if multiple powerups grabbed


    def _spawn_bonus_wave_enemies(self, now, elapsed_ms, spawn_scale):
        """Spawn bonus wave enemies based on timing and scaling"""
        # Loafkitty (level 2 spawn rate)
        if elapsed_ms >= self.settings.loafkitty_spawn_delay:
            if now >= self.bonus_loaf_next_spawn:
                interval = random.randint(
                    int(self.settings.loafkitty_min_spawn_interval / spawn_scale),
                    int(self.settings.loafkitty_max_spawn_interval / spawn_scale)
                )
                self.bonus_loaf_next_spawn = now + interval
                enemy = BonusWaveEnemy(self.settings, self.screen, "loaf")
                enemy.spawn_pos(random.randint(0, self.settings.screen_width - enemy.rect.width), -enemy.rect.height)
                self.bonus_wave_enemies.add(enemy)
        
        # Centurionkitty (level 3 spawn rate)
        if elapsed_ms >= self.settings.centurionkitty_spawn_delay:
            if now >= self.bonus_centurion_next_spawn:
                interval = random.randint(
                    int(self.settings.centurionkitty_min_spawn_interval / spawn_scale),
                    int(self.settings.centurionkitty_max_spawn_interval / spawn_scale)
                )
                self.bonus_centurion_next_spawn = now + interval
                enemy = BonusWaveEnemy(self.settings, self.screen, "centurion")
                enemy.spawn_pos(random.randint(0, self.settings.screen_width - enemy.rect.width), -enemy.rect.height)
                self.bonus_wave_enemies.add(enemy)
        
        # Emperorkitty (cruiser spawn rate, after 2 minutes)
        if elapsed_ms >= self.settings.emperorkitty_spawn_delay:
            if now >= self.bonus_emperor_next_spawn:
                interval = random.randint(
                    int(self.settings.emperorkitty_min_spawn_interval / spawn_scale),
                    int(self.settings.emperorkitty_max_spawn_interval / spawn_scale)
                )
                self.bonus_emperor_next_spawn = now + interval
                enemy = BonusWaveEnemy(self.settings, self.screen, "emperor")
                enemy.spawn_pos(random.randint(0, self.settings.screen_width - enemy.rect.width), -enemy.rect.height)
                if len(self.players) > 0:
                    enemy.set_target_player(random.choice(list(self.players)))
                self.bonus_wave_enemies.add(enemy)
        
        # Ninjakitty (spawns after 7 seconds, more frequently than centurion)
        if elapsed_ms >= self.settings.ninjakitty_spawn_delay:
            if now >= self.bonus_ninja_next_spawn:
                interval = random.randint(
                    int(self.settings.ninjakitty_min_spawn_interval / spawn_scale),
                    int(self.settings.ninjakitty_max_spawn_interval / spawn_scale)
                )
                self.bonus_ninja_next_spawn = now + interval
                enemy = BonusWaveEnemy(self.settings, self.screen, "ninja")
                enemy.spawn_pos(random.randint(0, self.settings.screen_width - enemy.rect.width), -enemy.rect.height)
                self.bonus_wave_enemies.add(enemy)
        
        # Bluewhalekitty (0.5x lazertanker spawn rate, after 4 minutes)
        if elapsed_ms >= self.settings.bluewhalekitty_spawn_delay:
            if now >= self.bonus_bluewhale_next_spawn:
                interval = random.randint(
                    int(self.settings.bluewhalekitty_min_spawn_interval / spawn_scale),
                    int(self.settings.bluewhalekitty_max_spawn_interval / spawn_scale)
                )
                self.bonus_bluewhale_next_spawn = now + interval
                enemy = BonusWaveEnemy(self.settings, self.screen, "bluewhale")
                enemy.spawn_pos(random.randint(0, self.settings.screen_width - enemy.rect.width), -enemy.rect.height)
                if len(self.players) > 0:
                    enemy.set_target_player(random.choice(list(self.players)))
                self.bonus_wave_enemies.add(enemy)
    
        # Nyancat (spawns on a schedule using bonus_nyancat_next_spawn)
        # Music lead-in should apply to the FIRST spawn too (so we cannot gate on elapsed_ms >= spawn_delay).
        if getattr(self, "bonus_nyancat_next_spawn", None) is not None:
            lead_ms = int(getattr(self.settings, "nyancat_music_lead_ms", 7000))
            # Start nyancat music lead_ms before spawn
            if now >= (self.bonus_nyancat_next_spawn - lead_ms) and now < self.bonus_nyancat_next_spawn:
                if not self.audio.nyancat_music_channel or not self.audio.nyancat_music_channel.get_busy():
                    self.audio.nyancat_music_channel = self.audio.play("nyan_cat_music", loop=-1)

            # Spawn nyancat
            if now >= self.bonus_nyancat_next_spawn:
                interval = random.randint(
                    int(self.settings.nyancat_min_spawn_interval / spawn_scale),
                    int(self.settings.nyancat_max_spawn_interval / spawn_scale)
                )
                self.bonus_nyancat_next_spawn = now + interval
                enemy = BonusWaveEnemy(self.settings, self.screen, "nyancat")
                # Start off-screen to the left
                enemy.spawn_pos(-enemy.rect.width, random.randint(50, 200))
                self.bonus_wave_enemies.add(enemy)

    def _fire_bluewhale_laser(self, enemy):
        """Fire continuous blue laser beams from bluewhalekitty - two streams at specific sprite positions"""
        # Check bullet cap (28 bullets max per bluewhale)
        bullet_count = []
        for b in self.alien_bullets:
            if hasattr(b, 'owner_ref') and b.owner_ref == enemy:
                bullet_count.append(b)
        if len(bullet_count) >= 28:  # Cap of 28 (fixed value, not lazertanker_bullet_max)
            return  # Don't fire if at cap
        
        # Calculate firing positions based on sprite dimensions
        # Position 1: 7% from left, 88% down the height
        fire_x1 = enemy.rect.left + (enemy.rect.width * 0.07)
        fire_y1 = enemy.rect.top + (enemy.rect.height * 0.88)
        
        # Position 2: centerx, 86% down the height
        fire_x2 = enemy.rect.centerx
        fire_y2 = enemy.rect.top + (enemy.rect.height * 0.86)
        
        # Fire from position 1
        bullet1 = Bullet(
            self.settings, self.screen,
            fire_x1, fire_y1,
            direction=1,
            owner_type="kitty",
            owner_level=13,  # Bluewhalekitty
            owner_ref=enemy  # Set owner_ref so we can count bullets per enemy
        )
        self.alien_bullets.add(bullet1)
        
        # Fire from position 2 (only if we haven't hit the cap yet)
        if len(bullet_count) + 1 < 28:  # Check if we can add another bullet
            bullet2 = Bullet(
                self.settings, self.screen,
                fire_x2, fire_y2,
                direction=1,
                owner_type="kitty",
                owner_level=13,  # Bluewhalekitty
                owner_ref=enemy  # Set owner_ref so we can count bullets per enemy
            )
            self.alien_bullets.add(bullet2)
    
    def _do_bonus_wave_collisions(self):
        """Handle collisions in bonus wave"""
        # Shields absorb/regen if enabled
        if self.settings.orbital_shields_enabled and self.shields:
            # Player bullets charge shields toward regen
            # Mobile shields: owner's bullets pass through, other players' bullets recharge
            hits = pygame.sprite.groupcollide(self.player_bullets, self.shields, False, False)
            bullets_to_kill = []
            for bullet, shields_hit in hits.items():
                hit_shield = False
                for shield in shields_hit:
                    # Check if this is a mobile shield (mom-created)
                    if hasattr(shield, 'tracked_player') and shield.tracked_player:
                        # Mobile shield: check if bullet owner matches shield owner
                        if (hasattr(bullet, 'owner_ref') and bullet.owner_ref and 
                            hasattr(bullet.owner_ref, 'player_id') and
                            bullet.owner_ref.player_id == shield.tracked_player.player_id):
                            # Owner's bullet passes through
                            continue
                        else:
                            # Other player's bullet recharges the shield
                            if shield.heal(1):  # Recharge by 1 stage, returns True if stage improved
                                self.audio.play("shield_recharge")  # Play sound when shield stage improves
                            # Track shield recharge shot
                            if hasattr(bullet, 'owner_ref') and hasattr(bullet.owner_ref, 'player_id'):
                                player_id = bullet.owner_ref.player_id
                                if player_id in self.player_stats:
                                    self.player_stats[player_id]['shield_recharge_shots'] += 1
                            hit_shield = True
                    else:
                        # Stationary shield - recharge it
                        if shield.register_recharge_hit():  # Returns True if stage improved
                            self.audio.play("shield_recharge")  # Play sound when shield stage improves
                        # Track shield recharge shot
                        if hasattr(bullet, 'owner_ref') and hasattr(bullet.owner_ref, 'player_id'):
                            player_id = bullet.owner_ref.player_id
                            if player_id in self.player_stats:
                                self.player_stats[player_id]['shield_recharge_shots'] += 1
                        hit_shield = True
                # Kill bullet if it hit a shield (and wasn't owner's bullet on mobile shield)
                if hit_shield:
                    bullets_to_kill.append(bullet)
            # Remove bullets that hit shields
            for bullet in bullets_to_kill:
                bullet.kill()
            
            # Kitty bullets damage shields
            hits = pygame.sprite.groupcollide(self.alien_bullets, self.shields, False, False)
            for bullet, shields_hit in hits.items():
                # Check for NyancatBullet (double damage to shields)
                is_nyancat_bullet = isinstance(bullet, NyancatBullet)
                
                # Determine damage based on bullet owner_ref (if it's a bonus wave enemy)
                if hasattr(bullet, 'owner_ref') and bullet.owner_ref:
                    enemy = bullet.owner_ref
                    # Check if this is a bonus wave enemy by checking if it's in the bonus_wave_enemies group
                    if enemy in self.bonus_wave_enemies and hasattr(enemy, 'enemy_type'):
                        enemy_type = enemy.enemy_type
                        damage_values = {
                            "loaf": 4,
                            "centurion": 4,
                            "emperor": 6,
                            "bluewhale": 8,
                            "ninja": 5
                        }
                        dmg = damage_values.get(enemy_type, 1)
                        # Double damage for NyancatBullet
                        if is_nyancat_bullet:
                            dmg *= 2
                        for shield in shields_hit:
                            shield.take_damage(dmg)
                        bullet.kill()
                    else:
                        # Regular alien bullets
                        dmg = 2 if is_nyancat_bullet else 1
                        for shield in shields_hit:
                            shield.take_damage(dmg)
                        bullet.kill()
                else:
                    # Bullet without owner_ref (shouldn't happen, but handle it)
                    dmg = 2 if is_nyancat_bullet else 1
                    for shield in shields_hit:
                        shield.take_damage(dmg)
                    bullet.kill()
            
            # Kitty sprites collide with shields (use custom hitbox for ninjakitty)
            for enemy in self.bonus_wave_enemies.sprites():
                collision_rect = enemy.get_collision_rect() if hasattr(enemy, 'get_collision_rect') else enemy.rect
                shields_hit = pygame.sprite.spritecollide(enemy, self.shields, dokill=False)
                # Filter shields that actually collide with the hitbox
                shields_hit = [s for s in shields_hit if s.rect.colliderect(collision_rect)]
                if not shields_hit:
                    continue
                # Process collisions for this enemy
                damage_values = {
                    "loaf": 4,
                    "centurion": 4,
                    "emperor": 6,
                    "bluewhale": 8,
                    "ninja": len(self.settings.shield_colors)  # Maximum damage - destroy shield instantly
                }
                dmg = damage_values.get(enemy.enemy_type, 1)
                for shield in shields_hit:
                    shield.take_damage(dmg)
                # Stop nyancat music if nyancat is destroyed and no other nyancats are alive
                if enemy.enemy_type == "nyancat":
                    enemy.kill()  # Kill first, then check if any remain
                    if not any(e.enemy_type == "nyancat" for e in self.bonus_wave_enemies) and self.audio.nyancat_music_channel:
                        self.audio.stop_music_channel(self.audio.nyancat_music_channel)
                        self.audio.nyancat_music_channel = None
                else:
                    # Enemies are destroyed by shield collision
                    enemy.kill()
        
        # Player bullets vs enemies (with custom hitbox support for ninjakitty)
        # Use pygame.sprite.groupcollide for efficient collision detection
        # First pass: get potential collisions using default rects (fast)
        potential_hits = pygame.sprite.groupcollide(
            self.player_bullets, self.bonus_wave_enemies, False, False
        )
        
        bullets_to_kill = []  # List of bullets to remove
        bullets_processed = set()  # Track which bullets we've already added (using id for hashability)
        # Second pass: verify collisions using custom hitboxes where needed
        for bullet, enemies_hit in potential_hits.items():
            for enemy in enemies_hit:
                # Use custom hitbox if available, otherwise use default rect
                collision_rect = enemy.get_collision_rect() if hasattr(enemy, 'get_collision_rect') else enemy.rect
                if bullet.rect.colliderect(collision_rect):
                    # Add bullet only once (even if it hits multiple enemies)
                    bullet_id = id(bullet)
                    if bullet_id not in bullets_processed:
                        bullets_to_kill.append(bullet)
                        bullets_processed.add(bullet_id)
                    was_destroyed = enemy.take_hit()
                    
                    # Track bullet hit (for accuracy calculation)
                    if hasattr(bullet, 'owner_ref') and hasattr(bullet.owner_ref, 'player_id'):
                        player_id = bullet.owner_ref.player_id
                        if player_id in self.player_stats:
                            self.player_stats[player_id]['bullets_hit'] += 1
                            # Track enemy destroyed (bonus wave enemy)
                            if was_destroyed:
                                self.player_stats[player_id]['enemies_destroyed'] += 1
                    
                    # Create firework effect on hit
                    colors = []
                    if enemy.enemy_type == "loaf":
                        colors = [(255, 255, 0)] * 8  # Yellow
                    elif enemy.enemy_type == "centurion":
                        colors = [(255, 0, 0)] * 8  # Red
                    elif enemy.enemy_type == "emperor":
                        colors = [(200, 0, 255)] * 8  # Bright purple
                    elif enemy.enemy_type == "bluewhale":
                        colors = [(100, 190, 255)] * 8  # Light blue
                    elif enemy.enemy_type == "ninja":
                        colors = [(255, 255, 255)] * 8  # White for ninjakitty
                    elif enemy.enemy_type == "nyancat":
                        base_colors = [(255, 0, 0), (255, 192, 203), (255, 165, 0), (0, 255, 0),
                                      (0, 255, 255), (0, 0, 255), (128, 0, 128), (255, 0, 0)]  # Rainbow for nyancat
                        # Cycle colors per hit for visual variety
                        if not hasattr(self, 'nyancat_color_offset'):
                            self.nyancat_color_offset = 0
                        colors = base_colors[self.nyancat_color_offset:] + base_colors[:self.nyancat_color_offset]
                        self.nyancat_color_offset = (self.nyancat_color_offset + 1) % len(base_colors)
                    
                    # Create firework bullets
                    for i in range(8):
                        angle = (i * 45) * (math.pi / 180)
                        # Use hitbox center for nyancat, sprite center for others
                        if enemy.enemy_type == "nyancat" and hasattr(enemy, 'hitbox_rect') and enemy.hitbox_rect:
                            emanation_x, emanation_y = enemy.hitbox_rect.centerx, enemy.hitbox_rect.centery
                        else:
                            emanation_x, emanation_y = enemy.rect.centerx, enemy.rect.centery

                        firework = BonusWaveFirework(
                            self.settings, self.screen,
                            emanation_x, emanation_y,
                            colors[i % len(colors)], angle
                        )
                        self.bonus_wave_fireworks.add(firework)
                    
                    if was_destroyed:
                        # Store enemy type before killing
                        enemy_type = enemy.enemy_type
                        
                        # Stop nyancat music if nyancat is destroyed and no other nyancats are alive
                        if enemy_type == "nyancat":
                            enemy.kill()  # Kill first, then check if any remain
                            if not any(e.enemy_type == "nyancat" for e in self.bonus_wave_enemies) and self.audio.nyancat_music_channel:
                                self.audio.stop_music_channel(self.audio.nyancat_music_channel)
                                self.audio.nyancat_music_channel = None
                        else:
                            enemy.kill()
                        
                        # Award points to player who killed the enemy #bonus wave - scoring
                        if bullet.owner_ref is not None and hasattr(bullet.owner_ref, 'player_score'):
                            score_values = {
                                "loaf": 100,
                                "centurion": 200,
                                "emperor": 300,
                                "bluewhale": 500,
                                "ninja": 250,
                                "nyancat": 1000
                            }
                            points = score_values.get(enemy_type, 0)
                            bullet.owner_ref.player_score += points
                        
                        # Drop powerup using bonus wave probability #bonus wave - drop powerups on enemy death
                        # Nyancat always drops 3 powerups (left/center/right). Other enemies use normal chance.
                        should_drop = (enemy_type == "nyancat") or (random.random() <= self.settings.bonus_wave_powerup_drop_chance)
                        if should_drop:
                            if enemy_type == "nyancat":
                                # Nyancat drops 3 powerups: left edge, center, right edge
                                ptype1 = choose_powerup_type(self.settings, is_bonus_wave=True)
                                ptype2 = choose_powerup_type(self.settings, is_bonus_wave=True)
                                ptype3 = choose_powerup_type(self.settings, is_bonus_wave=True)

                                powerup1 = PowerUpPickup(self.settings, self.screen, ptype1, enemy.rect.left, enemy.rect.centery)
                                powerup2 = PowerUpPickup(self.settings, self.screen, ptype2, enemy.rect.centerx, enemy.rect.centery)
                                powerup3 = PowerUpPickup(self.settings, self.screen, ptype3, enemy.rect.right, enemy.rect.centery)

                                self.powerups.add(powerup1, powerup2, powerup3)
                            else:
                                ptype = choose_powerup_type(self.settings, is_bonus_wave=True)  # bonus wave - choose dad or mom (50/50)
                                powerup = PowerUpPickup(self.settings, self.screen, ptype, enemy.rect.centerx, enemy.rect.centery)
                                self.powerups.add(powerup)
                        
                        # Note: Defense strength is only reduced when enemies breach the bottom, not when killed
                        enemy.kill()
                    break  # Only process first collision per bullet
        
        # Remove bullets that hit enemies
        for bullet in bullets_to_kill:
            bullet.kill()
        
        # Shockwaves vs bonus wave enemies #bonus wave - shockwaves damage kitty sprites
        for sw in self.shockwaves.sprites():
            # Use custom collision detection for enemies with custom hitboxes
            for enemy in self.bonus_wave_enemies.sprites():
                collision_rect = enemy.get_collision_rect() if hasattr(enemy, 'get_collision_rect') else enemy.rect
                if not sw.rect.colliderect(collision_rect):
                    continue
                # Skip if this shockwave has already hit this enemy
                if enemy in sw.hit_aliens:
                    continue
                
                # Mark as hit before applying damage to prevent multiple hits
                sw.hit_aliens.add(enemy)
                
                # Apply 2 damage to kitty sprites
                enemy.damage_stage += 2
                was_destroyed = enemy.damage_stage >= enemy.max_damage
                
                # Create firework effect on hit (same as bullet hits)
                colors = []
                if enemy.enemy_type == "loaf":
                    colors = [self.settings.loafkitty_firework_color] * 8
                elif enemy.enemy_type == "centurion":
                    colors = [self.settings.centurionkitty_firework_color] * 8
                elif enemy.enemy_type == "emperor":
                    colors = [self.settings.emperorkitty_firework_color] * 8
                elif enemy.enemy_type == "bluewhale":
                    colors = [self.settings.bluewhalekitty_firework_color] * 8
                elif enemy.enemy_type == "ninja":
                    colors = [self.settings.ninjakitty_firework_color] * 8
                elif enemy.enemy_type == "nyancat": # rainbow for nyancat
                    base_colors = self.settings.nyancat_rainbow_colors
                    # Cycle colors per hit for visual variety
                    if not hasattr(self, 'nyancat_color_offset'):
                        self.nyancat_color_offset = 0
                    colors = base_colors[self.nyancat_color_offset:] + base_colors[:self.nyancat_color_offset]
                    self.nyancat_color_offset = (self.nyancat_color_offset + 1) % len(base_colors)
                
                # Create firework bullets
                for i in range(8):
                    angle = (i * 45) * (math.pi / 180)
                    # Use hitbox center for nyancat, sprite center for others
                    if enemy.enemy_type == "nyancat" and hasattr(enemy, 'hitbox_rect') and enemy.hitbox_rect:
                        emanation_x, emanation_y = enemy.hitbox_rect.centerx, enemy.hitbox_rect.centery
                    else:
                        emanation_x, emanation_y = enemy.rect.centerx, enemy.rect.centery

                    firework = BonusWaveFirework(
                        self.settings, self.screen,
                        emanation_x, emanation_y,
                        colors[i % len(colors)], angle
                    )
                    self.bonus_wave_fireworks.add(firework)
                
                if was_destroyed:
                    # Store enemy type before killing
                    enemy_type = enemy.enemy_type
                    
                    # Stop nyancat music if nyancat is destroyed and no other nyancats are alive
                    if enemy_type == "nyancat":
                        enemy.kill()  # Kill first, then check if any remain
                        if not any(e.enemy_type == "nyancat" for e in self.bonus_wave_enemies) and self.audio.nyancat_music_channel:
                            self.audio.stop_music_channel(self.audio.nyancat_music_channel)
                            self.audio.nyancat_music_channel = None
                    else:
                        enemy.kill()
                    
                    # Award points to shockwave owner #bonus wave - scoring
                    if hasattr(sw, 'owner') and sw.owner and hasattr(sw.owner, 'player_score'):
                        score_values = {
                            "loaf": 100,
                            "centurion": 200,
                            "emperor": 300,
                            "bluewhale": 500,
                            "ninja": 250,
                            "nyancat": 1000
                        }
                        points = score_values.get(enemy_type, 0)
                        sw.owner.player_score += points
                    
                    # Drop powerup using bonus wave probability #bonus wave - drop powerups on enemy death
                    # Nyancat always drops 3 powerups (left/center/right). Other enemies use normal chance.
                    should_drop = (enemy_type == "nyancat") or (random.random() <= self.settings.bonus_wave_powerup_drop_chance)
                    if should_drop:
                        if enemy_type == "nyancat":
                            # Nyancat drops 3 powerups: left edge, center, right edge
                            ptype1 = choose_powerup_type(self.settings, is_bonus_wave=True)
                            ptype2 = choose_powerup_type(self.settings, is_bonus_wave=True)
                            ptype3 = choose_powerup_type(self.settings, is_bonus_wave=True)

                            powerup1 = PowerUpPickup(self.settings, self.screen, ptype1, enemy.rect.left, enemy.rect.centery)
                            powerup2 = PowerUpPickup(self.settings, self.screen, ptype2, enemy.rect.centerx, enemy.rect.centery)
                            powerup3 = PowerUpPickup(self.settings, self.screen, ptype3, enemy.rect.right, enemy.rect.centery)

                            self.powerups.add(powerup1, powerup2, powerup3)
                        else:
                            ptype = choose_powerup_type(self.settings, is_bonus_wave=True)  # bonus wave - choose dad or mom (50/50)
                            powerup = PowerUpPickup(self.settings, self.screen, ptype, enemy.rect.centerx, enemy.rect.centery)
                            self.powerups.add(powerup)
                    
                    enemy.kill()
        
        # Dad shockwave collisions with kitties (hits every frame, 1 damage per hit)
        # Use custom collision detection for enemies with custom hitboxes
        for shockwave in self.dad_shockwaves.sprites():
            for enemy in self.bonus_wave_enemies.sprites():
                collision_rect = enemy.get_collision_rect() if hasattr(enemy, 'get_collision_rect') else enemy.rect
                if not shockwave.rect.colliderect(collision_rect):
                    continue
                # Apply damage (1 damage per frame collision)
                was_destroyed = enemy.take_hit()  # Returns True if destroyed
                
                # Create firework effect on hit (every frame while colliding)
                colors = []
                if enemy.enemy_type == "loaf":
                    colors = [self.settings.loafkitty_firework_color] * 8  # Yellow
                elif enemy.enemy_type == "centurion":
                    colors = [self.settings.centurionkitty_firework_color] * 8  # Red
                elif enemy.enemy_type == "emperor":
                    colors = [self.settings.emperorkitty_firework_color] * 8  # Bright purple
                elif enemy.enemy_type == "bluewhale":
                    colors = [self.settings.bluewhalekitty_firework_color] * 8  # Light blue
                elif enemy.enemy_type == "ninja":
                    colors = [(self.settings.ninjakitty_firework_color)] * 8  # White for ninjakitty
                elif enemy.enemy_type == "nyancat":
                    base_colors = self.settings.nyancat_rainbow_colors  # Rainbow for nyancat
                    # Cycle colors per hit for visual variety
                    if not hasattr(self, 'nyancat_color_offset'):
                        self.nyancat_color_offset = 0
                    colors = base_colors[self.nyancat_color_offset:] + base_colors[:self.nyancat_color_offset]
                    self.nyancat_color_offset = (self.nyancat_color_offset + 1) % len(base_colors)
                
                # Create firework bullets
                for i in range(8):
                    angle = (i * 45) * (math.pi / 180)
                    # Use hitbox center for nyancat, sprite center for others
                    if enemy.enemy_type == "nyancat" and hasattr(enemy, 'hitbox_rect') and enemy.hitbox_rect:
                        emanation_x, emanation_y = enemy.hitbox_rect.centerx, enemy.hitbox_rect.centery
                    else:
                        emanation_x, emanation_y = enemy.rect.centerx, enemy.rect.centery

                    firework = BonusWaveFirework(
                        self.settings, self.screen,
                        emanation_x, emanation_y,
                        colors[i % len(colors)], angle
                    )
                    self.bonus_wave_fireworks.add(firework)
                
                # Kill enemy if destroyed
                if was_destroyed:
                    # Store enemy type before killing
                    enemy_type = enemy.enemy_type
                    
                    # Stop nyancat music if nyancat is destroyed and no other nyancats are alive
                    if enemy_type == "nyancat":
                        enemy.kill()  # Kill first, then check if any remain
                        if not any(e.enemy_type == "nyancat" for e in self.bonus_wave_enemies) and self.audio.nyancat_music_channel:
                            self.audio.stop_music_channel(self.audio.nyancat_music_channel)
                            self.audio.nyancat_music_channel = None
                    else:
                        # Award points if applicable (dad shockwaves don't have owner_ref, so no scoring)
                        enemy.kill()
        
        # Mom bullet collisions with players (heal players +1 health each AND create/charge mobile shields)
        player_hits = pygame.sprite.groupcollide(self.mom_bullets, self.players, False, False)
        bullets_hit_players = set()
        for bullet, players_hit in player_hits.items():
            for player in players_hit:
                if player.player_state == "alive":
                    # Heal player by +1 health (up to max)
                    if hasattr(player, 'player_health') and hasattr(player, 'heal'):
                        player.heal(1)  # Use player's heal method
                        self._trigger_hud_flash(player, "hp")  # Flash HP indicator

                    # Create/charge mobile shield in front of player
                    if player.player_id not in self.player_shields or not self.player_shields[player.player_id].alive():
                        # Create shield above player - store reference to player for tracking
                        # Shield thickness is 1/2 of normal (10px instead of 20px)
                        shield = Shield(self.settings, pygame.Rect(player.rect.left, player.rect.top - 10, player.rect.width, 10))
                        shield.tracked_player = player  # bonus wave - store player reference for tracking
                        self.shields.add(shield)
                        self.player_shields[player.player_id] = shield
                    else:
                        # Charge shield (heal by 1 level)
                        self.player_shields[player.player_id].heal(1)
                    bullets_hit_players.add(bullet)
        
        # Mom bullet collisions with stationary shields (respawn dead shields and charge alive ones)
        if self.settings.orbital_shields_enabled and hasattr(self, 'shield_slots') and self.shield_slots:
            # Check collisions with existing shields (alive shields)
            shield_hits = pygame.sprite.groupcollide(self.mom_bullets, self.shields, False, False)
            bullets_hit_shields = set()
            for bullet, shields_hit in shield_hits.items():
                # Skip bullets that already hit players
                if bullet in bullets_hit_players:
                    continue
                for shield in shields_hit:
                    # Skip mobile shields (mom-created shields with tracked_player)
                    if hasattr(shield, 'tracked_player') and shield.tracked_player:
                        continue
                    # This is a stationary shield - heal it by 1 stage
                    if shield.heal(1):  # Returns True if stage improved
                        self.audio.play("shield_recharge")  # Play sound when shield stage improves
                    bullets_hit_shields.add(bullet)
                    break  # Only process first shield hit per bullet
            
            # Check for dead shields that need respawning
            # Find bullets that didn't hit players or alive shields but might hit dead shield slots
            for bullet in self.mom_bullets.sprites():
                if bullet in bullets_hit_players or bullet in bullets_hit_shields:
                    continue  # Skip bullets that already hit something
                
                # Check if bullet collides with any shield slot position
                for slot_idx, slot_rect in enumerate(self.shield_slots):
                    if bullet.rect.colliderect(slot_rect):
                        # Check if there's no shield at this slot (shield was killed)
                        shield_at_slot = None
                        for shield in self.shields:
                            if not hasattr(shield, 'tracked_player') or not shield.tracked_player:
                                # This is a stationary shield
                                if shield.rect.colliderect(slot_rect):
                                    shield_at_slot = shield
                                    break
                        
                        if shield_at_slot is None:
                            # No shield at this slot - create it at max damage (worst state)
                            new_shield = Shield(self.settings, slot_rect.copy())
                            # Set to max damage (highest stage_index = worst state)
                            max_damage_index = len(self.settings.shield_colors) - 1
                            new_shield.stage_index = max_damage_index
                            new_shield._sync_color()  # Update color to reflect max damage state
                            self.shields.add(new_shield)
                            bullets_hit_shields.add(bullet)
                            break  # Only create one shield per bullet
            
            # Remove all bullets that hit shields (alive or respawned)
            for bullet in bullets_hit_shields:
                bullet.kill()
        
        # Remove bullets that hit players
        for bullet in bullets_hit_players:
            bullet.kill()
        
        # Kitty bullets vs squadrons #bonus wave - kitty bullets damage squadrons
        squadron_is_hit = pygame.sprite.groupcollide(self.alien_bullets, self.squadrons, False, False)
        for bullet, squadrons_hit in squadron_is_hit.items():
            is_laserminion_bomb = isinstance(bullet, LaserminionBomb)
            # Only process collisions with kitty bullets (bonus wave enemy bullets)
            # Check if bullet has owner_ref that's a bonus wave enemy
            if hasattr(bullet, 'owner_ref') and bullet.owner_ref:
                if bullet.owner_ref in self.bonus_wave_enemies:
                    for squadron in squadrons_hit:
                        was_alive = squadron.alive()  # Check if squadron was alive before taking hit
                        squadron.take_hit(1)  # 1 damage per hit
                        # Play death sound if squadron just died
                        if was_alive and not squadron.alive():
                            self.audio.play("powerup_squadron_death")
                        
                        # Apply LaserminionBomb knockback
                        if is_laserminion_bomb:
                            # LaserminionBomb: sideways knockback (1/2 squadron width)
                            # Direction: if bomb hits LEFT of centerx, bump RIGHT; if RIGHT of centerx, bump LEFT
                            if bullet.rect.centerx < squadron.rect.centerx:
                                direction = 1  # Bump right
                            else:
                                direction = -1  # Bump left
                            bump_distance = squadron.rect.width // 2
                            squadron.rect.x += direction * bump_distance
                            # Clamp to screen bounds
                            if squadron.rect.left < 0:
                                squadron.rect.left = 0
                            if squadron.rect.right > self.settings.screen_width:
                                squadron.rect.right = self.settings.screen_width
                            # Update squadron's internal position if it has one
                            if hasattr(squadron, 'x'):
                                squadron.x = float(squadron.rect.x)
                    
                    # Kill bullet after impact (LaserminionBomb disappears)
                    if is_laserminion_bomb:
                        bullet.kill()
                    else:
                        bullet.kill()  # Remove bullet after collision
        
        # Alien bullets vs players
        player_is_hit = pygame.sprite.groupcollide(self.alien_bullets, self.players, False, False)
        if player_is_hit:
            for bullet, ships_hit in player_is_hit.items():
                # Check for special bullet types (once per bullet, not per ship)
                is_nyancat_bullet = isinstance(bullet, NyancatBullet)
                is_laserminion_bomb = isinstance(bullet, LaserminionBomb)
                
                for ship in ships_hit:
                    # If ship is respawning:
                    if ship.player_state in ("between_lives", "respawning"):
                        continue
                    else:
                        # Determine damage
                        if is_nyancat_bullet:
                            damage = 3  # Triple damage for NyancatBullet
                        else:
                            damage = 1  # Normal damage
                        
                        ship.player_health -= damage
                        # Track damage taken
                        if ship.player_id in self.player_stats:
                            self.player_stats[ship.player_id]['damage_taken'] += damage
                        self._trigger_hud_flash(ship, "hp")
                        self.audio.play("bullet_hit")
                        ship.trigger_hit_animation(350)  # Trigger hit animation (shorter than HUD flash duration)
                        
                        # Apply knockback effects
                        if is_nyancat_bullet:
                            # NyancatBullet: knockback downward by ship height
                            knockback_distance = ship.rect.height
                            ship.rect.y += knockback_distance
                            # Clamp to screen bounds
                            if ship.rect.bottom > self.settings.play_height:
                                ship.rect.bottom = self.settings.play_height
                            ship.y = float(ship.rect.y)
                        elif is_laserminion_bomb:
                            # LaserminionBomb: sideways knockback (1/2 ship width)
                            # Direction: if bomb hits LEFT of centerx, bump RIGHT; if RIGHT of centerx, bump LEFT
                            if bullet.rect.centerx < ship.rect.centerx:
                                direction = 1  # Bump right
                            else:
                                direction = -1  # Bump left
                            bump_distance = ship.rect.width // 2
                            ship.rect.x += direction * bump_distance
                            # Clamp to screen bounds
                            if ship.rect.left < 0:
                                ship.rect.left = 0
                            if ship.rect.right > self.settings.screen_width:
                                ship.rect.right = self.settings.screen_width
                            ship.x = float(ship.rect.x)
                        
                        if ship.player_health <= 0:
                            ship.player_lives -= 1
                            # Track lives lost
                            if ship.player_id in self.player_stats:
                                self.player_stats[ship.player_id]['lives_lost'] += 1
                            self._trigger_hud_flash(ship, "lives")
                            self.audio.play("player_life_lost")
                            ship.player_health = ship.current_max_health
                            if ship.player_lives >= 0:
                                self._start_player_respawn_timer(ship)
                            elif ship.player_lives < 0:
                                self._player_death(ship)
                # Kill bullet after processing all ships (NyancatBullet and LaserminionBomb disappear after impact)
                if (is_nyancat_bullet or is_laserminion_bomb) and bullet.alive():
                    bullet.kill()
                elif bullet.alive():
                    bullet.kill()  # Normal bullets also get killed
        
        # Enemies vs players (collision) - bonus wave - use bump behavior for all cat sprites
        # Use custom collision detection for enemies with custom hitboxes
        for enemy in self.bonus_wave_enemies.sprites():
            collision_rect = enemy.get_collision_rect() if hasattr(enemy, 'get_collision_rect') else enemy.rect
            # Check collision with each player using custom hitbox
            for player in self.players.sprites():
                if not player.rect.colliderect(collision_rect):
                    continue
                # First check if they are respawning
                if player.player_state in ("respawning", "between_lives"):
                    continue
                else:
                        # All bonus wave enemies use bump behavior (2 damage + knockback, don't destroy enemy)
                        damage = 2
                        player.player_health -= damage
                        self._trigger_hud_flash(player, "hp")
                        player.trigger_hit_animation(450)  # Trigger hit animation (matches HUD flash duration)
                        self.audio.play("player_collide")
                        bump_distance = (enemy.rect.width // 2) + (player.rect.width // 2) + 4
                        direction = -1 if player.rect.centerx < enemy.rect.centerx else 1
                        player.rect.x += direction * bump_distance
                        # Clamp to screen bounds and sync float position
                        if player.rect.left < 0:
                            player.rect.left = 0
                        if player.rect.right > self.settings.screen_width:
                            player.rect.right = self.settings.screen_width
                        player.x = float(player.rect.x)
                        
                        # Handle life losses
                        if player.player_health <= 0:
                            player.player_lives -= 1
                            self._trigger_hud_flash(player, "lives")
                            self.audio.play("player_life_lost")
                            player.player_health = player.current_max_health
                            if player.player_lives >= 0:
                                self._start_player_respawn_timer(player)
                            else:
                                self._player_death(player)
                # Lifepod-bonus wave enemy collisions (trigger respawn animation)
        # Use custom collision detection for enemies with custom hitboxes
        for lifepod in self.lifepods.sprites():
            if lifepod.state != "normal":  # Skip if already respawning
                continue
            for enemy in self.bonus_wave_enemies.sprites():
                collision_rect = enemy.get_collision_rect() if hasattr(enemy, 'get_collision_rect') else enemy.rect
                if lifepod.rect.colliderect(collision_rect):
                    lifepod.start_respawn()
                    break  # Only trigger once per collision
            if lifepod.state != "normal":  # If respawn was triggered, don't check bullets
                continue

        # Lifepod-bonus wave enemy bullet collisions (trigger respawn animation)
        # Filter for bonus wave enemy bullets (those with owner_ref in bonus_wave_enemies)
        for lifepod in self.lifepods.sprites():
            if lifepod.state != "normal":  # Skip if already respawning
                continue
            for bullet in self.alien_bullets.sprites():
                # Check if this is a bonus wave enemy bullet
                if hasattr(bullet, 'owner_ref') and bullet.owner_ref and bullet.owner_ref in self.bonus_wave_enemies:
                    if lifepod.rect.colliderect(bullet.rect):
                        lifepod.start_respawn()
                        bullet.kill()  # Remove bullet after collision
                        break  # Only trigger once per collision
        # Enemies that breach bottom
        for enemy in self.bonus_wave_enemies:
            if enemy.rect.top > self.settings.play_height:
                breach_value = self.settings.bonus_wave_breach_values[enemy.enemy_type]
                self.bonus_wave_defense_strength -= breach_value
                enemy.kill()
    
    def _init_bonus_wave_defeat_screen(self):
        """Initialize bonus wave defeat screen"""
        # Stop all sounds before showing defeat screen
        # Stop all alien hum sounds
        for alien in self.aliens:
            if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                alien.hum_sound_channel.stop()
                alien.hum_sound_channel = None
        # Stop all lasertanker firing sounds
        for alien, channel in list(self.audio.lasertanker_firing_sound_channels.items()):
            if channel:
                channel.stop()
        self.audio.lasertanker_firing_sound_channels.clear()
        # Stop nyancat music
        if self.audio.nyancat_music_channel:
            self.audio.stop_music_channel(self.audio.nyancat_music_channel)
            self.audio.nyancat_music_channel = None
        
        # Set defeat screen start time for delayed music
        self.defeat_screen_start_time = pygame.time.get_ticks()
        
        # Store player data before they're removed from sprite group
        self._store_final_player_data()
        # Defeat banner scrolls right to left (left edge positioning)
        try:
            font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf'))
            calc_font = pygame.font.Font(font_path, int(self.settings.screen_height * 0.14))
        except:
            calc_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.14))
        banner_text = "THE PROPHECY IS... ... ... ... ... TRUE?"
        banner_width = calc_font.size(banner_text)[0]
        self.defeat_banner_x = self.settings.screen_width  # bonus wave - start from right (left edge at screen_width)
        self.defeat_banner_active = True
        self.credits_y = self.settings.screen_height_total  # bonus wave - start below screen
        self.credits_active = False
        self.thanks_active = False
        # Initialize credits section tracking
        self.credits_section_index = 0
        self.credits_section_start_y = self.credits_y
        self.credits_initial_y = self.credits_y
        try:
            # bonus wave - load and scale the special defeat background
            defeat_bg = pygame.image.load(self.settings.bonus_wave_defeat_bg_path).convert()
            self.bg_defeat = pygame.transform.scale(defeat_bg, (self.settings.screen_width, self.settings.screen_height))
        except:
            self.bg_defeat = self.bg_starter  # Fallback if image not found
    
    def _init_bonus_wave_victory_screen(self):
        """Initialize bonus wave victory screen (20 minutes)"""
        # Stop all sounds before showing victory screen
        # Stop all alien hum sounds
        for alien in self.aliens:
            if hasattr(alien, 'hum_sound_channel') and alien.hum_sound_channel:
                alien.hum_sound_channel.stop()
                alien.hum_sound_channel = None
        # Stop all lasertanker firing sounds
        for alien, channel in list(self.audio.lasertanker_firing_sound_channels.items()):
            if channel:
                channel.stop()
        self.audio.lasertanker_firing_sound_channels.clear()
        # Stop nyancat music
        if self.audio.nyancat_music_channel:
            self.audio.stop_music_channel(self.audio.nyancat_music_channel)
            self.audio.nyancat_music_channel = None
        
        # Set victory screen start time for delayed music
        self.victory_screen_start_time = pygame.time.get_ticks()
        
        # Store player data before they're removed from sprite group
        self._store_final_player_data()
        self.victory_banner_text = "THE PROPHECY IS ... ... ... ... ... ... ... ... ... ... TRUE!!!!!!!!!"
        # Victory banner scrolls right to left (left edge positioning)
        try:
            font_path = resource_path(os.path.join('assets', 'BAUHS93.ttf'))
            calc_font = pygame.font.Font(font_path, int(self.settings.screen_height * 0.14))
        except:
            calc_font = pygame.font.SysFont(None, int(self.settings.screen_height * 0.14))
        banner_width = calc_font.size(self.victory_banner_text)[0]
        self.victory_banner_x = self.settings.screen_width  # bonus wave - start from right (left edge at screen_width)
        self.victory_banner_active = True
        self.credits_y = self.settings.screen_height_total  # bonus wave - start below screen
        self.credits_active = False
        self.thanks_active = False
        # Initialize credits section tracking
        self.credits_section_index = 0
        self.credits_section_start_y = self.credits_y
        self.credits_initial_y = self.credits_y
        try:
            # bonus wave - load and scale the perfect victory background
            victory_bg = pygame.image.load(self.settings.bonus_wave_victory_bg_path).convert()
            self.bg_victory = pygame.transform.scale(victory_bg, (self.settings.screen_width, self.settings.screen_height))
        except:
            self.bg_victory = self.bg_starter  # Fallback if image not found
    
    def _draw_bonus_wave(self):
        """Draw bonus wave enemies and effects"""
        for enemy in self.bonus_wave_enemies:
            enemy.draw()
        for firework in self.bonus_wave_fireworks:
            firework.draw()

    def _powerup_line(self, player_id: int, ship) -> str:
        #keys = self._get_player_keys_dict(player_id)

        # Pull the actual pygame key constants from your dict
        #k_squad = keys["squadron"]
        #k_shock = keys["shockwave"]
        #k_nano  = keys["nanites"]

        # Convert pygame key constants into readable labels ("q", "rshift", etc.)
        #k_squad_name = pygame.key.name(k_squad).upper()
        #k_shock_name = pygame.key.name(k_shock).upper()
        #k_nano_name  = pygame.key.name(k_nano).upper()

        return (
            f"POWERUPS: "
            f"Squadrons: {ship.powerups.get('squadron', 0)} | "
            f"Shockwaves: {ship.powerups.get('shockwave', 0)} | "
            f"Nanites: {ship.powerups.get('nanites', 0)} |"
        )
    #def _get_player_keys_dict(self, player_id: int) -> dict:
        #"""helper for _powerup_line() to access player keys dictionary in base_settings.py"""
    # settings.player1_keys, settings.player2_keys, etc.
        #return getattr(self.settings, f"player{player_id}_keys")

if __name__ == "__main__":

    gameinstance = AlienInvasion()
    gameinstance.Main_Game_Loop()
