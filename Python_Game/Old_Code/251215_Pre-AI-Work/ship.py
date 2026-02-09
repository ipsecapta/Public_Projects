#ship.py
# A file to model the player ships' level, mechanics, and appearance. 
# For other ship settings (movement speed, firing speed, etc) check the base_settings.py file. 
import pygame


ship1_path = "img/blueship.png"
ship2_path = "img/redship.png"
ship3_path = "img/cyanship.png"
ship4_path = "img/pinkship.png"

class Ship(pygame.sprite.Sprite): #create a Ship class, that is a sub-class of the pygame Sprite class.
    def __init__(self, settings, screen, player_id, player_level=1, player_health=11, player_lives=3, score = 0, player_state = "alive"):
        super().__init__()
        self.settings = settings # WHEN THE SHIP OBJECT(S) ARE CREATED IN THE MAIN FILE, THE VALUE PASSED FOR this .settings parameter WILL BE -->
                                 #--> the Settings() class object created from the Settings class imported from the base_settings module.
        self.screen = screen
        self.player_id = player_id
        self.player_level = player_level
        self.player_score = score
        self.firing = False # This attribute is to allow for button holding to fire, instead of having to tap the fire button over and over. This becomes important at higher levels.
        self.next_fire_time = 0
        self.player_health = player_health
        self.player_lives = player_lives
        self.player_state = player_state # options are "alive", "between lives", and "dead"
        self.current_max_health = 10 + player_level # init this attribute for later use 
        

        # Pick a sprite image and movement key set, based on player:
        if player_id == 1: #for player 1
            image_path = ship1_path #use the path determined above for the image of player 1s ship.
            self.keys = settings.player1_keys #The movement keys for player 1 are drawn from the player1_keys dictionary in the base_settings module
        elif player_id == 2:
            image_path = ship2_path #SAME AS ABOVE BUT FOR PLAYER 2
            self.keys = settings.player2_keys #SAME AS ABOVE BUT FOR PLAYER 2
        elif player_id == 3:
            image_path = ship3_path #SAME AS ABOVE BUT FOR PLAYER 2
            self.keys = settings.player3_keys #SAME AS ABOVE BUT FOR PLAYER 2
        elif player_id == 4:
            image_path = ship4_path #SAME AS ABOVE BUT FOR PLAYER 2
            self.keys = settings.player4_keys #SAME AS ABOVE BUT FOR PLAYER 2

        #load each image from its path, and scale each image
        self.image = pygame.image.load(image_path).convert_alpha() #use the convert_alpha() method to load the image in rgba, such that its transparent background (a.k.a. alpha channel) is maintained (as a png)
        self.image = pygame.transform.smoothscale(self.image, (round(self.settings.multiplayer_resizer*60), round(self.settings.multiplayer_resizer*40))) #set each image scale to 60x40 pixels.
        # Get rectangle of ship sprite:
        self.rect = self.image.get_rect()

        #place at starting position:
        if player_id == 1:
            self.rect.centerx = settings.screen_width * 0.65 # player 1 starts 70% of the screen length from left.
        elif player_id == 2:
            self.rect.centerx = settings.screen_width * 0.35 # player 2 starts 30% of screen length from left.
        elif player_id == 3:
            self.rect.centerx = settings.screen_width * 0.85
        elif player_id == 4:
            self.rect.centerx = settings.screen_width * 0.15

        self.rect.bottom = settings.screen_height * 0.9 # both players start toward the bottom of the screen vertically.

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
            self.current_max_health = self.player_level + 10 # max health goes up with player level - this number will be useful when respawning or healing players.
        else:
            self.speed = self.settings.base_ship_speed

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

        #Block of code to adjust player_level based on how much xp they've earned. Threshholds are set in base_settings file.
        if self.player_score in self.settings.lvl2_xp_requirement:
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

    def draw(self):
        self.screen.blit(self.image, self.rect) #blit the sprite image to the screen.