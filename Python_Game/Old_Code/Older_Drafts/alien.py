#alien.py

import pygame
import math #I decided I wanted the three different levels of aliens to have different movement patterns, so imported math to calculate zigzags, etc.
import random #since aliens at level 3 need a random movement pattern (though always forward), I imported random.

#Paths to Alien Sprite Images:
ALIEN1_PATH = "img/alien1clean.png"
ALIEN2_PATH = "img/alien2clean.png"
ALIEN3_PATH = "img/alien3clean.png"
ALIEN4_PATH = "img/alien4clean.png"
DESTROYER_PATH = "img/destroyer_dmg0.png"
CRUISER_PATH = "img/cruiser_dmg0.png"
L_TANKER_PATH = "img/laz0rtanker_dmg0.png"
BOMBARDER_PATH = "img/bombarder_dmg0.png"




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
            img_path = ALIEN1_PATH
            self.speed = settings.alien1_strafe_speed #calling up the alien(x)_speed variables from base_settings, which
                                                  #main file will already have importedand assigned to "settings".
            self.spritesize = (50, 50)  #set the size of the sprite as a tuple, for multiple uses later
        elif level == 2: 
            img_path = ALIEN2_PATH
            self.speed = settings.alien2_speed
            self.spritesize = (40, 60)
        elif level == 3:
            img_path = ALIEN3_PATH
            self.speed = settings.alien3_speed
            self.spritesize = (40, 69)
        elif level == 4:
             img_path = ALIEN4_PATH
             self.speed = settings.alien4_speed
             self.spritesize = (40, 90)
        elif level == 5: #destroyers are level 5
             img_path = DESTROYER_PATH
             self.speed = settings.destroyer_speed
             self.spritesize = (90, 128)

        #LINK THE SPRITE IMAGE, and SCALE THEM.
        self.image = pygame.image.load(img_path).convert_alpha() #load the appropriate sprite, determined above
        #then use if / elif statements to smoothly scale them to proportionate size:
        if level == 1:
            self.image = pygame.transform.smoothscale(self.image, self.spritesize)
        elif level ==2:
            self.image = pygame.transform.smoothscale(self.image, self.spritesize) 
        elif level ==3: 
            self.image = pygame.transform.smoothscale(self.image, self.spritesize)
        elif level ==4:
            self.image = pygame.transform.smoothscale(self.image, self.spritesize)
        elif level == 5: #destroyer
            self.image = pygame.transform.smoothscale(self.image, self.spritesize)
        self.rect = self.image.get_rect() # get rect of sprite
        self.x = float(self.rect.x) # convert coordinates to float for smooth movement.
        self.y = float(self.rect.y)
        

        #init DIFFERENT TYPES OF MOVEMENT depending on level:
       
        if self.level ==2: # level 2 aliens to zigzag down the screen independently of each other. 
          
             self.zig_amplitude = random.randint(10,50)            
             self.zig_frequency = 0.08 #amplitude and frequency to use for a sine wave function - I'm slightly hazy on the math here.
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
        elif self.level == 7: #laser tankers
             self.min_fire_interval = settings.laztanker_min_fire_interval
             self.max_fire_interval = settings.laztanker_max_fire_interval
             self.next_fire_time = 0
             self.max_damage = len(self.settings.laztanker_hitframes)
             self.damage_stage = 0 #set damage stage to 0
        elif self.level == 8: #bombarders
             self.min_fire_interval = settings.bombarder_min_fire_interval
             self.max_fire_interval = settings.bombarder_max_fire_interval
             self.next_fire_time = 0
             self.max_damage = len(self.settings.bombarder_hitframes)
             self.damage_stage = 0 #set damage stage to 0

        #Next: a helper function for level 3 aliens to move in an erratic way. 
    def _alien3_vector_changer(self):
        """a helper function for the update() function that will allow level 3 aliens to move in an erratic way."""  
         #I tweaked this using chatGPT, which did the trig for me when I requested a formula to exclude certain ranges of angles,-->
         # -->to force this class into more horizontal movement. 
        while True:
            angle = random.uniform(0, 2 * math.pi)
            # Convert to degrees in [0, 180) to measure "steepness"
            deg = math.degrees(angle) % 180
            # Reject angles that are too close to vertical: there is a "steep" band of angles we want to exclude.
            if 22.5 <= deg <= 157.5:
                continue
            # If we get here, angle is OK (more sideways)
            vx = math.cos(angle) * self.drift_speed
            # Almost always drift downward, but shallowly: vertical component is magnitude of sin minus 'slowdown' bias,-->
            # --> which will occasionally permit very shallow retrograde movement. I tweaked this one myself.
            vy = (abs(math.sin(angle)) * self.speed) - 0.075

            return vx, vy
      

        
    def spawn_pos(self, x, y):
        """method belongign to the alien class that handles start positions of aliens"""
        self.x = float(x)
        self.y = float(y)
        
        self.rect.x = int(self.x) #sync the floats of x and y coordinates to the sprite rect for later drawing
        self.rect.y = int(self.y)
    
        if self.level == 2:
              self.base_x = self.x #passing x location to a variable to be used later in the update function.

        
    def ready_to_fire(self, current_time_ms: int) -> bool:
         """This boolean based method returns TRUE if the alien 'wants' to fire.
         Allows per-sprite firing rates, and different rates for different levels.
         Does NOT create bullets, just says 'sprite fires' - main file creates the bullet."""
         if self.level == 4:
            return False #level 4 aliens are demolition ships that never fire.
         
         if self.rect.top <=-self.rect.height*.33: #ships do not fire till they are ~2/3 of the way on screen.
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
        if self.damage_stage > self.max_damage:
            return True # will trigger death of the sprite
        if self.level == 5:
            self.image = pygame.image.load(self.settings.destroyer_hitframes[self.damage_stage-1]).convert_alpha() #load the new sprite image, more damaged.
            self.image = pygame.transform.smoothscale(self.image, self.spritesize)#size the sprite according to attribute in init
        if self.level == 6:
            self.image = pygame.image.load(self.settings.cruiser_hitframes[self.damage_stage-1]).convert_alpha() #load the new sprite image, more damaged.
            self.image = pygame.transform.smoothscale(self.image, self.spritesize)
        if self.level == 7:
            self.image = pygame.image.load(self.settings.laztanker_hitframes[self.damage_stage-1]).convert_alpha() #load the new sprite image, more damaged.
            self.image = pygame.transform.smoothscale(self.image, self.spritesize)
        if self.level == 8:
            self.image = self.settings.bombarder_hitframes[self.damage_stage-1]
            self.image = pygame.image.load(self.settings.bombarder_hitframes[self.damage_stage-1]).convert_alpha() #load the new sprite image, more damaged.
            self.image = pygame.transform.smoothscale(self.image, self.spritesize)
        return False

    def update(self):
        """The method belonging to the Alien class that determines alien movement"""
        
        #movement of lvl 1 alien fleets: back-forth plus steady advance
        if self.level == 1:
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
                 self.drift_change_interval = random.randint(40, 80) #set a new random change interval.
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

        elif self.level == 5: #destroyers are level 5. Their movement and bullets both are slower and larger.
            self.y += self.speed
            self.rect.y = int(self.y)

        if self.rect.top > self.settings.screen_height:
            #//to do: add a way to count how many aliens have penetrated defenses
            self.kill()

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
