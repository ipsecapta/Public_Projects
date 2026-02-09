#!/usr/bin/env python3
#
# Project: Final Project
#
# Files needed by this file: 
#       menu_helpers.py (this file)
#       Visintainer_A_Alien_Game.py (main file)
#
# Author: Anthony Visintainer
# Date: 8 December 2025
# 
#
#This file is for the functions that help with the opening menu.

import pygame
import sys

def gamesetup(self, ShipClass): #note that the ship class is passed to this function from the main file, so it can create ship objects for the main file. 
        #first hide the main screen
        self.screen=pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height), flags=pygame.HIDDEN)
        #then begin setup CLI:
        input("Greetings, space cadet! The earth is under fire, and your squadron has been deployed to stave off the invasion for as long as possible."
                "\nPress ENTER to continue.")
        input("You may choose which wave to face for your initial deployment - the higher the number, the more enemies."
              "\nPress ENTER to continue.")

        while self.current_wave_num not in (0,1,2,3,4):
                while True:
                  self.current_wave_num = input("Select a wave number to start on - 1 through 5:   ") #prompt the user for
                  try:                        
                        if int(self.current_wave_num) in (1,2,3,4,5): #check the selected wave number
                            self.current_wave_num = int(self.current_wave_num) #convert the inputted string to an integer so the main function can math with it.
                            break #this kills the subloop, and sends us back to the main loop to be checked: is the current_wave_num now in acceptable range?
                        elif int(self.current_wave_num) not in (1,2,3,4,5):
                            self.current_wave_num = input("That's outside the range you're allowed to pick, Cadet! \nSelect a wave number to start on - 1 through 5:   ")
                  except ValueError: #if something is input that causes ValueError (e.g. a non-number), a more enthusiastic response:
                       print("That's not even an number, space cadet!")
            
                self.current_wave_num -= 1 #increment it down one, so that the index will be called up correctly. 
        print("You may also choose how many members are in your squadron! Choose wisely.")
        while len(self.players) == 0:
                while True:
                    number_players = input("Select a number of players - 1 through 4:   ")
                    try:
                      if int(number_players) in (1,2,3,4):
                        number_players = int(number_players)
                        break
                      elif int(number_players) not in (1,2,3,4):
                        number_players = input("Can you count, cadet? That's not a number 1-4! \n Select a number of players - 1 through 4:   ")
                        
                    except ValueError:
                        print("Not even a valid number, cadet! Are you sure you're in a state to save the world right now?")
                        #last adjustment: set the resizing factor in base_settings.py to fit more on screen depending on how many players there are:
                
                self.settings.multiplayer_resizer = 1-.075*number_players
                print ("Resizer is set to:", self.settings.multiplayer_resizer)
                _apply_player_count(self, number_players, ShipClass) #creates the sprites, given class and number, and adds them to the player group.
      
      
        print(f"Great! All {number_players} of you will start on wave {self.current_wave_num}")
            
        for player in range(1, number_players+1):
                 print(f"Player {player}, your control keys are:") 
                 print (getattr(self.settings, f"p{player}keydesc"),"\n")
        readyornot = input("When ready, type READY and hit enter.")
            
        while readyornot.lower() != "ready":
                 readyornot = input("The world needs saving, cadet! When ready, type READY and hit enter.")

#ADJUSTMENTS TO KEEP MULTIPLAYER FUN:
        #The following adjust the spawning time of aliens so that the more players are, the quicker they spawn.
        self.level2_minspawntime = round(self.settings.alien2_min_spawn_interval - (self.settings.alien2_min_spawn_interval*(len(self.players)*0.15)))
        self.level2_maxspawntime = round(self.settings.alien2_max_spawn_interval - (self.settings.alien2_max_spawn_interval*(len(self.players)*0.15)))
        self.level3_minspawntime = round(self.settings.alien3_min_spawn_interval - (self.settings.alien3_min_spawn_interval*(len(self.players)*0.15)))
        self.level3_maxspawntime = round(self.settings.alien3_max_spawn_interval - (self.settings.alien3_max_spawn_interval*(len(self.players)*0.15)))
        self.level4_minspawntime = round(self.settings.alien4_min_spawn_interval - (self.settings.alien4_min_spawn_interval*(len(self.players)*0.15)))
        self.level4_maxspawntime = round(self.settings.alien4_max_spawn_interval - (self.settings.alien4_max_spawn_interval*(len(self.players)*0.15)))
        self.destroyer_minspawntime = round(self.settings.destroyer_min_spawn_interval - (self.settings.destroyer_min_spawn_interval*(len(self.players)*0.15)))
        self.destroyer_maxspawntime = round(self.settings.destroyer_max_spawn_interval - (self.settings.destroyer_max_spawn_interval*(len(self.players)*0.15)))
        
        #the following adjusts the fleet aliens (level 1 aliens) to have a higher speed based on the number of players.       
        if len(self.players)>1:
            self.settings.fleet_advance_speed += (len(self.players)*.01) #the fleets advance a little faster for each extra player on the screen.
            self.level1_reinforcements_threshhold -= min(30, (5 * len(self.players)))

        #the following adjusts the number of fleet alien rows up by 2 per level for each extra player:
            for wave in self.settings.wave_master_index:
                 wave["rows_level1"] += len(self.players)
        
        #add extra rows visible at wave start for each additional player, to increase difficulty
            self.settings.level1_alien_starting_rows += len(self.players)
            print(f"Starting waves will attempt {self.settings.level1_alien_starting_rows}, and cap at either total lvl1 rows for wave or at 6")           
            
#Next, I thought it would be nice to have a little start screen:         
        self.screen=pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height), pygame.RESIZABLE)#reshow the screen we hid at the start:
        for ship in self.players:
             ship.screen = self.screen #make sure the screen the ships are set to is this new screen
        startscreen = pygame.image.load(self.settings.startscreen_path) #load the startscreen image
        startscreen = pygame.transform.scale(startscreen, (self.settings.screen_width, self.settings.screen_height))#cale it to the screen size
        self.screen.blit(startscreen, (0, 0)) #blit it to the screen.

#START PREGAME PAUSE:     
        pygame.display.flip()#display it in the window

        pregame_pause = True
        while pregame_pause:
             
            for event in pygame.event.get(): #listen for any keystrokes
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN: #if any key is pressed, start the game:
                    self.game_state = "playing"
                    pregame_pause=False
            self.clock.tick(30) # AI recommended this, as it makes the loop wait a little before running again, keeping it from 'running too hot'
    #Once setup is complete, the main game loop will call the display back and start the game.
 
    

def _apply_player_count(self,number_players, ShipClass): #note that the ship class is passed from the menu function down to this function so it can create them:
        """helper function for gamesetup() that acreates player sprites, given class and number, and adds them to the self.players sprite group."""
        for iter in range(1,number_players+1):
            ship_name = (f"p{iter}ship")
            newship = ShipClass(self.settings, self.screen, player_id=iter, player_health=self.settings.player_starting_health, player_lives=self.settings.player_starting_lives, player_level=1) # create player 1 ship
            setattr(self, ship_name, newship) #this is a set attribute command - tinkering around, I wanted to dynamically assign ship names 
                                            #-->AND create the ships in this function, and the best way seemed to be to tell the program:
                                            #"make a variable "ship name"; make a new ship; then create a variable with the name ship_name that 
                                            #accesses the exact same place in memory as the new ship.
                                            #when the loop iterates again, the newship reference to that memory location will be destroyed, 
                                            #but the ship_name reference will be kept. So the object will 'live' under ship_name now.
                                            #Due to python's memory weirdness (or genius, as it were) I can just add new_ship 
                                            #to the sprite group, and the sprite group will then be calling the MEMORY LOCATION of new_ship; 
                                            #and as long as there's at least one reference to that memory location, even if it's not new_ship
                                            #anymore, python can access it by that reference. 
            
            self.players.add(newship)



