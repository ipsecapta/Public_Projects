#!/usr/bin/env python3
#
# Project: Final Project
#
# Files needed by this file: 
#       bullet.py (this file)
#       Visintainer_A_AlienGame.py (main file)
#       base_settings.py 
#      
# Author: Anthony Visintainer
# Date: 8 December 2025
# 
# This module contains the code to determine bullet logic, and assign different features to different types of bullet.
#
# Note to self: for universal bullet settings (speed, colors, width, height, etc) see base_settings.py.
import math
import random
import pygame

class Bullet(pygame.sprite.Sprite): 
    """The Bullet Sprite. I chose to create enough parameters to have just one class, 
        that can be passed different attributes to create different bullets."""
    def __init__(self, settings, screen, 
                 x, y, direction, 
                 owner_type, owner_level=1, owner_ref=None, squadron_ref=None, firework = None):
        """BULLET PARAMETER DESCRIPTIONS:
        *settings*: movement speed, dimensions, color, etc will be called as attributes of this parameter, from variables in base_settings.py
        *screen*: the display surface the bullets will be mapped onto
        *x,y*: bullet starting position.
        *direction*: whether the bullet moves up (-1) or down (+1)
        *owner_type*: who owns the bullet - player or some class of alien?
        *owner_level*: allow for multiple levels of aliens, and allow player bullets to level up.
        *owner_ref*: reference to the player/alien that fired the bullet. None means it's no set to anyone. used for bullet # limits, tracking points, and owner-based attributes"""

        super().__init__() #call the super class - pygame sprite - and init for the bullet subclass. give the function variables to --->
                            #--->pass the parameters to.
        self.settings = settings
        self.screen = screen
        self.owner_type = owner_type
        self.owner_ref = owner_ref
        self.owner_level = owner_level
        self.squadron_ref = squadron_ref  # Track if bullet was fired by a squadron
        self.firework = firework  # Track if bullet is a firework
        self.direction = direction
        
        #Use if statements to distinguish size differences in types of bullets depending on who fired them:
        if owner_type == "boss":
            width = settings.boss_bullet_width
            height = settings.boss_bullet_height
            self.color = settings.boss_bullet_color
            self.speed = settings.boss_bullet_speed

        #use if and elif statements to distinguish bullet colors and speeds:
        elif owner_type == "player":
            # Check if this is a lifepod bullet (lifepods have 'state' attribute) or squadron bullet (has squadron_ref)
            if owner_ref and hasattr(owner_ref, 'state'):
                # Lifepod bullets: 1/2 size of normal player bullets
                width = settings.bullet_width // 2  # 2 pixels wide
                height = settings.bullet_height // 2  # 8 pixels tall
            elif squadron_ref is not None:
                # Squadron bullets: 1/2 size of normal player bullets
                width = settings.bullet_width // 2  # 2 pixels wide
                height = settings.bullet_height // 2  # 8 pixels tall
            elif firework is not None:
                # Firework bullets: celebratory firework bullets
                width = settings.player_firework_width  # 4 pixels wide
                height = settings.player_firework_height  # 4 pixels tall
                color_choice = random.randint(0, len(settings.player_firework_colors) - 1)
                self.color = settings.player_firework_colors[color_choice]
                self.speed = settings.player_firework_speed
            else:
                # Normal player bullets
                width = settings.bullet_width  # 4 pixels wide
                height = settings.bullet_height  # 16 pixels tall
            
            # Firework bullets should not inherit normal/level-11 bullet visuals/speeds
            if firework is None:
                if owner_level == 11: #bullets will look special and fly faster if players are level 11.
                    self.speed = settings.lvl11_bullet_speed
                    self.color = settings.lvl11_bullet_color
                else: # if not level 11, bullets will look normal.
                    self.color = settings.player_bullet_color
                    self.speed = settings.bullet_speed
            
        elif owner_type == "alien" and owner_level == 5: # destroyer bullets are slightly thicker, slower, and whitish purple
            width = settings.destroyer_bullet_width
            height = settings.destroyer_bullet_height
            self.color = settings.destroyerandcruiser_bullet_color
            self.speed = settings.alien_bullet_speed - 0.1
        elif owner_type == "alien" and owner_level == 6: # cruiser bullets are much thicker and much slower
            width = settings.cruiser_bullet_width
            height = settings.cruiser_bullet_height
            self.color = settings.destroyerandcruiser_bullet_color
            self.speed = settings.alien_bullet_speed - 0.25
        elif owner_type == "alien" and owner_level == 7: # lazer tankers fire a stream of, thin, red, fast laser. dangerous.
            width = settings.laztanker_bullet_width
            height = settings.laztanker_bullet_height
            self.color = settings.laztanker_bullet_color
            self.speed = settings.alien_bullet_speed + 0.25
            #TODO: drop interceptors here with firing the double-tiny bullet, 4 pixels up and 4 pixels down from their center-(frontside) coordinate
        elif owner_type == "alien":
            width = settings.alien_bullet_width
            height = settings.alien_bullet_height
            self.color = settings.alien_bullet_color
            self.speed = settings.alien_bullet_speed
        elif owner_type == "kitty":
            # Bonus wave enemy bullets
            kitty_type_map = {
                10: "loaf",      # Loafkitty
                11: "centurion", # Centurionkitty
                12: "emperor",  # Emperorkitty
                13: "bluewhale", # Bluewhalekitty
                14: "ninja"     # Ninjakitty (if it fires)
            }
            kitty_type = kitty_type_map.get(owner_level, "loaf")
            
            # Set size based on kitty type
            if kitty_type == "loaf":
                width = settings.loafkitty_bullet_width
                height = settings.loafkitty_bullet_height
            elif kitty_type == "bluewhale":
                width = settings.bluewhalekitty_bullet_width
                height = settings.bluewhalekitty_bullet_height
            else:  # centurion, emperor, ninja
                width = settings.centurionkitty_bullet_width
                height = settings.centurionkitty_bullet_height
            
            # Set speed
            if kitty_type == "loaf":
                self.speed = settings.loafkitty_bullet_speed
            elif kitty_type == "bluewhale":
                self.speed = settings.bluewhalekitty_bullet_speed
            else:
                self.speed = settings.centurionkitty_bullet_speed
            
            # Set initial color and blink colors
            if kitty_type == "loaf":
                self.color = settings.loafkitty_bullet_color
                self.blink_colors = [settings.loafkitty_bullet_color, (255, 255, 255)]  # Yellow and white
                self.blink_rate_ms = settings.loafkitty_bullet_blink_rate_ms
            elif kitty_type == "centurion":
                self.color = settings.centurionkitty_bullet_color
                self.blink_colors = [(255, 255, 255), settings.centurionkitty_bullet_color]  # White and red
                self.blink_rate_ms = settings.centurionkitty_bullet_blink_rate_ms
            elif kitty_type == "emperor":
                self.color = settings.emperorkitty_bullet_color
                self.blink_colors = [(255, 255, 255), settings.emperorkitty_bullet_color]  # White and purple
                self.blink_rate_ms = settings.emperorkitty_bullet_blink_rate_ms
            elif kitty_type == "bluewhale":
                self.color = settings.bluewhalekitty_bullet_colors[0]  # First blue color
                self.blink_colors = settings.bluewhalekitty_bullet_colors  # Two blue colors
                self.blink_rate_ms = settings.bluewhalekitty_bullet_blink_rate_ms
            
            # Initialize blinking state
            self.blink_index = 0
            self.last_blink_change = pygame.time.get_ticks()
            self.original_color = self.color

        #returning to attributes of the bullet class, we make good on width and height in those if statements.
        self.rect = pygame.Rect(0, 0, width, height) #says: create the bullet rect in the top corner, and --->
                                                    #--->match whatever width and height parameters are set above.
        self.rect.centerx = x #the bullet rects will be placed at the x and y center of their rect.
        self.rect.centery = y

        #change coordinate to float, for smooth movement:
        self.y = (float(self.rect.y))

    def update(self): #an update function, to allow the class to move as part of the game loop.
        self.y += self.speed * self.direction #take the direction (which will be either 1 or -1) and multiply by speed for bullet mvmt\

        self.rect.y= int(self.y) #sync the bullet's rect to the new location calculated in the prev line
        
        # Handle blinking for kitty bullets (and any other bullets with blink_colors)
        if hasattr(self, 'blink_colors') and self.blink_colors:
            current_time = pygame.time.get_ticks()
            blink_rate = getattr(self, 'blink_rate_ms', 40)
            if current_time - self.last_blink_change >= blink_rate:
                self.blink_index = (self.blink_index + 1) % len(self.blink_colors)
                self.color = self.blink_colors[self.blink_index]
                self.last_blink_change = current_time
        
        #bullets disappear when they leave the screen:
        if self.rect.bottom < 0 or self.rect.top > self.settings.play_height:
            self.kill()
        
    def draw(self): # a draw function, to place the bullet visibly on screen
        pygame.draw.rect(self.screen, self.color, self.rect)
        """>>>EVENTUALLY REPLACE WITH PNG SPRITES THAT GET BLITTED ON TO SCREEN"""


class NyancatBullet(pygame.sprite.Sprite):
    """Special rainbow-flashing square bullet for nyancat"""
    def __init__(self, settings, screen, x, y, direction, owner_ref=None):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.owner_ref = owner_ref
        self.direction = direction

        # Create square bullet (same width/height)
        size = 8  # 8x8 pixel square
        self.rect = pygame.Rect(0, 0, size, size)
        self.rect.centerx = x
        self.rect.centery = y

        # Rainbow colors cycle every millisecond
        self.rainbow_colors = [
            (255, 0, 0),    # Red
            (255, 165, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (75, 0, 130),   # Indigo
            (255, 0, 255)   # Violet/Purple
        ]
        self.color_index = 0
        self.last_color_change = pygame.time.get_ticks()
        self.color = self.rainbow_colors[0]

        # Slow descent
        self.speed = 1.0  # Very slow downward movement
        self.y = float(self.rect.y)

    def update(self):
        """Update bullet position and color"""
        # Update position (slow descent)
        self.y += self.speed * self.direction
        self.rect.y = int(self.y)

        # Cycle through rainbow colors every millisecond
        current_time = pygame.time.get_ticks()
        if current_time - self.last_color_change >= 1:  # 1ms = very fast cycling
            self.color_index = (self.color_index + 1) % len(self.rainbow_colors)
            self.color = self.rainbow_colors[self.color_index]
            self.last_color_change = current_time

        # Remove when off screen
        if self.rect.bottom < 0 or self.rect.top > self.settings.play_height:
            self.kill()

    def draw(self):
        """Draw the rainbow square bullet"""
        pygame.draw.rect(self.screen, self.color, self.rect)


class VictoryFireworkSpark(pygame.sprite.Sprite):
    """Cosmetic victory firework spark: moves outward, then fades out near the end of its lifetime."""
    def __init__(self, settings, screen, x, y, color_rgb, angle_rad, size: int = 4, speed: float | None = None,
                 lifetime_ms: int | None = None, fade_ms: int | None = None):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.color_rgb = tuple(color_rgb)
        self.size = int(size)
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = (int(x), int(y))
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

        self.speed = float(speed if speed is not None else getattr(settings, "player_firework_bloom_speed", 9))
        self.vx = math.cos(angle_rad) * self.speed
        self.vy = math.sin(angle_rad) * self.speed

        self.spawn_time = pygame.time.get_ticks()
        if lifetime_ms is None:
            min_ms = int(getattr(settings, "victory_firework_spark_lifetime_min_ms", 2000))
            max_ms = int(getattr(settings, "victory_firework_spark_lifetime_max_ms", 3000))
            lifetime_ms = random.randint(min_ms, max_ms)
        self.lifetime_ms = int(lifetime_ms)

        if fade_ms is None:
            fade_ms = int(getattr(settings, "victory_firework_spark_fade_ms", 600))
        self.fade_ms = int(max(1, fade_ms))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        now = pygame.time.get_ticks()
        if now - self.spawn_time >= self.lifetime_ms:
            self.kill()

    def draw(self):
        now = pygame.time.get_ticks()
        age = now - self.spawn_time
        remaining = self.lifetime_ms - age

        alpha = 255
        if remaining <= self.fade_ms:
            # fade from 255 -> 0 during the last fade_ms
            alpha = int(max(0, min(255, 255 * (remaining / float(self.fade_ms)))))

        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        surf.fill((self.color_rgb[0], self.color_rgb[1], self.color_rgb[2], alpha))
        self.screen.blit(surf, self.rect.topleft)


class VictoryFireworkShell(pygame.sprite.Sprite):
    """Cosmetic victory firework shell (player): blinks and explodes into 8-way sparks before leaving the top."""
    def __init__(self, settings, screen, x, y, fireworks_group, owner_ref=None, squadron_ref=None,
                 shell_size: int = 6, spark_size: int = 4):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.owner_ref = owner_ref
        self.squadron_ref = squadron_ref
        self.fireworks_group = fireworks_group

        self.shell_size = int(shell_size)
        self.spark_size = int(spark_size)
        self.rect = pygame.Rect(0, 0, self.shell_size, self.shell_size)
        self.rect.centerx = int(x)
        self.rect.centery = int(y)
        self.y = float(self.rect.y)

        self.base_speed = float(getattr(settings, "player_firework_speed", 5))
        self.current_speed = self.base_speed

        # Compute target distance so explosion happens at least 100px before the shell exits the top.
        start_top = int(self.rect.top)
        max_dist = max(100, start_top - 100)
        self.target_dist = random.randint(100, max_dist) if max_dist > 100 else 100
        self.start_top = float(start_top)
        # How far (in px) before detonation we begin slowing down
        self.decel_zone = float(getattr(settings, "victory_firework_shell_decel_zone_px", 55.0))

        # Alpha blinking (implemented as visible/invisible toggling)
        self.visible = True
        self.blink_rate_ms = int(getattr(settings, "victory_firework_shell_blink_rate_ms", 40))
        self.last_blink_change = pygame.time.get_ticks()

        self.color_rgb = (255, 255, 255)

    def update(self):
        # Blink toggle
        now = pygame.time.get_ticks()
        if now - self.last_blink_change >= self.blink_rate_ms:
            self.visible = not self.visible
            self.last_blink_change = now

        traveled = self.start_top - float(self.rect.top)
        remaining = self.target_dist - traveled

        # Decelerate right before target distance expires
        if remaining <= self.decel_zone:
            # More pronounced slowdown: ease-out curve that gets very slow near detonation
            t = max(0.0, min(1.0, remaining / self.decel_zone))
            exponent = float(getattr(self.settings, "victory_firework_shell_decel_exponent", 2.0))
            min_factor = float(getattr(self.settings, "victory_firework_shell_min_speed_factor", 0.05))
            factor = max(min_factor, t ** exponent)
            self.current_speed = self.base_speed * factor
        else:
            self.current_speed = self.base_speed

        # Move up
        self.y -= self.current_speed
        self.rect.y = int(self.y)

        # Explode on reaching target travel distance
        traveled = self.start_top - float(self.rect.top)
        if traveled >= self.target_dist:
            self._explode()
            self.kill()
            return

        # Safety: remove if offscreen
        if self.rect.bottom < 0:
            self.kill()

    def _explode(self):
        # One random bloom color per explosion
        colors = getattr(self.settings, "player_firework_colors", [(255, 255, 255)])
        bloom_color = random.choice(list(colors)) if colors else (255, 255, 255)

        difficulty = getattr(self.settings, "difficulty_mode", "normal").lower()
        if difficulty == "hard":
            sets = int(getattr(self.settings, "victory_firework_spark_sets_hard", 3))
            sparks_per_set = int(getattr(self.settings, "victory_firework_sparks_per_set_hard", 16))
        else:
            sets = int(getattr(self.settings, "victory_firework_spark_sets_normal", 1))
            sparks_per_set = int(getattr(self.settings, "victory_firework_sparks_per_set_normal", 8))
        sets = max(1, sets)
        sparks_per_set = max(1, sparks_per_set)

        cx, cy = self.rect.centerx, self.rect.centery
        if sets <= 1:
            # Single set immediately
            step = (2.0 * math.pi) / float(sparks_per_set)
            for i in range(sparks_per_set):
                angle = i * step
                base_speed = float(getattr(self.settings, "player_firework_bloom_speed", 9))
                slowdown = float(getattr(self.settings, "victory_firework_spark_speed_slowdown", 1.0))
                spark_speed = max(0.0, base_speed - slowdown)
                spark = VictoryFireworkSpark(
                    self.settings, self.screen,
                    cx, cy,
                    bloom_color,
                    angle_rad=angle,
                    size=self.spark_size,
                    speed=spark_speed,
                    lifetime_ms=None,
                    fade_ms=None
                )
                self.fireworks_group.add(spark)
            return

        # Multiple sets: emit rings spaced apart in time (e.g., 100ms)
        delay_ms = int(getattr(self.settings, "victory_firework_spark_set_delay_ms", 100))
        burst = VictoryFireworkBurst(
            settings=self.settings,
            screen=self.screen,
            x=cx,
            y=cy,
            fireworks_group=self.fireworks_group,
            color_rgb=bloom_color,
            spark_size=self.spark_size,
            sets=sets,
            set_delay_ms=delay_ms,
            sparks_per_set=sparks_per_set,
        )
        self.fireworks_group.add(burst)

    def draw(self):
        if not self.visible:
            return
        surf = pygame.Surface((self.shell_size, self.shell_size), pygame.SRCALPHA)
        surf.fill((self.color_rgb[0], self.color_rgb[1], self.color_rgb[2], 255))
        self.screen.blit(surf, self.rect.topleft)


class VictoryFireworkShellSmall(VictoryFireworkShell):
    """Smaller cosmetic victory firework shell for squadrons/lifepods (3x3 shell, 2x2 sparks)."""
    def __init__(self, settings, screen, x, y, fireworks_group, owner_ref=None, squadron_ref=None):
        super().__init__(
            settings, screen, x, y, fireworks_group,
            owner_ref=owner_ref, squadron_ref=squadron_ref,
            shell_size=3, spark_size=2
        )


class VictoryFireworkBurst(pygame.sprite.Sprite):
    """Spawns multiple radial spark sets spaced out in time (used for multi-bloom difficulty effects)."""
    def __init__(self, settings, screen, x, y, fireworks_group, color_rgb, spark_size: int, sets: int, set_delay_ms: int, sparks_per_set: int = 8):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.fireworks_group = fireworks_group
        self.color_rgb = tuple(color_rgb)
        self.spark_size = int(spark_size)
        self.sets_total = max(1, int(sets))
        self.set_delay_ms = max(0, int(set_delay_ms))
        self.sparks_per_set = max(1, int(sparks_per_set))
        self.cx = int(x)
        self.cy = int(y)

        self.spawned_sets = 0
        self.next_set_time = pygame.time.get_ticks()  # spawn first set immediately

    def _spawn_one_set(self):
        step = (2.0 * math.pi) / float(self.sparks_per_set)
        for i in range(self.sparks_per_set):
            angle = i * step
            base_speed = float(getattr(self.settings, "player_firework_bloom_speed", 9))
            slowdown = float(getattr(self.settings, "victory_firework_spark_speed_slowdown", 1.0))
            spark_speed = max(0.0, base_speed - slowdown)
            spark = VictoryFireworkSpark(
                self.settings, self.screen,
                self.cx, self.cy,
                self.color_rgb,
                angle_rad=angle,
                size=self.spark_size,
                speed=spark_speed,
                lifetime_ms=None,
                fade_ms=None
            )
            self.fireworks_group.add(spark)

    def update(self):
        now = pygame.time.get_ticks()
        if self.spawned_sets >= self.sets_total:
            self.kill()
            return

        if now >= self.next_set_time:
            self._spawn_one_set()
            self.spawned_sets += 1
            self.next_set_time = now + self.set_delay_ms

    def draw(self):
        # Nothing visible for the controller sprite itself
        return