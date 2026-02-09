#bullet.py - file to determine bullet logic, and assign different features to different types of bullet.
#For universal bullet settings (speed, colors, width, height, etc) see base_settings.py.
import pygame

class Bullet(pygame.sprite.Sprite): 
    """The Bullet Sprite. I chose to create enough parameters to have just one class, 
        that can be passed different attributes to create different bullets."""
    def __init__(self, settings, screen, 
                 x, y, direction, 
                 owner_type, owner_level=1, owner_ref=None):
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

        self.direction = direction

        #Use if statements to distinguish size differences in types of bullets depending on who fired them:
        if owner_type == "boss": #call up the unique size settings for boss bullets
            width = settings.boss_bullet_width
            height = settings.boss_bullet_height
            self.color = settings.boss_bullet_color

        #use if and elif statements to distinguish bullet colors and speeds:
        elif owner_type == "player":
            width = settings.bullet_width
            height = settings.bullet_height
            self.color = settings.player_bullet_color
            self.speed = settings.bullet_speed
        elif owner_type == "alien" and owner_level == 7: # destroyer bullets are slightly thicker, slower, and whitish purple
            width = settings.destroyer_bullet_width
            height = settings.destroyer_bullet_height
            self.color = settings.destroyerandcruiser_bullet_color
            self.speed = settings.alien_bullet_speed - 0.1
        elif owner_type == "alien" and owner_level == 6: # cruiser bullets are much thicker and much slower
            width = settings.cruiser_bullet_width
            height = settings.cruiser_bullet_height
            self.color = settings.destroyerandcruiser_bullet_color
            self.speed = settings.alien_bullet_speed - 0.25
        elif owner_type == "alien" and owner_level == 5: # lazer tanker bullets are long,thin, red, and faster than other aliens.
            width = settings.laztanker_bullet_width
            height = settings.laztanker_bullet_height
            self.color = settings.laztanker_bullet_color
            self.speed = settings.alien_bullet_speed + 0.25
        elif owner_type == "alien":
            width = settings.alien_bullet_width
            height = settings.alien_bullet_height
            self.color = settings.alien_bullet_color
            self.speed = settings.alien_bullet_speed
        elif owner_type == "boss":
            self.color = settings.boss_bullet_color
            self.speed = settings.boss_bullet_speed
        
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
        #bullets disappear when they leave the screen:
        if self.rect.bottom <0 or self.rect.top > self.settings.screen_height:
            self.kill()
        
    def draw(self): # a draw function, to place the bullet visibly on screen
        pygame.draw.rect(self.screen, self.color, self.rect)
        """>>>EVENTUALLY REPLACE WITH PNG SPRITES THAT GET BLITTED ON TO SCREEN"""