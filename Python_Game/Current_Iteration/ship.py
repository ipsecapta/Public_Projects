#!/usr/bin/env python3
#
# Project: Final Project
#
# Files needed by this file: 
#       ship.py (this file)
#       Visintainer_A_AlienGame.py (main file)
#       All images whose paths in the /img directory are referenced (e.g. see lines 18-21 below)
#
# Author: Anthony Visintainer
# Date: 8 December 2025
# 
# This file models the player ships' level, mechanics, and appearance. 
# For other ship settings (movement speed, firing speed, etc) check the base_settings.py file. 
import pygame
from base_settings import resource_path

ship1_path = resource_path("img/blueship.png")
ship2_path = resource_path("img/redship.png")
ship3_path = resource_path("img/cyanship.png")
ship4_path = resource_path("img/pinkship.png")
ship1_hit_path = resource_path("img/blueship_hit.png")
ship2_hit_path = resource_path("img/redship_hit.png")
ship3_hit_path = resource_path("img/cyanship_hit.png")
ship4_hit_path = resource_path("img/pinkship_hit.png")

# Escape pod paths
escapepod1_path = resource_path("img/blue_escapepod.png")
escapepod2_path = resource_path("img/red_escapepod.png")
escapepod3_path = resource_path("img/cyan_escapepod.png")
escapepod4_path = resource_path("img/pink_escapepod.png")

# Escape pod respawn paths
escapepod_respawn1_path = resource_path("img/blue_escapepod_respawn.png")
escapepod_respawn2_path = resource_path("img/red_escapepod_respawn.png")
escapepod_respawn3_path = resource_path("img/cyan_escapepod_respawn.png")
escapepod_respawn4_path = resource_path("img/pink_escapepod_respawn.png")

#search below for respawn_path to find path for respawn images.

class Ship(pygame.sprite.Sprite): #create a Ship class, that is a sub-class of the pygame Sprite class.
    def __init__(self, settings, screen, player_id, player_level=0, player_health=11, player_lives=3, player_score = 0, player_state = "alive", sound_callback=None):
        super().__init__()
        self.settings = settings # WHEN THE SHIP OBJECT(S) ARE CREATED IN THE MAIN FILE, THE VALUE PASSED FOR this .settings parameter WILL BE -->
                                 #--> the Settings() class object created from the Settings class imported from the base_settings module.
        self.screen = screen
        self.player_id = player_id
        self.player_level = player_level
        self.player_score = player_score
        self.firing = False # This attribute is to allow for button holding to fire, instead of having to tap the fire button over and over. This becomes important at higher levels.
        self.next_fire_time = 0
        self.player_health = player_health
        self.player_lives = player_lives
        self.player_state = player_state # options are "alive", "between lives", and "dead"
        self.current_max_health = 10 + player_level # init this attribute for later use 
        self.hp_flash_until_ms = 0
        self.lives_flash_until_ms = 0
        self.hit_animation_until_ms = 0  # Timer for hit animation sprite swap
        self.level_up_line_y = -1  # -1 means no animation active, otherwise tracks the white line position
        self.level_up_animation_count = 0  # Counter for how many times the animation has completed
        self.previous_level = player_level  # Track previous level to detect level ups
        self.sound_callback = sound_callback  # Callback function to play sounds (e.g., level up)

        #set powerup inventories
        self.powerups = {"squadron": 0, "shockwave": 0, "nanites": 0, "dad": 0, "mom": 0}  # bonus wave - dad and mom powerups
        # HUD flash timers for inventory pickups (per powerup type)
        self.powerup_flash_until_ms = {
            "squadron": 0,
            "nanites": 0,
            "shockwave": 0
        }
        self.squadron_left = None
        self.squadron_right = None
        
        # Track powerup usage for credits
        self.powerups_used = {"squadron": 0, "shockwave": 0, "nanites": 0, "dad": 0, "mom": 0}  # bonus wave - track dad and mom usage

        #initting respawn-related attributes:
        self.respawn_target_y = int(self.settings.screen_height * 0.99) #respawn is further back than initial spawn - bottom of screen basically, hopefully behind safety of shields.
        self.respawn_fly_speed = 6.0 #player flies back to spawn very quickly.
        self.respawn_end_time = None # init this variable in a none state; but it will be set to implement the length of the respawn cycle.

        # Pick a sprite image and movement key set, based on player:
        if player_id == 1: #for player 1
            image_path = ship1_path #use the path determined above for the image of player 1s ship.
            hit_image_path = ship1_hit_path
            self.keys = settings.player1_keys #The movement keys for player 1 are drawn from the player1_keys dictionary in the base_settings module
        elif player_id == 2:
            image_path = ship2_path #SAME AS ABOVE BUT FOR PLAYER 2
            hit_image_path = ship2_hit_path
            self.keys = settings.player2_keys #SAME AS ABOVE BUT FOR PLAYER 2
        elif player_id == 3:
            image_path = ship3_path #SAME AS ABOVE BUT FOR PLAYER 2
            hit_image_path = ship3_hit_path
            self.keys = settings.player3_keys #SAME AS ABOVE BUT FOR PLAYER 2
        elif player_id == 4:
            image_path = ship4_path #SAME AS ABOVE BUT FOR PLAYER 2
            hit_image_path = ship4_hit_path
            self.keys = settings.player4_keys #SAME AS ABOVE BUT FOR PLAYER 2

        # Store ship image path for lifepod creation
        self.ship_image_path = image_path

        #load each image from its path, and scale each image
        self.image = pygame.image.load(image_path).convert_alpha() #use the convert_alpha() method to load the image in rgba, such that its transparent background (a.k.a. alpha channel) is maintained (as a png)
        self.image = pygame.transform.smoothscale(self.image, (round(self.settings.multiplayer_resizer*60), round(self.settings.multiplayer_resizer*40))) #set each image scale to 60x40 pixels.
        
        # Load hit animation image
        try:
            self.hit_image = pygame.image.load(hit_image_path).convert_alpha()
            self.hit_image = pygame.transform.smoothscale(self.hit_image, self.image.get_size())
        except Exception:
            # Fallback to normal image if hit image is missing
            self.hit_image = self.image
        
        # Get rectangle of ship sprite:
        self.rect = self.image.get_rect()

        #try/except to attempt to load a respawning image from preset path:
        try:
            respawn_path = resource_path(f"img/player{self.player_id}_respawning.png") #self-adjusting variable to state the image path. 
            self.respawn_image = pygame.image.load(respawn_path).convert_alpha() #load image based on path; convert it to render rgba
            self.respawn_image = pygame.transform.scale(self.respawn_image, self.image.get_size())#scale the sprite
        except Exception:
            #just in case a filename goes missing or something:
            self.respawn_image = self.image

        #place ship at starting position:
        if player_id == 1:
            self.rect.centerx = settings.screen_width * 0.65 # player 1 starts 70% of the screen length from left.
        elif player_id == 2:
            self.rect.centerx = settings.screen_width * 0.35 # player 2 starts 30% of screen length from left.
        elif player_id == 3:
            self.rect.centerx = settings.screen_width * 0.85
        elif player_id == 4:
            self.rect.centerx = settings.screen_width * 0.15

        self.rect.bottom = int(settings.screen_height * 0.9) # all players start toward the bottom of the screen vertically.

        # Store x and y coordinates as decimals, for accurate & smooth movement
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        # Movement flags: ship starts on the screen, not moving - movement booleans all set to false.
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False

    def update(self): # a function for ship movement

        #first, set up a getattr statement for all levels above 1, to let ships get faster and stronger with higher levels:
        if self.player_level !=1:
            self.speed = getattr(self.settings, f"lvl{self.player_level}_speed") 
            self.current_max_health = self.settings.player_starting_health + self.player_level # max health goes up with player level - this number will be useful when respawning or healing players.
        else:
            self.speed = self.settings.base_ship_speed

        if self.player_state == "alive": #NORMAL MOVEMENT AND LEVELING UP
            # Horizontal movement
            if self.moving_left and self.rect.left > 0: # if the left side of the ship sprite's rectangle is not past x=0 (the left edge of screen), -->
                self.x -= self.speed #--> then increment ship position leftward by one unispeed defined in the settings file.
            if self.moving_right and self.rect.right < self.settings.screen_width: #if the right side of the ship's sprite's rectangle is not past the maximum screen width (screen right edge)-->
                self.x += self.speed #-->then increment ship position rightward by one unispeed etc.

            # Vertical movement : same as above, but with vertical coordinates and motion.
            if self.moving_up and self.rect.top > 0:
                self.y -= self.speed
            if self.moving_down and self.rect.bottom < self.settings.screen_height:
                self.y += self.speed
       
            self.rect.x = int(self.x) #return float value for x location to an integer value, so that it can be drawn (blit only accepts integers, since you can't draw between pixels)
            self.rect.y = int(self.y) #same as above, but for y location

            # Update level up animation line position
            if self.level_up_line_y != -1:
                self.level_up_line_y -= 2  # Move upward at speed 2
                if self.level_up_line_y < self.rect.top:
                    self.level_up_animation_count += 1  # Increment completion counter
                    if self.level_up_animation_count < 8:
                        self.level_up_line_y = self.rect.bottom  # Restart from bottom
                    else:
                        self.level_up_line_y = -1  # Animation fully complete after 8 cycles

            #Block of code to adjust player_level based on how much xp they've earned. Threshholds are set in base_settings file.
            # In Kiddie mode, players stay at level 10 (never change level)
            if hasattr(self.settings, 'difficulty_mode') and self.settings.difficulty_mode.lower() == "kiddie":
                self.player_level = 10  # Always level 10 in Kiddie mode
            else:
                # Normal leveling logic
                old_level = self.player_level
                if self.player_score in self.settings.lvl1_xp_requirement:
                    self.player_level = 1
                elif self.player_score in self.settings.lvl2_xp_requirement:
                    self.player_level = 2
                elif self.player_score in self.settings.lvl3_xp_requirement:
                    self.player_level = 3
                elif self.player_score in self.settings.lvl4_xp_requirement:
                    self.player_level = 4
                elif self.player_score in self.settings.lvl5_xp_requirement:
                    self.player_level = 5
                elif self.player_score in self.settings.lvl6_xp_requirement:
                    self.player_level = 6
                elif self.player_score in self.settings.lvl7_xp_requirement:
                    self.player_level = 7
                elif self.player_score in self.settings.lvl8_xp_requirement:
                    self.player_level = 8
                elif self.player_score in self.settings.lvl9_xp_requirement:
                    self.player_level = 9
                elif self.player_score in self.settings.lvl10_xp_requirement:
                    self.player_level = 10
                elif self.player_score >= self.settings.lvl11_xp_requirement:
                    self.player_level = 11


            # Check for level up and start animation
            if self.player_level > self.previous_level and self.level_up_line_y == -1:
                # Level increased! Start the level up animation
                self.level_up_line_y = self.rect.bottom  # Start at bottom of sprite
                self.level_up_animation_count = 0  # Reset animation counter
                # Play level up sound if callback is provided
                if self.sound_callback:
                    self.sound_callback()
            self.previous_level = self.player_level

            #set up needs_heal attribute for nanites to check. 
            if self.player_health < self.current_max_health:
                self.needs_heal = True
            else:
                self.needs_heal = False
        elif self.player_state == "between_lives":
            # Fly down to bottom of screen at a fixed speed, ignore movement flags
            self.y += self.respawn_fly_speed
            if self.rect.bottom < self.respawn_target_y:
                self.rect.y = int(self.y)
            else:
                # Clamp to target and switch to respawning state (parked)
                self.rect.bottom = self.respawn_target_y
                self.y = float(self.rect.y)
                self.player_state = "respawning"

        elif self.player_state == "respawning":
            # Park at bottom; allow horizontal movement to avoid enemy fire
            # Horizontal movement (left-right only)
            if self.moving_left and self.rect.left > 0:
                self.x -= self.speed
            if self.moving_right and self.rect.right < self.settings.screen_width:
                self.x += self.speed
            
            # Update x position but keep y locked at bottom
            self.rect.x = int(self.x)
            # Ensure bottom stays locked at bottom of play screen
            self.rect.bottom = self.settings.screen_height
            self.y = float(self.rect.y)

        elif self.player_state == "dead":
            # Nothing: dead ships don't move
            pass
    
    def heal(self, amount: int):
        """Heal the ship by the specified amount, up to current_max_health."""
        self.player_health = min(self.current_max_health, self.player_health + amount)
    
    def trigger_powerup_flash(self, ptype: str, duration_ms: int = 900) -> None:
            """Flash a specific powerup count in the HUD (ptype is 'squadron'/'nanites'/'shockwave')."""
            now = pygame.time.get_ticks()
            if not hasattr(self, "powerup_flash_until_ms"):
                self.powerup_flash_until_ms = {}
            self.powerup_flash_until_ms[ptype] = now + duration_ms
    
    def trigger_hit_animation(self, duration_ms: int = 450) -> None:
        """Trigger hit animation sprite swap (matches HUD health flash duration)."""
        now = pygame.time.get_ticks()
        self.hit_animation_until_ms = now + duration_ms
        
    def draw(self):
        now = pygame.time.get_ticks()
        
        #Choose which image to display, based on state player is in:
        if self.player_state in ("between_lives", "respawning"):
            # During respawn, always use respawn image (hit animation doesn't interfere)
            image = self.respawn_image
        elif self.hit_animation_until_ms > now:
            # Show hit image if hit animation is active
            image = self.hit_image
        else:
            # Normal image
            image = self.image
        
        self.screen.blit(image, self.rect) #blit the sprite image to the screen.

        # Draw level up animation line if active
        if self.level_up_line_y != -1:
            pygame.draw.line(self.screen, (255, 255, 255),  # White color
                           (self.rect.left, self.level_up_line_y),  # Start point
                           (self.rect.right, self.level_up_line_y),  # End point
                           3)  # 3 pixel thickness


class Lifepod_Squadron(pygame.sprite.Sprite):
    """Escape pod for dead players - provides continued gameplay experience."""

    def __init__(self, settings, screen, player_id):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.player_id = player_id

        # Determine escape pod image based on player_id (fixed mapping)
        if player_id == 1:
            self.image_path = escapepod1_path  # Blue
            self.respawn_image_path = escapepod_respawn1_path
        elif player_id == 2:
            self.image_path = escapepod2_path  # Red
            self.respawn_image_path = escapepod_respawn2_path
        elif player_id == 3:
            self.image_path = escapepod3_path  # Cyan
            self.respawn_image_path = escapepod_respawn3_path
        elif player_id == 4:
            self.image_path = escapepod4_path  # Pink
            self.respawn_image_path = escapepod_respawn4_path
        else:
            # Default to blue if unknown
            self.image_path = escapepod1_path
            self.respawn_image_path = escapepod_respawn1_path

        # Load images
        self.normal_image = pygame.image.load(self.image_path).convert_alpha()
        self.respawn_image = pygame.image.load(self.respawn_image_path).convert_alpha()

        # Scale images (40x40 base size scaled by multiplayer_resizer)
        base_size = (40, 40)
        scaled_size = (int(base_size[0] * settings.multiplayer_resizer),
                      int(base_size[1] * settings.multiplayer_resizer))
        self.normal_image = pygame.transform.smoothscale(self.normal_image, scaled_size)
        self.respawn_image = pygame.transform.smoothscale(self.respawn_image, scaled_size)

        # Start with normal image
        self.image = self.normal_image
        self.rect = self.image.get_rect()

        # Position at visual midbottom of play screen, spaced by player_id
        # Spread lifepods across the bottom: P1=left, P2=right, P3=center-left, P4=center-right
        if player_id == 1:
            self.rect.centerx = settings.screen_width // 4  # Left quarter
        elif player_id == 2:
            self.rect.centerx = 3 * settings.screen_width // 4  # Right quarter
        elif player_id == 3:
            self.rect.centerx = settings.screen_width // 6  # Far left
        elif player_id == 4:
            self.rect.centerx = 5 * settings.screen_width // 6  # Far right
        else:
            self.rect.centerx = settings.screen_width // 2  # Center fallback

        self.rect.bottom = settings.screen_height

        # Movement
        self.speed = settings.base_ship_speed * 0.9  # 10% slower than base player ship speed

        # Respawn state
        self.state = "normal"  # normal, respawning
        self.respawn_start_time = 0
        self.respawn_duration = 5000  # 5 seconds

        # Control flags (will be set by external input)
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False
        self.firing = False
        self.next_fire_time = 0

        # Position tracking for smooth movement
        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)

    def update(self):
        """Update escape pod position and state."""
        current_time = pygame.time.get_ticks()

        if self.state == "normal":

            # Normal movement
            if self.moving_left and self.rect.left > 0:
                self.x -= self.speed
            if self.moving_right and self.rect.right < self.settings.screen_width:
                self.x += self.speed
            if self.moving_up and self.rect.top > 0:
                self.y -= self.speed
            if self.moving_down and self.rect.bottom < self.settings.screen_height:
                self.y += self.speed

            # Update rect
            self.rect.centerx = int(self.x)
            self.rect.centery = int(self.y)

        elif self.state == "respawning":
            # Move to bottom at speed 6
            if self.rect.bottom < self.settings.screen_height:
                self.y += 6
                self.rect.centery = int(self.y)

            # Check if respawn time is up
            if current_time - self.respawn_start_time >= self.respawn_duration:
                self.state = "normal"
                self.image = self.normal_image

    def start_respawn(self):
        """Start the respawn animation."""
        self.state = "respawning"
        self.respawn_start_time = pygame.time.get_ticks()
        self.image = self.respawn_image

        # Move to bottom position
        self.rect.bottom = self.settings.screen_height
        self.y = float(self.rect.centery)

    def draw(self):
        """Draw the escape pod."""
        self.screen.blit(self.image, self.rect)
