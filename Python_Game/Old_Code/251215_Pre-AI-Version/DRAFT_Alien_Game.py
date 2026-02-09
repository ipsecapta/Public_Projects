#Visintainer Aliens.py
import sys
import pygame

from base_settings import Settings #import Settings module before other custom - because custom modules are referencing base_settings through the main file's code,-->
                                   #-->not directly from the base_settings module.
from ship import Ship
from bullet import Bullet
from alien import Alien
import menu_helpers
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
   
    #initialize font elements
        self.hud_font = pygame.font.SysFont(None,19)
        self.hud_text_color = (self.settings.hud_text_color) #get font color from base_settings


    #Create screen -->create the screen according to the specifications in in the base_settings file, and allow it to be resizable:
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height), pygame.RESIZABLE) 
    # Next create the ship sprite groups
        self.players = pygame.sprite.Group() # create the sprite grouping for both player ship sprites
        """self.p1ship = Ship(self.settings, self.screen, player_id=1, player_level=1) # create player 1 ship
        self.p2ship = Ship(self.settings, self.screen, player_id=2, player_level=1) # create player 2 ship
        self.p3ship = Ship(self.settings, self.screen, player_id=3, player_level=1) # create player 2 ship
        self.p4ship = Ship(self.settings, self.screen, player_id=4, player_level=1) # create player 2 ship"""
        #and a counter that will be used to track how many players have died:
        self.players_inactive = 0


    #then the alien sprite groups
        self.aliens = pygame.sprite.Group()
    #Then bullet sprite groups:
        self.player_bullets = pygame.sprite.Group()#create a pygame Group object including all player bullets
        self.alien_bullets = pygame.sprite.Group()# "" "" all alien bullets.

    #set up wave mechanics:
        self.current_wave_num = None #wave will be selected at game start
        self.game_state = "start_menu" #have five: start menu, playing, paused, between_waves, or finished.
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

    #define the Main Loop:


    def Main_Game_Loop(self):
        """This is the Main Game Loop."""

#starting with a brief CLI menu - it will hide the main screen, and then bring it back. 
        
        if self.game_state == "start_menu":
            menu_helpers.gamesetup(self, Ship) #here we initialize the starting menu module, and pass it the Ship class so it can create ships based on input.

# Next, given the input above, set up victory/defeat, player death/respawn varables:
        self.max_breach_tolerance = self.current_wave_num + 2 # the higher the level, the more breach tolerance we have.
        self.breaches_this_wave = 0 #We could have put this above in the __init__, but it seemed tidier to put it here.
            
        
    #load screen backgrounds into the program:
        self.settings.load_images()     

    #set the wave index correctly, ready a new wave, now that the gamesetup() function has gotten everything ready:
        self._new_alien_wave(self.current_wave_num)

#and now the main code:
        while True: # this means the event loop is always running. It will be what the program uses to watch for keyboard input and other game changes.
            self._check_keystroke_events() # reads player input from the pygame.event.get() function, and sets booleans for movement, firing, etc
            self._update_game() # moves ship and game elements based on booleans - 
            self._draw_screen() # draws the result
            self.clock.tick(60) # keeps the clock created above in line 17 ticking 60 times per second.

    #define all helper functions referenced above in the main loop:

#KEYSTROKE EVENT FUNCTION
    def _check_keystroke_events(self):
        """helper function for Main_Game_Loop() that checks for keystrokes for the main game loop"""
        for event in pygame.event.get(): # this is the event loop, which moves the game along by using the pygame 'get' function for the pygame 'event' class.
            if event.type == pygame.QUIT: #his if loop is to correlate closing window with the pygame event type 'quit'.
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
                ship.firing = True
                #self._fire_player_bullet(ship) #if the fire key is pressed, then run the helper function _fire_player_bullet and pass it the ship as its ship parameter..

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

                    #to allow for ship level to affect max bullets, call values from base_settings
                    """ I used to have a bunch of if statements to parse this (if player_level == 1, etc);  
                    # but I knew there had to be a simpler way, so I described a concept of an iterable variable name lookup to an AI, 
                    # and it explained dynamic attribute lookups to me, which is what I chose to use for this section."""                    
                    #Note: SPEED IS CHANGED IN ship.py update() function, also using getattr.
                    level = ship.player_level
                    max_bullets = getattr(self.settings, f"lvl{level}_bullet_max", 3)
                    
                    #finally, an if statement to enforce the max bullet cap:
                    if len(bullet_count) >= max_bullets: #if the sprite under iteration has its proper max bullets attributed to it:
                        return #limit the function to not fire another bullet, but end here.
                    #otherwise:
                    bullet = Bullet( settings=self.settings, screen=self.screen, 
                                    x=ship.rect.centerx, y=ship.rect.top, direction=-1,
                                    owner_type="player", owner_level=ship.player_level, owner_ref=ship) #create a bullet object and pass it the right parameters
                    #TODO: play sound: player shot
                    #self.sounds["player_firing"].play()
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
            elif event.key == keys["fire"]:
                 ship.firing = False
    
#GAME UPDATE FUNCTION:       
    def _update_game(self):
        """helper function for Main_Game_Loop() to update player and alien sprites and bullets, & check wave state.  """
    #First, check for any between-wave pauses:
        #if self.game_state == "paused":
            #self._pause_game()

        if self.game_state == "between_waves":
            self.players.update() 
            self.player_bullets.update()
            self.alien_bullets.update()
            self._update_between_waves()
            return
    #allow alien bullets, as well as player ships and bullets, to still move when game ends.
        if self.game_state == "victory":
            self.players.update()
            self.player_bullets.update()
            self.alien_bullets.update()
            return
        if self.game_state == "defeat":
            self.aliens.update()
            self.player_bullets.update()
            self.alien_bullets.update()
            return
   
    #Rest of instructions in this function are for normal gameplay. First, check for aliens that need to be spawned, whether rows or individuals
        self._update_wave_spawning()
    #functions for moving sprites:
        self.players.update() #note that the .update() method in this and other statements is native to the pygame sprite class.
            #quick check, to enable 'hold down' fire instead of endless button mashing:
        now = pygame.time.get_ticks()
        for ship in self.players:
             if ship.firing and now >= getattr(ship, "next_fire_time", 0): #this if statement allows the loop to check after every time it updates
                                                                        #-->the players, to see if they're still holding down the firing key.
                self._fire_player_bullet(ship)
                ship.next_fire_time = now + 150
        self.aliens.update()
        self._handle_alien_breaches()
        self.player_bullets.update()
        self.alien_bullets.update()
    #after sprites and bullets are moved, check to see if anyone is on/past the edges, and correct:
        self._check_fleet_edges()
    # allow aliens to execute firing logic
        self._alien_firing_logic()
        self._do_collisions()


    #If the alien sprite group is empty, and no more are needing to spawn, start a between-wave-pause
        if not self.aliens and self._current_wave_has_finished_spawning():
            self._new_wave_pause()
    
        
    def _new_alien_wave(self, next_wave_num: int):
        """helper function for update_game() to spawn an new wave of aliens"""
        #first: if we reach the end of the wave index, we have no more weaves to spawn, and we end the game.""
        if next_wave_num >= len(self.settings.wave_master_index):
            self.game_state = "victory" #set the game state to finish,


            return #ignore the rest of the function. 
        
        #otherwise start a new wave:
        else:
            self.aliens_breached_this_wave = 0
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

        
            # Spawn up to 4 rows immediately, on-screen
            rows_to_spawn_now = min(self.settings.level1_alien_starting_rows, self.level1_rows_total, 6)
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
            battlefield_width = self.settings.screen_width - (2 * margin_x)
            lvl1_aliens_per_row = (battlefield_width // ( spacing_x + alien1_width)) #floor division to find the nearest lesser integer, which will give us how many lvl1 aliens can fit in the screen space.

            total_row_width = lvl1_aliens_per_row*alien1_width + (lvl1_aliens_per_row - 1)*spacing_x # count up the alien widths plus the spaces, to determine the length of the row for centering
            start_x = (self.settings.screen_width - total_row_width) // 2 # clever way of keeping the row centered: find the difference between the total row width and the screen width; split that effectively in two, and stick half of it as a buffer before the first alien.
            #use a for loop to place the aliens:
            for i in range(lvl1_aliens_per_row): 
                fleet_alien_iter = Alien(self.settings, self.screen, level=1)
                x = start_x + i*(fleet_alien_iter.rect.width + spacing_x)
                fleet_alien_iter.spawn_pos(x, row_y) #call the spawn_pos() function from alien.py to help determine spawn positions.
                self.aliens.add(fleet_alien_iter) # add the new alien to the aliens sprite group.


                            
    def _update_wave_spawning(self):
                    """helper function for _update_game() function - spawns level 1 and lvls 2-4 aliens. 
                    Draws adjusted spawn interval info from menu_helpers.py."""
                    now = pygame.time.get_ticks() #hook into the clock with a now variable to store get_ticks()
                    
                    #spawning lvl 1 aliens
                    if self.level1_rows_remaining > 0 and now >=self.next_level1_row_time:
                        level_1_aliens = [alien for alien in self.aliens if alien.level ==1]
                        
                        if level_1_aliens:
                            top_y = min(alien.rect.top for alien in level_1_aliens)
                            
                        else:
                            top_y = self.level1_reinforcements_threshhold + 10

                        if top_y > self.level1_reinforcements_threshhold:
                            tailor_alien = Alien(self.settings, self.screen, level=1)
                            self._spawn_level1_row(-tailor_alien.rect.height) 

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
            
    def _spawn_single_alien(self, level: int):
                    """helper function for _update_wave_spawning() - spawns any aliens that are ready to spawn."""
                    new_alien = Alien(self.settings, self.screen, level=level)

                    if new_alien.level == 2: #spawn level 2 aliens so their zigzagging won't get them stuck against the side of the screen.
                        min_x = new_alien.zig_amplitude + new_alien.rect.width
                        max_x = self.settings.screen_width - (new_alien.zig_amplitude + new_alien.rect.width)
                    
                    if new_alien.level == 6: #cruiser
                         min_x = int(self.settings.screen_width * 0.3)
                         max_x = int(self.settings.screen_width * 0.7)
                    
                    else:
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
        #alien level 4 is not listed, since it does not fire any bullets.
        elif alien_level == 5: #destroyer
            max_bullets = self.settings.destroyer_bullet_max
            owner_type ="alien"
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
        #print("Fire from", alien.level, "at", alien.rect.centerx, alien.rect.centery)#debugging
        #otherwise, mmake a new bullet for that alien:
        bullet = Bullet(settings=self.settings, screen=self.screen, 
                        x=alien.rect.centerx, y=alien.rect.bottom, direction=1,
                        owner_type=owner_type, owner_level=alien_level, owner_ref=alien)
        #TODO: ADD ALIEN FIRING SOUND EFFECTS HERE -
        #self.sounds[f"level_{alien_level}_alien_fire"].play() #note to include a None level, and sounds that correlate to it - basically, the mini bullets fired from the Cruiser and Bombarder's support turrets.
        self.alien_bullets.add(bullet) #add the bullet to the Alien Bullets sprite group.
    

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
        now = pygame.time.get_ticks()
        for alien in self.aliens:
             if alien.ready_to_fire(now):
                  #debug
                  #print("Alien fired:", alien.level, alien.rect.centerx, alien.rect.centery)
                  self.fire_alien_bullet(alien, alien.level)
    

    def _do_collisions(self):
        """Handles collisions"""
        #Tracking collisions betweel PLAYER BULLETS and ALIEN SHIPS:
        alien_is_hit = pygame.sprite.groupcollide(self.player_bullets, self.aliens, True, False)
        for bullet, aliens_hit in alien_is_hit.items():
                #this for loop exist to allow higher level aliens to require several shots in order to be damaged. 
                for alien in aliens_hit:
                    destroyed = False
                    if alien.level in (1,2,3,4): #aliens at levels 1-4 only need 1 hit to destroy them.
                        destroyed = True
                    elif alien.level in (5,6,7,8): #aliens at levels 5-8 need multiple hits; a function in the alien.py file allows variety based on class.
                        destroyed = alien.check_destruction() #for aliens with hitpoints, the .destroyed() function in alien.py will return a True or False depending on -->
                                                    #--> how many times the alien has been hit.
                   
                    #kill the alien, if the above code determines it has been destroyed:
                    if destroyed:
                        #TODO:if alien.level in (1,2,3,4):
                            #small alien explosion
                        #TODO:elif alien.level in (5,6)
                            #self.sounds["destroyer_cruiser_explosion"].play()
                        #elif alien.level == 7 and element == "addon":
                            #self.sounds["lazertanker_piece explosion"].play()
                        #elif alien.level == 7 and element != "main":
                            #self.sounds["lasertanker_full_explosion"].play()
                        #elif alien.level == 8 and element == "addon":
                            #self.sounds["bombarder_piece_explosion"].play()
                        #elif alien.level == 8 and element == "main":
                            #self.sounds["bombarder_full_explosion"].play()
                        alien.kill()
                             
                        #after the alien is killed, take care of incrementing player score up - in order to make "boss" level work, I use a try+except; the try requires-->
                        # -->that the alien level be a number that can run through a scoring equation.        
                        try:
                            bullet.owner_ref.player_score += alien.level * ((alien.level* 1/2)*20) #scoring equation - note it has to have an integer as the alien level.
                            print (f"Player {bullet.owner_ref.player_id} hit a level {alien.level} alien and their score is now {bullet.owner_ref.player_score}")
                        except: #since "boss" level is a string, a try/except works well here to score the boss, without having to change the overall scoring equation above.
                            #player who killed boss alien gets 10,000 points;
                            bullet.owner_ref.player_score += 50000
                            print (f"CONGRATULATIONS Player {bullet.owner_ref.player_id}, you got the final hit on the BOSS ALIEN and your score is now {bullet.owner_ref.player_score}!")
                            #other players get 5,000 points
                            for player in self.players:
                                if player.player_id != bullet.owner_ref.player_id:
                                    player.player_score += 10000
                                    print(f"Well done, Player {player.player_id} - you finished with a score of {player.player_score}!")
                    

        #laser_hits_alien = pygame.sprite.groupcollide(self.aliens, self.laser, True, False)
        #shockwave_hits_alien = pygame.sprite.groupcollide(self.aliens, self.shockwave, True, False) #shockwaves tear through aliens. 

        #Tracking collisions between an ALIEN BULLETS and PLAYER SHIPS:
        player_is_hit = pygame.sprite.groupcollide(self.alien_bullets, self.players, True, False)
        if player_is_hit:
             for bullet, ships_hit in player_is_hit.items(): #note that in this for loop, the order of the two iterating variables has to match the -->
                                                            #--> Order of their corresponding parameter in the collision parameters.
                  for ship in ships_hit:
                    ship.player_health -= 1
                    print (f"PLAYER ID {ship.player_id}, your ship was just hit and you now have {ship.player_health} health left!") #debugging
                    if ship.player_health <= 0:
                        ship.player_lives -= 1
                        #player.player_state = "between_lives"
                        #self._start_player_respawn_timer(player)
                        #TODO: Respawn timer and animation
                        #TODO: Player lifeloss sound effect - if statements determining whose lifeloss to play, using Name field.
                        #name = ship.player_name 
                        # self.sounds[f'{name}_lifeloss'].play() #note to include a none category with a generic sound.
                        print (f"Player {ship.player_id} has lost a life and now has {ship.player_lives} lives left!")
                        ship.player_health = ship.current_max_health #reset player health.
                    if ship.player_lives <= 0:
                       self._player_death(ship)

        #Tracking collisions between ALIEN SHIPS and PLAYER SHIPS
        alien_collideswith_player = pygame.sprite.groupcollide(self.aliens, self.players, False, False)
        if alien_collideswith_player:
             for collided_alien, collided_player in alien_collideswith_player.items():  
                  self._player_alien_collision(collided_alien, collided_player)

                 
    def _player_alien_collision(self, collided_alien, collided_player):
                for player in collided_player:
                    
                    if collided_alien.level in (1,2,3):
                        player.player_health -= 1
                        #print (f"Player {player.player_id} and a level {collided_alien.level} alien collided! Player {player.player_id}'s health is now {player.player_health}")
                        #TODO: add loud shipcollide explosion sound here. 
                    if collided_alien.level == 4:
                        player.player_health -= 3
                        player.player_score += 300
                        print (f"Player {player.player_id} used their ship as a shield, reducing them to {player.player_health} health. Their score is now {player.player_score}")
                    if collided_alien.level in (5,6,7,8):
                         player.x = player.x
                         player.y = player.y
                         print (f"Player {player.player_id} ran into a level {collided_alien.level} alien ship and it tore up  their ship like tissue paper!")
                  
              #check player health; handle any life losses or dead players..
                    if player.player_health <= 0:
                        player.player_lives -= 1
                        #player.player_state = "between_lives"
                        #self._start_player_respawn_timer(player)
                        print (f"Player {player.player_id} has lost a life and now has {player.player_lives} lives left!")
                        player.player_health = player.current_max_health #reset player health.
#########################hook in a respawn function here eventually; will take care of resetting player health, dropping them to the bottom of screen with a damaged, transparent sprite 

                    if player.player_lives <= 0:
                       self._player_death(player)

                
                #level 1-4 aliens are destroyed by impact; level 
                    if collided_alien.level <= 4:
                          collided_alien.kill()
                          #TODO: add loud explosion kill sound here
                     
    """*******************************CONTINUE WORK HERE
            def _start_player_respawn_timer(self,player):
                        now = pygame.time.get_ticks()
                        self.player_respawn_time = max(3, (now + self.settings.player_respawn_time_ms - (self.current_wave_num * 1000))) #respawn player in 3 seconds or "10-current wave number" seconds.
                        self.player.
                        print(f"Player {player.player_id} has been downed, and will take {max(3, (10-self.current_wave_number))} seconds to respawn.")
            """
    def _player_death(self,player):
                        """Helper function for _do_collisions() and _player_alien_collisions to execute player death tasks."""
                        player.player_state = "dead"
                        print(f"Player {player.player_id} has been killed!!!")
                        self.players_inactive += 1
                        #TODO: Add player defeat sound - elifs to say which sound to pick depending on player Name (could add name field for Eli, Audrey, Jakey, Etc.)
                        if self.players_inactive >= len(self.players):
                             self.game_state = "defeat"     

    
######WAVE DYNAMICS FUNCTIONS:    
    def _current_wave_has_finished_spawning(self) -> bool:
        """helper function for _update_game() - boolean function that returns 'True' 
        if there are no more aliens left to spawn for this wave and all aliens are dead."""
        return (self.level1_rows_remaining == 0 and len(self.aliens)==0
             #self.level2_remaining == 0 and
             #self.level3_remaining == 0 and
             #self.level4_remaining == 0
        )
        #TODO: Drop "wave passed" animation and sound effect here.
    

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
             self.game_state = "victory"
        else:
             self.game_state = "between_waves" #put the game state in 'between wave break' for the time determined above.           


    def _update_between_waves(self):
         """this helper function for the _update_game function check if the between wave pause is over yet."""
         if self.next_wave_start_time is None: #once the timer set in _new_wave_pause() is run out,
              
              return
         now = pygame.time.get_ticks()
         if now >= self.next_wave_start_time: #get the time and check if we're ready to spawn (we already know we are)
              for ship in self.players: #first position all player ships toward the bottom of the screen, so they are not where aliens will spawn
                    if ship.rect.bottom <= self.settings.screen_height * 0.9:
                        ship.rect.bottom = int(self.settings.screen_height * 0.9)
                        ship.y = float(ship.rect.y)
              self._new_alien_wave(self.current_wave_num) #CREATE THE NEXT WAVE!
              self.next_wave_start_time = None  
              self.game_state = "playing" #CHANGE GAME STATE TO "PLAYING!"
              #TODO: Drop new wave sound announcement in here
              #TODO: Drop new wave animation in here (get ready text, e.g.)

    def _handle_alien_breaches(self):
         """helper function for the update_game() function to trigger defeat if we let too many aliens through."""
         aliens_breached = []
         for given_alien in self.aliens:
              if given_alien.rect.top > self.settings.screen_height:
                #aliens_breached.append(given_alien)
                #if not aliens_breached
                    if given_alien.level in (1,2,3,4):
                        self.breaches_this_wave += 1 #aliens level 1 - 4 count for a single breach each.
                    if given_alien.level == 5:
                        self.breaches_this_wave += 3 #destroyers are a triple breach - introduces urgency to deal with them.
                    if given_alien.level == 6:
                        self.breaches_this_wave += 4 #cruisers are a quadruple breach
                    if given_alien.level == 7: 
                        self.breaches_this_wave += 5 #laser tankers are a quintuple breach
                    #bombarders never move downscreen; so no need to account for their breachiness.
                    #TODO: Drop breach alert sound and/or animation (screen flash) in here
                    given_alien.kill() #kill the alien once it's off screen and its breach has been registered.
                    if self.breaches_this_wave > self.max_breach_tolerance:
                        self.game_state = "defeat"
                   



    def _draw_screen(self):
        """helper function for Main Game Loop to (re)draw the screen and ships"""
        
        #First a set of ifs to handle changing background screens, and defeat/victory screens.
        bg_ref = None

        if self.game_state == "defeat":
            bg_ref = self.settings.bg_defeat
        elif self.game_state == "victory":
             bg_ref = self.settings.bg_victory
        else:
        
            if self.current_wave_num <= 2:
                bg_ref = self.settings.bg_starter
            elif self.current_wave_num in range (3,5):
                bg_ref = self.settings.bg_3to4
            elif self.current_wave_num in range (5,7):
               bg_ref = self.settings.bg_5to6
            elif self.current_wave_num in range (7,9):
                bg_ref = self.settings.bg_7to8
            elif self.current_wave_num in range (9,11):
                bg_ref = self.settings.bg_9to10
            
            elif bg_ref == None:
                bg_ref = self.settings.bg_starter


        
        self.screen.blit(bg_ref, (0, 0)) #redraw the background
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

        #draw the heads up display:
        self._draw_hud()

        pygame.display.flip() #flip the display

    def _draw_hud(self):  
        """Draws the Heads Up Display for players - inventory, player health, lives remaining, and wave+scoring info"""
        current_wave_text = f"Wave{self.current_wave_num + 1}" if self.current_wave_num is not None else "Wave ?" # tells the program" set the text to display the current wave; unless current wave is none; in which case, and in all other cases; show debut text "Wave ?""
        wave_surf = self.hud_font.render(current_wave_text, True, self.settings.hud_text_color)
        wave_rect = wave_surf.get_rect(center=(self.settings.screen_width // 2, 15))
        self.screen.blit(wave_surf, wave_rect)

            # Player info at bottom
        # Spread across the bottom of the screen
        if self.players:
            hud_y = int(self.settings.screen_height * .97) #place the text of the HUD's 97% toward bottom of screen.

            hud_x_placements = {1:int(self.settings.screen_width * 0.65), 
                               2:int(self.settings.screen_width * 0.35), 
                               3:int(self.settings.screen_width *0.85), 
                               4:int(self.settings.screen_width * 0.15)}
            
            for ship in self.players:
                info = (f"P{ship.player_id}: HP {ship.player_health} | Lives {ship.player_lives} | Lvl {ship.player_level}")
                #having created the variable, render it, antialiased, for display
               
               
                hud_color = getattr(self.settings, f"player{ship.player_id}_hud_color", 
                                    self.settings.hud_text_color #as a fallback option if the first one should fail
                                     )
                hud_x = hud_x_placements.get(ship.player_id)
                
                info_surf = self.hud_font.render(info, True, hud_color)
                #give it a rect
                info_rect = info_surf.get_rect(
                    center=(hud_x, hud_y)
                )
                self.screen.blit(info_surf, info_rect)

if __name__ == "__main__":

    gameinstance = AlienInvasion()
    gameinstance.Main_Game_Loop()


    #https://chatgpt.com/c/69160d6b-b54c-832e-a230-5279c8f6bf65