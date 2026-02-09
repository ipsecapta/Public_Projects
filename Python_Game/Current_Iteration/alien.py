#alien.py

import pygame
import math #I decided I wanted the three different levels of aliens to have different movement patterns, so imported math to calculate zigzags, etc.
import random #since aliens at level 3 need a random movement pattern (though always forward), I imported random.

#INTERCEPTOR_PATH = "img/interceptor_dmg0.png"




class Alien(pygame.sprite.Sprite): #Create a class for aliens level 1-3
    def __init__(self, settings, screen, level=1):
        """CLASS PARAMETER DESCRIPTION:
        SETTINGS: import settings for motion speed, etc from base_settings.py
        SCREEN: display surface the sprite will be drawn on
        LEVEL: For aliens at different levels to have different motion & firing patterns"""

        super().__init__() #run the super init to get attributes from sprite class; then assign Alien class attribs.
        self.settings = settings
        self.screen = screen
        self.level = level #assign the input received for level parameter to a self.level attribute.
        #use if statements to CHOOSE THE SPRITE IMAGE and speed based on alien level
        if level == 1:
            self.speed = settings.alien1_strafe_speed #calling up the alien(x)_speed variables from base_settings, which
                                                  #main file will already have importedand assigned to "settings".
            self.spritesize = self.settings.alien1_spritesize  #set the size of the sprite as a tuple, for multiple uses later
        elif level == 2: 
            self.speed = settings.alien2_speed
            self.spritesize = self.settings.alien2_spritesize
        elif level == 3:
            self.speed = settings.alien3_speed
            self.spritesize = self.settings.alien3_spritesize
        elif level == 4:
            self.speed = settings.alien4_speed
            self.spritesize = self.settings.alien4_spritesize
        elif level == 5: #destroyers are level 5
            self.speed = settings.destroyer_speed
            self.spritesize = self.settings.destroyer_spritesize
        elif level == 6: #cruisers are level 6
            self.speed = settings.cruiser_speed
            self.spritesize = self.settings.cruiser_spritesize
        elif level == 7: #laser tankers are level 7
            self.speed = settings.laztanker_speed
            self.spritesize = self.settings.laztanker_spritesize
        

        #elif level == 30:
           # img_path = INTERCEPTOR_PATH
           # self.spritesize = (round(60*self.settings.multiplayer_resizer), round(40*self.settings.multiplayer_resizer))
       
        #LINK THE SPRITE IMAGE, using preloaded Surfaces from settings (already scaled).
        base_image = getattr(self.settings, "alien_images", {}).get(level)
        if base_image is None:
            # Fallback if settings.load_images() was not called for some reason.
            path = getattr(self.settings, "alien_sprite_paths", {}).get(level)
            if path:
                base_image = pygame.image.load(path).convert_alpha()
                base_image = pygame.transform.smoothscale(base_image, self.spritesize)
        if base_image is None:
            base_image = pygame.Surface(self.spritesize, pygame.SRCALPHA)

        self.image = base_image.copy()
        self.rect = self.image.get_rect() # get rect of sprite
        self.x = float(self.rect.x) # convert coordinates to float for smooth movement.
        self.y = float(self.rect.y)
        self.warping_in = False
        self.warp_target_y = None
        self.warp_entry_speed = None
        

        #init DIFFERENT TYPES OF MOVEMENT depending on level:
       
        if self.level ==2: # level 2 aliens, Stealth Fighters, to zigzag down the screen independently of each other. 
          
             self.zig_amplitude = random.randint(20,65)            
             self.zig_frequency = 0.06 #amplitude and frequency to use for a sine wave function - I'm slightly hazy on the math here.
             self.zig_phase = random.random() * 2 * math.pi
             self.base_x = 0.0 #0.0 is a placeholder - the real value wil be set below in alien_spawn_pos()
             
        if self.level == 3: #level 3 aliens will have random movement, changing direction every random
            self.drift_speed = self.speed + 0.4
            self.drift_change_interval = random.randint(60, 400) #ships will change direction erratically, but within certain limits.
            self.drift_timer = 0
            self.vx, self.vy = self._alien3_vector_changer() #helper function to determine direction changes for lvl 3 aliens
    
        #init different RATES OF FIRE, and MAX DAMAGE, INITIAL DAMAGE for different levels of alien:
        if self.level ==1:
             self.min_fire_interval = settings.alien1_min_fire_interval
             self.max_fire_interval = settings.alien1_max_fire_interval
             now = pygame.time.get_ticks()
             self.next_fire_time = now + random.randint(10, self.max_fire_interval)
        elif self.level ==2:
             self.min_fire_interval = settings.alien2_min_fire_interval
             self.max_fire_interval = settings.alien2_max_fire_interval
             self.next_fire_time = 0 #allow first firing  fire as soon as able
        elif self.level ==3:
             self.min_fire_interval = settings.alien3_min_fire_interval
             self.max_fire_interval = settings.alien3_max_fire_interval
             self.next_fire_time = 0
        #level 4 aliens need no elif, since ready_to_fire() precludes them from ever firing.
        elif self.level == 5: #destroyers
             self.min_fire_interval = settings.destroyer_min_fire_interval
             self.max_fire_interval = settings.destroyer_max_fire_interval
             self.next_fire_time = 0
             self.damage_stage = 0 #set damage stage to 0
             self.max_damage = len(self.settings.destroyer_hitframes)
        elif self.level == 6: #cruisers 
             self.min_fire_interval = settings.cruiser_min_fire_interval
             self.max_fire_interval = settings.cruiser_max_fire_interval
             self.next_fire_time = 0
             self.damage_stage = 0 #set damage stage to 0
             self.max_damage = len(self.settings.cruiser_hitframes)
             # Wing firing timer (independent of main gun)
             now = pygame.time.get_ticks()
             self.next_wing_fire_time = now + random.randint(settings.cruiser_wing_min_fire_interval, settings.cruiser_wing_max_fire_interval)
             self.next_wing_second_shot_time = None  # Timer for second wing shot (1 second after first)
        elif self.level == 7: #laser tankers
             self.min_fire_interval = settings.laztanker_min_fire_interval
             self.max_fire_interval = settings.laztanker_max_fire_interval
             self.next_fire_time = 0
             self.max_damage = len(self.settings.laztanker_hitframes)
             self.damage_stage = 0 #set damage stage to 0
        # elif self.level == 8: #gunships
        #      self.min_fire_interval = settings.gunship_min_fire_interval
        #      self.max_fire_interval = settings.gunship_max_fire_interval
        #      self.next_fire_time = 0
        #      self.max_damage = len(self.settings.gunship_hitframes)
        #      self.damage_stage = 0 #set damage stage to 0

        #helper function for level 3 aliens to move in an erratic way. I tweaked this using chatGPT, who did the trig for me when-->
         #-->I requested a formula to exclude certain ranges of angles, to force this class into more horizontal movement. 
    def _alien3_vector_changer(self): 
        while True:
            angle = random.uniform(0, 2 * math.pi)

            # Convert to degrees in [0, 180) to measure "steepness"
            deg = math.degrees(angle) % 180

            # Reject angles that are too close to vertical:
            # There is a "steep" band of angles we want to exclude.
            if 22.5 <= deg <= 157.5:
                continue

            # If we get here, angle is OK (more sideways)
            vx = math.cos(angle) * self.drift_speed
            # Almost always drift downward: vertical component is magnitude of sin minus 'slowdown' bias,-->
            # --> which will occasionally permit very shallow retrograde movement. I tweaked this one myself.
            vy = (abs(math.sin(angle)) * self.speed) - 0.075

            return vx, vy
            #TODO: Add a brief animation 1 second before the ship changes direction where the ship image switches to a version with orange/red tinted thrusters? Would this involve a .state attribute, with "normal" or "about_to_change" options?
            #TODO WAY DOWN THE ROAD IF AT ALL: images of Cruiser, Destroyer, and Interceptor where either thruster is slightly 
            #TODO: Possibly switch images for interceptor and level 3 alien. would work. 

        #function to handle start positions of aliens. 
    def spawn_pos(self, x, y):
        self.x = float(x)
        self.y = float(y)
        
        self.rect.x = int(self.x) #sync the floats of x and y coordinates to the sprite rect for later drawing
        self.rect.y = int(self.y)
    
        if self.level == 2:
              self.base_x = self.x #passing x location to a variable to be used later in the update function.

        
    def ready_to_fire(self, current_time_ms: int) -> bool:
         """This boolean based function returns TRUE if the alien 'wants' to fire.
         Allows per-sprite firing rates, and different rates for different levels.
         Does NOT create bullets, just says 'sprite fires' - main file creates the bullet."""
         if self.level == 4:
            return False #level 4 aliens are demolition ships that never fire.
         
         # Prevent firing if alien has passed the bottom of the screen
         if self.rect.bottom > self.settings.screen_height:
            return False
         
         # Firing visibility thresholds:
         # - Lazertankers (level 7) fire when 10% on screen
         # - Cruisers (level 6, center gun) should fire when 25% on screen
         # - Others fire when 33% on screen
         if self.level == 7:
            if self.rect.top <= -self.rect.height * 0.9:  # Lazertankers fire when 10% on screen
                return False
         elif self.level == 6:
            if self.rect.top <= -self.rect.height * 0.75:  # Cruisers fire when 25% on screen
                return False
         else:
            if self.rect.top <= -self.rect.height * 0.33:  # Other ships do not fire till they are ~2/3 of the way on screen
                return False
         
         if current_time_ms >= self.next_fire_time: #check if we've reached the end of the firing timer yet
            #if timer has been completed, then reset it, but at a random length that is within min and max limits for its level, found in base_settings.
            interval = random.randint(self.min_fire_interval, self.max_fire_interval)
            self.next_fire_time = current_time_ms + interval #set the firing timer again
            return True #then try to fire
         return False #otherwise, don't try to fire
    
    
    def check_destruction(self):
        """This method helps the main file's _do_collisions() function by incrementing damage on big aliens
        and returning a boolean to tell the collisions function whether that alien's hitpoints are depleted or not."""
        self.damage_stage += 1 #since the ship has been hit, add a damage stage

        if self.level == 5:
            frames = self.settings.destroyer_hitframes
        elif self.level == 6:
            frames = self.settings.cruiser_hitframes
        elif self.level == 7:
            frames = self.settings.laztanker_hitframes
        # elif self.level == 8:
        #     frames = self.settings.gunship_hitframes
        else:
            frames = None

        if not frames or self.damage_stage > len(frames):
            return True # will trigger death of the sprite

        self.image = frames[self.damage_stage - 1]
        self.rect = self.image.get_rect(center=self.rect.center)

        return False

    def set_target_player(self, player):
        """Store a one-time target player lock for listing movement (destroyers/cruisers)."""
        self.target_player = player
        if self.level == 5:
            self.listing_speed = self.settings.destroyer_list_speed
        elif self.level == 6:
            self.listing_speed = self.settings.cruiser_list_speed
        else:
            self.listing_speed = 0.0

    def update(self):
        """The method belonging to the Alien class that determines alien movement"""
        
        #movement of lvl 1 alien fleets: 
        if self.level == 1:
              if self.warping_in:
                    entry_speed = self.warp_entry_speed or self.settings.fleet_warp_entry_speed
                    self.y += entry_speed
                    target_y = self.warp_target_y if self.warp_target_y is not None else self.y
                    if self.y >= target_y:
                         self.y = float(target_y)
                         self.warping_in = False
                    self.rect.x = int(self.x)
                    self.rect.y = int(self.y)
              elif self.rect.top <= 10: #first, the row slides in at a quicker speed. 
                    self.y += self.settings.fleet_entry_speed
                    self.rect.x = int(self.x)
                    self.rect.y = int(self.y)
              
              #subsequently, back-forth plus steady advance
              elif self.level == 1 and self.rect.top > 10:
                    self.x += self.speed * self.settings.fleet_direction
                    self.y += self.settings.fleet_advance_speed #gradually slide forward, instead of jolting forward.
                    self.rect.x = int(self.x)#convert the rect location back to integer for placement.
                    self.rect.y = int(self.y) 
        

        #movement of lvl 2 aliens: measured zigzag
        elif self.level ==2:
            self.y += self.speed
            self.zig_phase += self.zig_frequency #increment the phase of the zigzagging forward by one increment of frequency

            self.x = self.base_x + self.zig_amplitude * math.sin(self.zig_phase) #the new x of the sprite is its base_x plus the amplitude times where it is now in the zig phase

            self.rect.x = int(self.x) #match new coordinates to rect, at forced integer, for placement.
            self.rect.y = int(self.y)#""

            if self.rect.left < 0: # next 5 lines are to keep the zigzag pattern from sending our alien out of bounds.
                self.rect.left = 0 
                self.x = float(self.rect.x)
            if self.rect.right > self.settings.screen_width:
                self.rect.right = self.settings.screen_width
                self.x = float(self.rect.x)
              

        #movement of lvl 3 aliens:random horizontal motion
        elif self.level == 3: 
            self.drift_timer += 1 #there is a "drift timer" that determines how long they continue in a direction before changing; here we increment it
            if self.drift_timer >= self.drift_change_interval: #if timer has reached the drift interval, it's time to change direction: 
                 self.vx, self.vy = self._alien3_vector_changer() #activate vector_changer to change direction
                 self.drift_change_interval = random.randint(40, 85) #set a new random change interval.
                 self.drift_timer = 0 #then reset the timer to zero, and it will now begin incrementing toward the interval chosen in prev. line.

            self.x += self.vx #increment x movement
            self.y += self.vy #increment y movement

            self.rect.x = int(self.x)#match x and y coordinates to enable placement. 
            self.rect.y = int(self.y)

            if self.rect.left < 0:  # next 5 lines are to keep the erratic pattern from sending our alien out of bounds.
                self.rect.left = 0
                self.x = float(self.rect.x)
                self.vx = abs(self.vx)  # bounce leftward
                self.drift_change_interval = random.randint(40, 80) #set a new random change interval.
                self.drift_timer = 0 #then reset the timer to zero, and it will now begin incrementing toward the interval chosen in prev. line.
            if self.rect.right > self.settings.screen_width:
                self.rect.right = self.settings.screen_width
                self.x = float(self.rect.x)
                self.vx = -abs(self.vx)  # bounce rightward
                self.drift_change_interval = random.randint(40, 80) #set a new random change interval.
                self.drift_timer = 0 #then reset the timer to zero, and it will now begin incrementing toward the interval chosen in prev. line.
        
        #movement for level 4 aliens is a quick straight line.
        elif self.level == 4:
            self.y += self.speed
            self.rect.y = int(self.y)

        elif self.level == 5: #destroyers are level 5. Their movement and bullets both are slower and larger. They slowly list to track a human player, with tight tracking. 
            if False: #destroyers do not list for the moment - guarding this with an if False block till I decide if this is a good feature or not.
                if hasattr(self, "target_player") and self.target_player:
                    target_center = self.target_player.rect.centerx #because it tracks on centerx, and not just checking .rect.right and .rect.left edges, it will track tighter.

                    if self.rect.centerx < target_center:  #check target's current let and right rect edges; if either of these is outside the alien's rect, it will adjust to align. Looser, slower tracking than a cruiser.  
                        self.x += self.listing_speed
                    elif self.rect.centerx > target_center:
                        self.x -= self.listing_speed
            #advance speed is unaffected.        
            self.y += self.speed
            self.rect.y = int(self.y)
            self.rect.x = int(self.x)

        elif self.level == 6: #cruisers are level 6. Their movement and bullets both are slower and larger. Cruisers will definitely slowly list.The novelty of the destroyer is: it's a big ship. The novelty of the Cruiser is: it is a bigger ship AND LISTS and shoots 2 types of bullet from three places.
            if hasattr(self, "target_player") and self.target_player: #check to see the cruiser/
                target_left = self.target_player.rect.left
                target_right = self.target_player.rect.right

                if self.rect.centerx < target_left: #check target's current let and right rect edges; if either of these is outside the alien's rect, it will adjust to align.
                    self.x += self.listing_speed
                elif self.rect.centerx > target_right: #this and the previous if create a 'loose' tracking.
                    self.x -= self.listing_speed
            #advancement speed is unaffected.
            self.y += self.speed
            self.rect.y = int(self.y)
            self.rect.x = int(self.x)
        elif self.level == 7: #laser tankers are level 7. They move even slower, and their bullets are a constant stream of red.
            self.y += self.speed
            self.rect.y = int(self.y)
        #TODO: ADD gunship ALIEN MOVEMENT HERE

       # elif self.level == 30: #rightward interceptor aliens
       #     self.x += self.speed
       #     if self.
            #TODO:consider adding here: if player y coordinate is less than interceptor y coordinate, have interceptor -= its y coordinate with its designated follow speed (add follow speed to settings), which would probably be 1; and it player's y is more than interceptor's y, have it += its y coordinate same, for a loose tracking of player.
            #TODO: add to bullet.py and base_settings.py the necessary configurations to have interceptors fire two 1high by 12wide pixel bullets and have these travel at
       # elif self.level == 31 #leftward interceptor aliens 
        #TODO: revamp interceptor aliens to EITHER have one variant that is determined to move left/right and blitted accordingly; or (simpler) have two variants, 30 and 31, to deal with left and right-moving interceptors respectively.
        #TODO: this todo belongs elswhere, but have interceptors, when they collide with players, EITHER nudge their ship sideways - or else have a timer where an !> or <! appears at the edge of the screen where one is about to spawn 1/2*interceptor_spawn_interval before it spawns. 
        #if self.rect.top > (self.settings.screen_height + 1): #killing the alien used to happen here, but it --> 
        #    self.kill() #-->has been moved to the main game function's _handle_alien_breaches() helper function.

    def draw(self): #Blit sprites onto the screen.
         self.screen.blit(self.image, self.rect)


    #Finally, to keep our level 1 alien fleet from moving off screen: 
    def check_edge_for_fleet(self):
            """Use true/false boolean to tell alien if it has hit edge of screen - for lv1 fleets"""
            if self.level != 1: #Have other aliens who do not move in fleets (lvl 2 and 3) ignore this instruction - they'll bounce on their own.
                return False
            if self.rect.right > self.settings.screen_width or self.rect.left <= 0:
                 return True
            return False


class Minion(pygame.sprite.Sprite):
    """Parent class for all minion types. Provides essential game integration without interfering with alien systems."""
    def __init__(self, settings, screen, minion_type, owner, level=1):
        super().__init__()

        self.settings = settings
        self.screen = screen
        self.minion_type = minion_type  # e.g., "laser", "Interceptor", "Bomber"
        self.owner = owner  # Reference to the entity that spawned this minion
        self.level = level  # For scoring purposes

        # Essential game integration attributes
        self.damage_stage = 0

    def spawn_pos(self, x, y):
        """Set spawn position - override in subclasses"""
        self.rect.centerx = x
        self.rect.centery = y

    def update(self):
        """Update minion - override in subclasses"""
        pass

    def draw(self):
        """Draw the minion - override in subclasses"""
        if hasattr(self, 'image') and hasattr(self, 'rect'):
            self.screen.blit(self.image, self.rect)

    def get_collision_rect(self):
        """Return collision rectangle"""
        return self.rect if hasattr(self, 'rect') else None

    def take_hit(self, dmg=1):
        """Handle taking damage - override in subclasses"""
        self.kill()

    def check_destruction(self):
        """Check if minion should be destroyed - override in subclasses"""
        return True

    def ready_to_fire(self, current_time_ms):
        """Check if ready to fire - override in subclasses"""
        return False


class Laserminion(Minion):
    """Laser minion that follows lazertankers in Hard mode."""
    def __init__(self, settings, screen, owner_tanker):
        super().__init__(settings, screen, "laser", owner_tanker, level=1)

        # Load and scale laserminion sprite
        self.image = pygame.image.load(settings.laserminion_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (27, 25))
        self.rect = self.image.get_rect()

        # Level 3 style movement setup (restricted to tanker boundaries)
        self.drift_speed = settings.laserminion_drift_speed  # Base movement speed
        self.drift_change_interval = random.randint(60, 400)
        self.drift_timer = 0
        self.vx, self.vy = self._generate_drift_vector()

        # Position tracking
        self.x = float(self.rect.centerx)
        self.y = float(self.rect.centery)

        # Firing setup
        self.min_fire_interval = self.settings.laserminion_min_fire_interval  # 4 seconds min
        self.max_fire_interval = self.settings.laserminion_max_fire_interval  # 5 seconds max 
        self.next_fire_time = 0  # Can fire immediately on spawn, even if off-screen

    def _generate_drift_vector(self):
        """Generate movement vector like level 3 aliens"""
        while True:
            angle = random.uniform(0, 2 * math.pi)
            deg = math.degrees(angle) % 180
            if 11.25 <= deg <= 168.75:  # Avoid moving too horizontally - these angles are steeper than class 3 aliens; to keep minions nearer their tankers.
                continue
            vx = math.cos(angle) * self.drift_speed
            vy = (abs(math.sin(angle)) * self.drift_speed) - 0.075
            return vx, vy

    def spawn_pos(self, x, y):
        """Set spawn position"""
        self.rect.centerx = x
        self.rect.centery = y
        self.x = float(x)
        self.y = float(y)

    def update(self):
        """Update movement and check boundaries"""
        if not self.owner.alive():
            self.kill()
            return

        # Update drift timer
        self.drift_timer += 1
        if self.drift_timer >= self.drift_change_interval:
            self.vx, self.vy = self._generate_drift_vector()
            self.drift_change_interval = random.randint(40, 85)
            self.drift_timer = 0

        # Apply movement
        self.x += self.vx
        self.y += self.vy

        # Boundary checking - bounce off the edges of the owner tanker
        tanker_left = self.owner.rect.left
        tanker_right = self.owner.rect.right

        if self.x - self.rect.width/2 < tanker_left:
            self.x = tanker_left + self.rect.width/2
            self.vx = abs(self.vx)  # Bounce right
            self.drift_timer = 0
        elif self.x + self.rect.width/2 > tanker_right:
            self.x = tanker_right - self.rect.width/2
            self.vx = -abs(self.vx)  # Bounce left
            self.drift_timer = 0

        # Update rect position
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        # Remove when owner tanker is destroyed or minion goes off screen
        if self.rect.top > self.settings.screen_height_total:
            self.kill()

    def ready_to_fire(self, current_time_ms):
        """Check if ready to fire (laserminions fire every 6-7 seconds)"""
        # No screen position restrictions - can fire even if off-screen
        if current_time_ms >= self.next_fire_time:
            self.next_fire_time = current_time_ms + 7000  # Exactly 7 seconds
            return True
        return False

    def take_hit(self, dmg=1):
        """Laserminions die in one hit"""
        self.kill()

    def check_destruction(self):
        """Always return True since laserminions die in one hit"""
        return True


class LaserminionBomb(pygame.sprite.Sprite):
    """Projectile fired by laserminions - accelerating red/white square."""
    def __init__(self, settings, screen, x, y):
        super().__init__()
        self.settings = settings
        self.screen = screen

        # Create 6x6 square
        self.image = pygame.Surface((6, 6), pygame.SRCALPHA)
        self.rect = self.image.get_rect(centerx=x, centery=y)

        # Movement
        self.speed = settings.laserminion_bomb_start_speed  # Start at configured speed
        self.acceleration = settings.laserminion_bomb_acceleration  # Acceleration per frame
        self.y = float(y)

        # Color cycling
        self.colors = settings.laserminion_bomb_colors  # Configured colors
        self.color_index = 0
        self.last_color_change = pygame.time.get_ticks()

        # Initial color fill
        self.image.fill(self.colors[0])

    def update(self):
        """Update position, speed, and color"""
        # Accelerate
        self.speed *= (1.0 + self.acceleration)  # 1% acceleration

        # Move downward
        self.y += self.speed
        self.rect.centery = int(self.y)

        # Color cycling every 4 milliseconds
        current_time = pygame.time.get_ticks()
        if current_time - self.last_color_change >= 4:
            self.color_index = (self.color_index + 1) % len(self.colors)
            self.image.fill(self.colors[self.color_index])
            self.last_color_change = current_time

        # Remove when off screen
        if self.rect.top > self.settings.screen_height_total:
            self.kill()

    def draw(self):
        """Draw the bomb to the screen"""
        self.screen.blit(self.image, self.rect)

    def spawn_pos(self, x, y):
        """Set spawn position"""
        self.rect.centerx = x
        self.rect.centery = y