# bonus_wave.py
# Custom secret wave with special kitty enemies
# This module handles the bonus wave enemies and their behaviors

import pygame
import math
import random
from base_settings import resource_path

class BonusWaveEnemy(pygame.sprite.Sprite):
    """Base class for bonus wave enemies"""
    def __init__(self, settings, screen, enemy_type):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.enemy_type = enemy_type  # "loaf", "centurion", "emperor", "bluewhale", "ninja", "nyancat"
        self.damage_stage = 0
        
        # Load and scale image
        image_paths = {
            "loaf": resource_path("img/loafkitty.png"),
            "centurion": resource_path("img/centurionkitty.png"),
            "emperor": resource_path("img/emperorkitty.png"),
            "bluewhale": resource_path("img/bluewhalekitty.png"),
            "ninja": resource_path("img/ninjakitty_sideways.png"),
            "nyancat": resource_path("img/nyancat.png")
        }
        
        # Base sizes (will be scaled by multiplayer_resizer)
        base_sizes = {
            "loaf": (100, 150),
            "centurion": (100, 67),
            "emperor": (100, 150),
            "bluewhale": (200, 300),
            "ninja": (112, 75),
            "nyancat": (867, 200)
        }
        
        self.image = pygame.image.load(image_paths[enemy_type]).convert_alpha()
        base_size = base_sizes[enemy_type]
        # Scale based on multiplayer_resizer (same as player ships and regular aliens)
        resize = settings.multiplayer_resizer
        size = (round(base_size[0] * resize), round(base_size[1] * resize))
        self.image = pygame.transform.smoothscale(self.image, size)
        self.original_image = self.image.copy()  # For flipping
        self.rect = self.image.get_rect()
        
        # Ninjakitty has a custom hitbox that excludes bottom-right corner (right 24% × lower 34%)
        if enemy_type == "ninja":
            # Calculate excluded area: right 24% × lower 34%
            exclude_right = int(size[0] * 0.24)  # Right 24% of width
            exclude_bottom_start = int(size[1] * 0.66)  # Lower 34% starts at 66% from top
            # Create hitbox rect that excludes bottom-right corner
            # Hitbox covers: left 76% of width, and top 66% of height
            self.hitbox_rect = pygame.Rect(
                self.rect.left,  # Start at left
                self.rect.top,  # Start at top
                size[0] - exclude_right,  # Width minus excluded right portion
                exclude_bottom_start  # Height up to excluded bottom portion
            )
        # Nyancat has a custom hitbox that excludes bottom 12% and left 65%
        elif enemy_type == "nyancat":
            # Nyancat hitbox: excludes bottom 12% and left 65% when not flipped
            # When flipped, excludes bottom 12% and right 65%
            exclude_side = int(size[0] * 0.65)  # 65% of width
            exclude_bottom = int(size[1] * 0.12)  # Bottom 12% of height
            # Create base hitbox rect (will be positioned correctly during updates)
            self.hitbox_rect = pygame.Rect(
                0, 0,  # Position will be set in update
                size[0] - exclude_side,  # Width minus excluded side portion
                size[1] - exclude_bottom  # Height minus excluded bottom portion
            )
            # Store hitbox parameters for dynamic positioning
            self.hitbox_exclude_side = exclude_side
            self.hitbox_exclude_bottom = exclude_bottom
        else:
            self.hitbox_rect = None  # Use default rect for other enemies
        
        # Set max damage based on type
        max_hits = {"loaf": 6, "centurion": 3, "emperor": 12, "bluewhale": 21, "ninja": 5, "nyancat": 42}
        self.max_damage = max_hits[enemy_type]
        
        # Movement properties
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        
        # Firing properties
        if enemy_type == "emperor":
            # Emperorkitty fires every ~0.5 seconds
            self.min_fire_interval = 500
            self.max_fire_interval = 500
        elif enemy_type == "bluewhale":
            # Bluewhalekitty fires at lasertanker rate (120-121ms) for continuous stream
            self.min_fire_interval = 120
            self.max_fire_interval = 121
        elif enemy_type == "ninja":
            # Ninjakitty does not fire any bullets
            self.min_fire_interval = None
            self.max_fire_interval = None
        elif enemy_type == "nyancat":
            # Nyancat fires every 0.5-0.75 seconds
            self.min_fire_interval = 500
            self.max_fire_interval = 750
        else:
            # Loaf and centurion fire at level 3 alien rate
            self.min_fire_interval = settings.alien3_min_fire_interval
            self.max_fire_interval = settings.alien3_max_fire_interval
        self.next_fire_time = 0
        
        # Special properties
        self.moving_right = False  # For centurionkitty and ninjakitty image flipping
        self.target_player = None  # For tracking enemies
        
        # Spawn timing
        self.spawn_time = pygame.time.get_ticks()
        
    def spawn_pos(self, x, y):
        """Set spawn position"""
        self.x = float(x)
        self.y = float(y)
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        # Update hitbox position for ninjakitty
        if self.hitbox_rect is not None:
            self.hitbox_rect.x = self.rect.x
            self.hitbox_rect.y = self.rect.y
        
    def ready_to_fire(self, current_time_ms: int, alien_bullets_group=None) -> bool:
        """Check if ready to fire"""
        # Prevent firing if enemy has passed the bottom of the screen
        if self.rect.bottom > self.settings.screen_height:
            return False
        # Bluewhalekitty fires at 25% on screen, others at 33%
        if self.enemy_type == "bluewhale":
            if self.rect.top <= -self.rect.height * 0.75:  # 25% on screen = top at -75% of height
                return False
        else:
            if self.rect.top <= -self.rect.height * 0.33:  # 33% on screen for others
                return False
        
        # Emperorkitty: check bullet cap - stop firing if at cap of 3
        if self.enemy_type == "emperor" and alien_bullets_group is not None:
            bullet_count = 0
            for b in alien_bullets_group:
                if hasattr(b, 'owner_ref') and b.owner_ref == self:
                    bullet_count += 1
            if bullet_count >= 3:  # Cap of 3 bullets
                return False  # Don't fire until bullets are off screen
        
        # Check if this enemy type fires bullets (some like ninjakitty don't fire)
        if self.min_fire_interval is None or self.max_fire_interval is None:
            return False

        if current_time_ms >= self.next_fire_time:
            interval = random.randint(self.min_fire_interval, self.max_fire_interval)
            self.next_fire_time = current_time_ms + interval
            return True
        return False
    
    def take_hit(self):
        """Take damage and return True if destroyed"""
        self.damage_stage += 1
        return self.damage_stage >= self.max_damage
    
    def update(self, time_elapsed_ms, speed_scale, player_group):
        """Update enemy position and behavior"""
        # Movement depends on type
        if self.enemy_type == "loaf":
            # Slow downward movement
            base_speed = 0.3 * speed_scale
            self.y += base_speed
            self.rect.y = int(self.y)
            
        elif self.enemy_type == "centurion":
            # Level 3 alien movement pattern
            if not hasattr(self, 'drift_timer'):
                self.drift_timer = 0
                self.drift_change_interval = random.randint(60, 400)
                self.drift_speed = 2.3 * speed_scale
                self.vx, self.vy = self._get_random_vector()
            
            self.drift_timer += 1
            if self.drift_timer >= self.drift_change_interval:
                self.vx, self.vy = self._get_random_vector()
                self.drift_change_interval = random.randint(40, 85)
                self.drift_timer = 0
            
            self.x += self.vx
            self.y += self.vy
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
            
            # Flip image based on direction
            if self.vx > 0 and not self.moving_right:
                self.image = pygame.transform.flip(self.original_image, True, False)
                self.moving_right = True
            elif self.vx < 0 and self.moving_right:
                self.image = self.original_image.copy()
                self.moving_right = False
            
            # Bounce off edges
            if self.rect.left < 0:
                self.rect.left = 0
                self.x = float(self.rect.x)
                self.vx = abs(self.vx)
                self.drift_timer = 0
            if self.rect.right > self.settings.screen_width:
                self.rect.right = self.settings.screen_width
                self.x = float(self.rect.x)
                self.vx = -abs(self.vx)
                self.drift_timer = 0
                
        elif self.enemy_type == "ninja":
            # Simplified ninjakitty movement - only changes direction at screen edges
            if not hasattr(self, 'vx'):
                # Initialize movement - start moving right with some downward drift
                self.vx = 4.0 * speed_scale  # Constant horizontal speed
                self.vy = 0.5 * speed_scale  # Slight downward drift

            self.x += self.vx
            self.y += self.vy
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

            # Update hitbox position
            if self.hitbox_rect is not None:
                self.hitbox_rect.x = self.rect.x
                self.hitbox_rect.y = self.rect.y

            # Flip sprite based on direction and bounce off edges
            if self.rect.left < 0:
                self.rect.left = 0
                self.x = float(self.rect.x)
                self.vx = abs(self.vx)  # Move right
                self.moving_right = True
                self.image = pygame.transform.flip(self.original_image, True, False)
            elif self.rect.right > self.settings.screen_width:
                self.rect.right = self.settings.screen_width
                self.x = float(self.rect.x)
                self.vx = -abs(self.vx)  # Move left
                self.moving_right = False
                self.image = self.original_image.copy()
                
        elif self.enemy_type in ("emperor", "bluewhale"):
            # Cruiser-like tracking movement - align centerx with target centerx
            if self.target_player and self.target_player.alive():
                target_centerx = self.target_player.rect.centerx
                self_centerx = self.rect.centerx

                if self_centerx < target_centerx:
                    # Move right to align centers
                    list_speed = (0.25 if self.enemy_type == "emperor" else 0.15) * speed_scale
                    self.x += list_speed
                elif self_centerx > target_centerx:
                    # Move left to align centers
                    list_speed = (0.25 if self.enemy_type == "emperor" else 0.15) * speed_scale
                    self.x -= list_speed
            
            # Downward movement
            advance_speed = (0.5 if self.enemy_type == "emperor" else 0.25) * speed_scale
            self.y += advance_speed
            self.rect.y = int(self.y)
            self.rect.x = int(self.x)

        elif self.enemy_type == "nyancat":
            # Nyancat: moves left to right, gentle vertical zigzag, exits and re-enters flipped
            if not hasattr(self, 'direction'):  # Initialize movement
                self.direction = 1  # 1 = right, -1 = left
                self.vertical_phase = 0
                self.exit_time = 0
                self.speed = 1.275 * speed_scale  # Slow horizontal movement (15% slower)
                # Start with normal (unflipped) sprite
                self.image = self.original_image.copy()

            current_time = pygame.time.get_ticks()

            # If off-screen and waiting, check if ready to re-enter
            if self.exit_time > 0:
                if current_time - self.exit_time >= 3000:  # 3 second delay
                    self.exit_time = 0
                    # Flip direction
                    old_direction = self.direction
                    self.direction *= -1
                    # Flip sprite when direction changes
                    if old_direction != self.direction:
                        self.image = pygame.transform.flip(self.image, True, False)
                    # Set starting position based on new direction
                    if self.direction == 1:  # Going right, start from left
                        self.x = -self.rect.width
                    else:  # Going left, start from right
                        self.x = self.settings.screen_width
                else:
                    return  # Still waiting, don't move

            # Vertical zigzag movement (gentle sine wave)
            vertical_speed = 0.68 * speed_scale  # 15% slower
            self.vertical_phase += 0.05
            vertical_offset = math.sin(self.vertical_phase) * 30  # 30 pixel amplitude

            # Horizontal movement
            self.x += self.speed * self.direction
            self.y += vertical_offset * 0.1  # Small vertical movement

            # Keep within reasonable vertical bounds
            if self.y < 50:
                self.y = 50
                self.vertical_phase = 0
            elif self.y > 200:
                self.y = 200
                self.vertical_phase = math.pi

            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

            # Update hitbox position (flips horizontally with sprite)
            if self.hitbox_rect is not None:
                if self.direction == 1:  # Moving right (normal orientation)
                    self.hitbox_rect.x = self.rect.x + self.hitbox_exclude_side
                else:  # Moving left (flipped orientation)
                    self.hitbox_rect.x = self.rect.x
                self.hitbox_rect.y = self.rect.y

            # Check if reached edge and should exit
            if self.direction == 1 and self.rect.left > self.settings.screen_width:
                # Exited right side, prepare to come back from left
                self.exit_time = current_time
            elif self.direction == -1 and self.rect.right < 0:
                # Exited left side, prepare to come back from right
                self.exit_time = current_time
    
    def _get_random_vector(self):
        """Get random movement vector for centurionkitty (similar to level 3 alien)"""
        while True:
            angle = random.uniform(0, 2 * math.pi)
            deg = math.degrees(angle) % 180
            if 22.5 <= deg <= 157.5:
                continue
            vx = math.cos(angle) * self.drift_speed
            vy = (abs(math.sin(angle)) * self.drift_speed) - 0.075
            return vx, vy
    
    def set_target_player(self, player):
        """Set target player for tracking"""
        self.target_player = player
    
    def get_collision_rect(self):
        """Get the rect to use for collision detection (uses hitbox_rect if available)"""
        if self.hitbox_rect is not None:
            return self.hitbox_rect
        return self.rect
    
    def draw(self):
        """Draw the enemy"""
        self.screen.blit(self.image, self.rect)


def create_firework_bullets(settings, screen, center_x, center_y, colors):
    """Create star pattern bullets radiating from center. Returns list of bullet sprites.
    colors: list of colors for each bullet (8 bullets total)"""
    bullets = []
    bullet_speed = settings.bullet_speed
    bullet_length = 40
    bullet_width = 2
    
    # 8 directions evenly spaced (45 degrees apart)
    for i in range(8):
        angle = (i * 45) * (math.pi / 180)  # Convert to radians
        color = colors[i % len(colors)]
        
        # Create a bullet sprite (non-colliding visual only)
        bullet = pygame.sprite.Sprite()
        bullet.image = pygame.Surface((bullet_width, bullet_length), pygame.SRCALPHA)
        bullet.image.fill(color)
        bullet.rect = bullet.image.get_rect()
        bullet.rect.centerx = center_x
        bullet.rect.centery = center_y
        
        # Calculate velocity
        bullet.vx = math.cos(angle) * bullet_speed
        bullet.vy = math.sin(angle) * bullet_speed
        bullet.x = float(center_x)
        bullet.y = float(center_y)
        bullet.lifetime = 2000  # 2 seconds before disappearing
        
        bullets.append(bullet)
    
    return bullets


class BonusWaveFirework(pygame.sprite.Sprite):
    """Non-colliding visual bullets for firework effects"""
    def __init__(self, settings, screen, center_x, center_y, color, angle):
        super().__init__()
        self.settings = settings
        self.screen = screen
        self.color = color
        
        bullet_length = 40
        bullet_width = 2
        self.image = pygame.Surface((bullet_width, bullet_length), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = center_x
        self.rect.centery = center_y
        
        bullet_speed = settings.bullet_speed
        self.vx = math.cos(angle) * bullet_speed
        self.vy = math.sin(angle) * bullet_speed
        self.x = float(center_x)
        self.y = float(center_y)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 2000  # 2 seconds
        
    def update(self):
        """Update firework bullet position"""
        self.x += self.vx
        self.y += self.vy
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        # Kill if lifetime expired or off screen
        now = pygame.time.get_ticks()
        if (now - self.spawn_time >= self.lifetime or 
            self.rect.bottom < 0 or self.rect.top > self.settings.screen_height_total or
            self.rect.right < 0 or self.rect.left > self.settings.screen_width):
            self.kill()
    
    def draw(self):
        """Draw the firework bullet"""
        self.screen.blit(self.image, self.rect)

