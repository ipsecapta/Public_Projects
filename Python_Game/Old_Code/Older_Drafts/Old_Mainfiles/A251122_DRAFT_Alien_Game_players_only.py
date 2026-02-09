#Visintainer Aliens.py
import sys
import pygame

from base_settings import Settings #import Settings module before other custom - because custom modules are referencing base_settings through the main file's code,-->
                                   #-->not directly from the base_settings module.
from ship import Ship
from bullet import Bullet
from alien import Alien

#create the game class
class AlienInvasion:
    """Class to manage entire game, its classes, assets, and behavior of elements."""
#initialize it with the init function:
    def __init__(self):
        """initialize the game, create game resources"""
        pygame.init() # initialize pygame background settings the game will need to function correctly
        pygame.display.set_caption("Alien Invasion!") # set the title for the game
        
        self.clock = pygame.time.Clock() #this lets pygame automatically handle the frame rate correction. It creates a clock that ticks one on each pass through the main loop.
        self.settings = Settings() # import settings from base_settings.py and assign them to an attribute of the __init__ function.

    #Create screen -->according to the specifications in inte base_settings file, and allow it to be resizable:
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height), pygame.RESIZABLE) 
    
    # call the load_images function from base_settings' Settings class, to load initial images onto screen created in previous line:
        self.settings.load_images(self.screen) 

    # Next create the ship sprite groups
        self.players = pygame.sprite.Group() # create the sprite grouping for both player ship sprites
        self.p1ship = Ship(self.settings, self.screen, player_id=1, player_level=1) # create player 1 ship
        self.p2ship = Ship(self.settings, self.screen, player_id=2, player_level=1) # create player 2 ship
        self.players.add(self.p1ship, self.p2ship) # add both player ships to the sprite grouping.
    #then the alien sprite groups
        self.aliens = pygame.sprite.Group()
    #Then bullet sprite groups:
        self.player_bullets = pygame.sprite.Group()#create a pygame Group object including all player bullets
        self.alien_bullets = pygame.sprite.Group()# "" "" all alien bullets.

    #set up wave mechanics:
        self.current_wave_index = 0 #start on wave 1
        self.game_state = "playing" #have three: playing, between waves, or finished.
        self.next_wave_start_time = None

        self.max_visible_level1_rows = 4 #only four rows of level 1 aliens on screen at any given time
        self.level1_row_spawn_delay_ms = 800
        self.level1_reinforcements_threshhold = 40

        self.level1_rows_total = 0
        self.level1_rows_spawned = 0
        self.level1_rows_remaining = 0

        self.level2_remaining = 0
        self.level3_remaining = 0

        self.next_level1_row_time = 0
        self.next_level2_spawn_time = 0
        self.next_level3_spawn_time = 0 

       # self._start_wave(self.current_wave_index                )
##############################BEGIN HERE TOMORROW. ADD COMMENTARY TO THE ABOVE. MAKE SURE YOU"RE IMPORTING INFO FROM THE base_settings.waves_template [{}{}]
    #define the main loop:
    def run_game(self):
        """This is the Main Game Loop loop."""
        while True: # this means the event lop is always running. It will be what the program uses to watch for keyboard input and other game changes.
            self._check_events() # reads input from the pygame.event.get() function, and sets booleans for movement, firing, etc
            self._update_game() # moves ship and game elements based on booleans - 
            self._draw_screen() # draws the result
            self.clock.tick(60) # keeps the clock created above in line 17 ticking 60 times per second.

    #define all helper functions referenced above in the main loop:

    def _check_events(self): # helper function that checks game events for the main game loop
        for event in pygame.event.get(): # this is the event loop, which moves the game along by using the pygame 'get' function for the pygame 'event' class.
            if event.type == pygame.QUIT: #this if loop is to correlate closing window with the pygame event type 'quit'.
                sys.exit()
            #these elifs direct the _check_event function to its own helper functions, _check_keydown_events and _check_keyup_events.
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event): #check for all keys pressed
        # For each ship, see if the pressed key belongs to it
        for ship in self.players: # for each ship sprite in the self.players group created above at line 25, check to see if any key-press events match its player's keystrokes:
            keys = ship.keys # the keys variable will equal the .keys attribute of the ship under iteration.
            #the following ifs and elifs say:  for that ship's movement (as defined in the settings and referenced in the imported Ship class)-->
            #--> is pushed, 
            if event.key == keys["left"]:#if a key event matches the dictionary entry in the "keys" dictionary
                ship.moving_left = True #then change the boolean for the ship.moving<direction> attribute of that Ship to True.
            elif event.key == keys["right"]:
                ship.moving_right = True
            elif event.key == keys["up"]:
                ship.moving_up = True
            elif event.key == keys["down"]:
                ship.moving_down = True
            elif event.key == keys["fire"]:
                self._fire_bullet(ship) #if the fire key is pressed, then run the helper function _fire_bullet and pass it the ship as its ship parameter..

            # Later: powerup keys go here
            # if event.key == keys["fire"]:
            #     self._fire_bullet(ship)
            # etc.

    def _check_keyup_events(self, event): #check through all keys not pressed; same procedure as in the previous check_keydown_events helper function.
        for ship in self.players:
            keys = ship.keys
            #set applicable ship movement booleans to False.
            if event.key == keys["left"]:
                ship.moving_left = False
            elif event.key == keys["right"]:
                ship.moving_right = False
            elif event.key == keys["up"]:
                ship.moving_up = False
            elif event.key == keys["down"]:
                ship.moving_down = False


    def _fire_bullet(self, ship): # A helper function referenced above to create bullets when fire keys are pressed.
        
        self.ship = ship #pass the ship parameter to a variable in the scope of this helper function
        
        bullet_count = [] # Initialize an empty list to count bullets: 

        #Next, the for loop to count bullets:
        for b in self.player_bullets: #for every sprite found in the player_bullets group 
            if b.owner_ref is ship: #if its owner parameter is the ship in question 
                bullet_count.append(b)
        #to allow for ship level to affect max bullets, call values from base_settings and pleace each under an if statement:
        if ship.player_level == 1:
            max_bullets = self.settings.lvl1_bullet_max
        elif ship.player_level == 2:
            max_bullets = self.settings.lvl2_bullet_max
        elif ship.player_level == 3:
            max_bullets = self.settings.lvl3_bullet_max
        #finally, an if statement to enforce the max bullet cap:
        if len(bullet_count) >= max_bullets: #if the sprite under iteration has its proper max bullets attributed to it:
            return #limit the function to not fire another bullet, but end here.
        
        #otherwise:
        bullet = Bullet( settings=self.settings, screen=self.screen, 
                        x=ship.rect.centerx, y=ship.rect.top, direction=-1,
                        owner_type="player", owner_level=ship.player_level, owner_ref=ship) #create a bullet object and pass it the right parameters
        self.player_bullets.add(bullet)#add the bullet to the player bullets sprite Group

    def fire_alien_bullet(self, alien, alien_level): #helper function to fire alien bullets.
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
        else: #for boss alien
            max_bullets = self.settings.boss_bullet_max
            owner_type = "boss_alien"

        #The for loop to count bullets:
        for b in self.alien_bullets: #for every sprite found in the alien_bullets group 
            if b.owner_ref is alien: #if its owner parameter is the alien in question 
                bullet_count.append(b)
        #if statement to enforce bullet cap:
        if len(bullet_count) >= max_bullets: #if the sprite under iteration has its proper max bullets attributed to it:
            return #limit the function to not fire another bullet, but end here.
    
        #otherwise, mmake a new bullet for that alien:
        bullet = Bullet(settings=self.settings, screen=self.screen, 
                        x=alien.rect.centerx, y=alien.rect.bottom, direction=1,
                        owner_type=owner_type, owner_level = alien_level, owner_ref=alien)
        
        self.alien_bullets.add(bullet) #add the bullet to the Alien Bullets sprite group.
    
    def alien_firing_logic(self):
        current_time = pygame.time.get_ticks()

        for alien in self. aliens:
            if alien.ready_to_fire(current_time):
                self.fire_alien_bullet(alien, alien.level)
    def _update_game(self): #helper function to update player and alien sprites and bullets
        self.players.update() #note that the .update() method in this and other statements is native to the pygame sprite class.
        #self.alien.update()
        self.player_bullets.update()
        self.alien_bullets.update()

    def _draw_screen(self):#helper function to (re)draw the screen and ships
        self.screen.blit(self.settings.bg_img, (0, 0)) #redraw the background
        #eventually: draw shields)"
        for ship in self.players: #redraw the player ships
            ship.draw()
        for bullet in self.player_bullets:
            bullet.draw()
        for bullet in self.alien_bullets:
            bullet.draw()

        pygame.display.flip() #flip the display


if __name__ == "__main__":
    gameinstance = AlienInvasion()
    gameinstance.run_game()