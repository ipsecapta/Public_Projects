#Visintainer Aliens.py
import sys
import pygame

from base_settings import Settings #import Settings module before other custom - because custom modules are referencing base_settings through the main file's code,-->
                                   #-->not directly from the base_settings module.
from ship import Ship
from bullet import Bullet
from alien import Alien
import random

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
        self.current_wave_num = 0 #start on wave 1
        self.game_state = "playing" #have three: playing, between_waves, or finished.
        self.next_wave_start_time = None

        self.max_visible_level1_rows = 4 #only four rows of level 1 aliens on screen at any given time
        self.level1_row_spawn_delay_ms = 800 #delay the spawning of the next row for just under a second (800 milliseconds)
        self.level1_reinforcements_threshhold = 40 #when current row is 40 pixels down the screen, spawn next row.

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

    #set the wave index to 0, so we will draw from the first wave specs in the base_settings wave_master_index list.:
        self._new_alien_wave(self.current_wave_num)

    #define the Main Loop:

    def Main_Game_Loop(self):
        """This is the Main Game Loop."""
        while True: # this means the event lop is always running. It will be what the program uses to watch for keyboard input and other game changes.
            self._check_keystroke_events() # reads player input from the pygame.event.get() function, and sets booleans for movement, firing, etc
            self._update_game() # moves ship and game elements based on booleans - 
            self._draw_screen() # draws the result
            self.clock.tick(60) # keeps the clock created above in line 17 ticking 60 times per second.

    #define all helper functions referenced above in the main loop:

#KEYSTROKE EVENT FUNCTION
    def _check_keystroke_events(self):
        """helper function for Main_Game_Loop() that checks for keystrokes for the main game loop"""
        for event in pygame.event.get(): # this is the event loop, which moves the game along by using the pygame 'get' function for the pygame 'event' class.
            if event.type == pygame.QUIT: #this if loop is to correlate closing window with the pygame event type 'quit'.
                sys.exit()
            #these elifs direct the _check_event function to its own helper functions, _check_keydown_events and _check_keyup_events.
            elif event.type == pygame.KEYDOWN:
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
            elif event.key == keys["right"]:
                ship.moving_right = True
            elif event.key == keys["up"]:
                ship.moving_up = True
            elif event.key == keys["down"]:
                ship.moving_down = True
            elif event.key == keys["fire"]:
                self._fire_player_bullet(ship) #if the fire key is pressed, then run the helper function _fire_player_bullet and pass it the ship as its ship parameter..

            # Later: powerup keys go here
            # if event.key == keys["powerup here"]:
            #     self._fire_powerup(ship)
            # etc.
    def _fire_player_bullet(self, ship): 
                    """helper function for _check_keydown_events() to fire player bullets."""
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


    def _check_keyup_events(self, event):
        """helper function to for _check_keystroke_events() - checks for keys NOT pressed; sets applicable motion booleans to false"""
        for ship in self.players:
            keys = ship.keys
            if event.key == keys["left"]:
                ship.moving_left = False
            elif event.key == keys["right"]:
                ship.moving_right = False
            elif event.key == keys["up"]:
                ship.moving_up = False
            elif event.key == keys["down"]:
                ship.moving_down = False
    
#UPDATE GAME FUNCTION:       
    def _update_game(self):
        """helper function for Main_Game_Loop() to update player and alien sprites and bullets, & check wave state.  """
    #First, check for any between-wave pauses:
        if self.game_state == "between_waves":
            self._update_between_waves()
            return
    #allow alien bullets, as well as player ships and bullets, to still move when game ends.
        if self.game_state == "finished":
            self.players.update()
            self.player_bullets.update()
            self.alien_bullets.update()
            return
    #check for aliens that need to be spawned, whether rows or individuals
        self._update_wave_spawning()
    #functions for moving sprites:
        self.players.update() #note that the .update() method in this and other statements is native to the pygame sprite class.
        self.aliens.update()
        self.player_bullets.update()
        self.alien_bullets.update()
    #after sprites and bullets are moved, check to see if anyone is on/past the edges, and correct:
        self._check_fleet_edges()
    # allow aliens to execute firing logic
        self._alien_firing_logic()

######COLLISION LOGIC WILL GO HERE.

    #If the alien sprite group is empty, and no more are needing to spawn, start a between-wave-pause
        if not self.aliens and self._current_wave_has_finished_spawning():
            self._new_wave_pause()
    
    
    
    def _new_alien_wave(self, next_wave_num: int):
        """helper function for update_game() to spawn an new wave of aliens"""
        #first: if we reach the end of the wave index, we have no more weaves to spawn, and we end the game.""
        if next_wave_num >= len(self.settings.wave_master_index):
            self.game_state = "finished" #set the game state to finish,
#############insert a winning screen, animation, or congratulations message here.             
            return #ignore the rest of the function. 
        
        #otherwise start a new wave:
        else:
            self.current_wave_num = next_wave_num # set the current wave number. Above, this variable is important for passing to the _new_alien_wave() helper function.
            current_wave = self.settings.wave_master_index[self.current_wave_num] #set the variable "wave" to reference the dictionary corresponding with the correct index number -->
                                                            #--> in the wave_master_index in the base_settings file.
            #clear any leftover aliens - ChatGPT recommended I do this; I suppose its good to clean things up just in case?
            self.aliens.empty()

            #get alien counts for this wave:
            self.level1_rows_total = current_wave["rows_level1"] #get the number of total lvl 1 rows from the dictionary in base_settings.py
            self.level1_rows_spawned = 0 #set number of rows spawned to 0
            self.level1_rows_remaining = self.level1_rows_total #assign a variable to count how many rows remain
            print("Starting wave", self.current_wave_num, "with rows_level1 = ", self.level1_rows_total)
            self.level2_remaining = current_wave["count_level2"] #set a counter for the number of lvl 2 aliens to spawn
            self.level3_remaining = current_wave["count_level3"] #"" ""  for level 3 """"
            self.level4_remaining = current_wave["count_level4"]

            #start alien spawning using pygame timer/clock:
            now = pygame.time.get_ticks()
            self.next_level1_row_time = now #spawn a row of lvl 1 aliens immediately.
            self.next_level2_spawn_time = now + self.settings.alien2_spawn_delay #set a timer to spawn first lvl 2 alien in ~3 sec
            self.next_level3_spawn_time = now + self.settings.alien3_spawn_delay # " " lvl 3 " " 
            self.next_level4_spawn_time = now + self.settings.alien4_spawn_delay # " " lvl 4 " " 


            # Spawn up to 4 rows immediately, on-screen
            rows_to_spawn_now = min(self.settings.level1_alien_starting_rows, self.level1_rows_total)
            for row_iteration in range(rows_to_spawn_now):
                        # First visible rows start at some y offset, e.g. 60, then spaced out
                        base_y = 60
                        row_spacing = 70  # pixels between level 1 rows
                        row_y = base_y + row_iteration * row_spacing
                        self._spawn_level1_row(row_y)
                        self.level1_rows_spawned += 1

            self.level1_rows_remaining = self.level1_rows_total - self.level1_rows_spawned
            self.game_state = "playing"
        


    def _spawn_level1_row(self, row_y: int):
            """helper function for _new_alien_wave() function; spawns a row of level1 aliens"""
            tailor_alien1 = Alien(self.settings, self.screen, level=1) #create a little tailor alien for measuring.
            alien1_width = tailor_alien1.rect.width

            margin_x = self.settings.fleet_margin_x
            spacing_x = self.settings.fleet_spacing_x
            battlefield_width = self.settings.screen_width - 2 * margin_x

            lvl1_aliens_per_row = battlefield_width // (spacing_x + alien1_width) #floor division to find the nearest lesser integer, which will give us how many lvl1 aliens can fit in the screen space.

            total_row_width = lvl1_aliens_per_row * alien1_width + (lvl1_aliens_per_row - 1) * spacing_x # count up the alien widths plus the spaces, to determine the length of the row for centering
            start_x = (self.settings.screen_width - total_row_width) // 2 # clever way of keeping the row centered: find the difference between the total row width and the screen width; split that effectively in two, and stick half of it as a buffer before the first alien.
           
           
            #use a for loop to place the aliens:
            for i in range(lvl1_aliens_per_row): 
                a = Alien(self.settings, self.screen, level=1)
                x = start_x + (i * (a.rect.width + spacing_x))
                a.spawn_pos(x, row_y) #call the spawn_pos() function from alien.py to help determine spawn positions.
                self.aliens.add(a) # add the new alien to the aliens sprite group.


                            
    def _update_wave_spawning(self):
                    """helper function for _update_game() function - spawns level 1 and lvls 2-4 aliens"""
                    now = pygame.time.get_ticks() #hook into the clock with a now variable to store get_ticks()
                    level_1_aliens = []
                    if self.level1_rows_remaining > 0 and now >= self.next_level1_row_time:
                        for alien_iter in self.aliens: #cycle through all aliens in the alien sprite group  
                            if alien_iter.level ==1 : #and if they are level one, 
                                level_1_aliens.append(alien_iter) # add them to the level_1_aliens list

                    if not level_1_aliens: #if there are no level1 aliens: 
                        top_y = self.level1_reinforcements_threshhold + 10 #then tell the spawning function that all obstacles are past the threshhold and it can spawn a new wave.
                    
                    else:
                        top_y = min(alien_iter.rect.top  for alien_iter in level_1_aliens) #a way of putting a for loop inside a function; we are telling it: iterate through all aliens in -->
                                                                                        #--> the level_1_aliens list; and return the minimum value for the .rect.top method on those aliens.
                    if top_y > self.level1_reinforcements_threshhold:
                        tailor_alien = Alien(self.settings, self.screen, level=1)
                        self._spawn_level1_row(-tailor_alien.rect.height)
                        
                        #INCREMENT THE 'ALREADY SPAWNED' and 'LEFT TO SPAWN' COUNTERS:
                        self.level1_rows_remaining -= 1
                        self.level1_rows_spawned += 1
                        self.next_level1_row_time = now +self.level1_row_spawn_delay_ms #set the variable that says when it is permitted to start a new row.
                        
                        
                    #set up spawning for level 2:    
                    if self.level2_remaining > 0 and now >= self.next_level2_spawn_time:
                        self._spawn_single_alien(level = 2) # no need to reference the other parameters, since the _spawn_single_alien() helper function takes care of ths. 
                        self.level2_remaining -= 1 #increment the number remaining for this wave down by one
                        #set the next level 2 alien to spawn at a random interval in the parameters set in base_settings.py:
                        self.next_level2_spawn_time = now + random.randint(self.settings.alien2_min_spawn_interval, self.settings.alien2_max_spawn_interval) 
                    #same for level 3:
                    if self.level3_remaining > 0 and now >= self.next_level3_spawn_time:
                        self._spawn_single_alien(level = 3)  
                        self.level3_remaining -= 1
                        self.next_level3_spawn_time = now + random.randint(self.settings.alien3_min_spawn_interval, self.settings.alien3_max_spawn_interval) 
                    #same for level 4:
                    if self.level4_remaining > 0 and now >= self.next_level4_spawn_time:
                        self._spawn_single_alien(level = 4)  
                        self.level4_remaining -= 1
                        self.next_level4_spawn_time = now + random.randint(self.settings.alien4_min_spawn_interval, self.settings.alien4_max_spawn_interval) 
            
    def _spawn_single_alien(self, level: int):
                    """helper function for _update_wave_spawnining() - spawns any aliens that are ready to spawn."""
                    new_alien = Alien(self.settings, self.screen, level=level)

                    min_x = new_alien.rect.width
                    max_x = self.settings.screen_width - new_alien.rect.width
                    x = random.randint(min_x, max_x)

                    y = -new_alien.rect.height #start just off screen
                    new_alien.spawn_pos(x,y)

                    self.aliens.add(new_alien)

    def fire_alien_bullet(self, alien, alien_level):
        """helper function  for update_game() to fire alien bullets.""" 
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
            if b.owner_ref == alien: #if its owner parameter is the alien in question 
                bullet_count.append(b)
        #if statement to enforce bullet cap:
        if len(bullet_count) >= max_bullets: #if the sprite under iteration has its proper max bullets attributed to it:
            return #limit the function to not fire another bullet, but end here.
    
        #otherwise, mmake a new bullet for that alien:
        bullet = Bullet(settings=self.settings, screen=self.screen, 
                        x=alien.rect.centerx, y=alien.rect.bottom, direction=1,
                        owner_type=owner_type, owner_level=alien_level, owner_ref=alien)
        
        self.alien_bullets.add(bullet) #add the bullet to the Alien Bullets sprite group.
    

    def _check_fleet_edges(self):
        """a helper function for update_game() to check the screen edges and make sure the level one fleet aliens don't go off screen."""
        for alien in self.aliens:
            if alien.level == 1 and alien.check_edge_for_fleet():
                 self._change_fleet_direction()
                 break
    
    def _change_fleet_direction(self):
        """helper function for _check_fleet_edges() - the motor that moves the level 1 fleets forward and also bounces them back from edges"""
        for alien in self.aliens:
              if alien.level == 1:#examine only level 1 aliens
                   alien.rect.y += self.settings.fleet_advance_speed #
                   alien.y = float(alien.rect.y)  # change coordinate to float, for smooth movement and to stay synced with other float measurements. 
        self.settings.fleet_direction *= -1 #crucial: the point of all this. IF you have hit an edge, level1 alien, then you must change direction. 
    
    def _alien_firing_logic(self):
        """helper function for _update_game() - check if each alien is ready to fire, and if so, create a bullet object at the appropriate level."""
        now = pygame.time.get_ticks()
        for alien in self.aliens:
             if alien.ready_to_fire(now):
                  self.fire_alien_bullet(alien, alien.level)


    def _current_wave_has_finished_spawning(self) -> bool:
        """helper function for _update_game() - boolean function that returns 'True' if there are no more aliens left to spawn for this wave."""
        return (
             self.level1_rows_remaining == 0 and
             self.level2_remaining == 0 and
             self.level3_remaining == 0 and
             self.level4_remaining == 0
                    ) 
    

    def _new_wave_pause(self):
        """helper function for _update_game() to create a small breather between levels."""
        base_pause = self.settings.new_wave_pause
        growing_pause = (self.current_wave_num + 1) * 1000
        pause_ms = max(base_pause, growing_pause) #call up the predetermined pause length from base_settings, compare to current wave number and pick larger. -->
                                                                #-->This gives longer breaks at higher levels;  min break is 5 seconds.)
        now = pygame.time.get_ticks()
        self.next_wave_start_time = now + pause_ms # sets the next wave start time to teh pause length from now.

        self.current_wave_num += 1 # CRUCIAL: HERE WE INCREMENT THE WAVE NUMBER UP by ONE!

        if self.current_wave_num >=len(self.settings.wave_master_index):
             self.game_state = "finished"
        else:
             self.game_state = "between_waves" #put the game state in 'between wave break' for the time determined above.
    
    def _update_between_waves(self):
         if self.next_wave_start_time is None: #once the timer set in _new_wave_pause() is run out,
              return
         now = pygame.time.get_ticks()
         if now >= self.next_wave_start_time: #get the time and check if we're ready to spawn (we already know we are)
              self._new_alien_wave(self.current_wave_num) #CREATE THE NEXT WAVE!
              self.next_wave_start_time = None
              self.game_state = "playing" #CHANGE GAME STATE TO "PLAYING!"



    def _draw_screen(self):
        """helper function for Main Game Loop to (re)draw the screen and ships"""
        self.screen.blit(self.settings.bg_img, (0, 0)) #redraw the background
        #eventually: draw shields)"

        #redraw the player ships
        for ship in self.players: 
            ship.draw()
        #redraw aliens
        for alien in self.aliens:
            alien.draw()
        #redraw player and then alien bullets
        for bullet in self.player_bullets:
            bullet.draw()
        for bullet in self.alien_bullets:
            bullet.draw()

        pygame.display.flip() #flip the display


if __name__ == "__main__":
    gameinstance = AlienInvasion()
    gameinstance.Main_Game_Loop()