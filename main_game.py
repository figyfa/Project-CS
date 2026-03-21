import pygame
import math
import random
import os

MOVE_COUNTER = 10 #Value used for determining how often the player can move every frame

HYPOTENUSE = 2.121 #Value used to represent the distance the player should move when moving diagonally

pygame.init() #Initialise pygame

pygame.mixer.init() #Initialise the pygame mixer for audio

pygame.mixer.set_num_channels(200000) #Set the number of channels for the audio

debugging = False #Activate or deactivate debugging mode

FPS = 60 #Set the FPS the game will run at
fpsClock = pygame.time.Clock()# Initialise Fps clock
pygame.display.set_caption("Game") # Set title to "Game"

def calc_distance(pointA, pointB):
    """ Method used to calculate the distance between two circles with coordinates and a radius"""
    return math.sqrt((pointA.wcx - pointB.wcx)**2 + (pointA.wcy - pointB.wcy)**2) - pointA.radius - pointB.radius

def calc_distance_circle_and_point(pointA, pointB,world):
    """ Method used to calculate the distance between a circle with a coordinate and radius and a tuple or list of
    size 2 containing coordinates"""
    return math.sqrt((pointA.wcx - pointB[0]-world.camera_follow.cam_cx)**2 + (pointA.wcy - pointB[1] - world.camera_follow.cam_cy)**2) - pointA.radius


class Widget:
    """ The Widget class is an abstract class that represents a single widget on the screen """
    def __init__(self, x, y, width, height, color,text,game):
        self.cx = x
        self.cy = y #The coordinates of the widget on the screen
        self.width = width
        self.height = height #The dimensions of the widget
        self.color = color
        self.text = text # The colour and the text in the widget
        self.active = True # Whether the widget should be drawn on the screen
        self.rect = pygame.Rect(x, y, width, height) # A rectangle that represented the widget's background
        self.font = pygame.font.SysFont('comicsans', 30)
        self.text_color = (0,0,0) # Establish font and colour of text
        self.text_render = self.font.render(self.text, True, self.text_color) # Create a render of the text in the font provided
        self.center_rect = self.text_render.get_rect(center = self.rect.center) # Create a rectangle at the center of the text object
        self.adjustable = False # Determine whether the textbox should be able to be changed by the player
        self.world = game # The game object which the widget is in.
        game.widgets.append(self) # A list containing all widgets.

    def draw(self,screen):
        """ Method used to draw the widget on the screen """
        self.text_render = self.font.render(self.text, True, self.text_color)
        pygame.draw.rect(screen, self.color, self.rect) # Draw a rectangle and blit the text onto the screen at the center rectangle's position
        screen.blit(self.text_render, self.center_rect)

    def execute_command(self):
        """ Virtual method used to execute the command of a button"""
        pass

class BackButton(Widget):
    """ Button used to return from the settings menu back to the main menu """
    def __init__(self, x, y, width, height, color,text,game):
        super().__init__(x,y,width,height,color,text,game)
        self.active = False # Declare back button as initially not active

    def execute_command(self):
        """ Sets all widgets to false and activates the widgets that make up the main menu """
        for button in self.world.widgets:
            button.active = False # Deactivate all buttons

        self.world.settings_open = False # Close settings

        self.world.start_button.active = True # Activate start and settings button
        self.world.settings_button.active = True

class StartButton(Widget):
    """ Button used to start the game """
    def __init__(self, x, y, width, height, color, text,game):
        super().__init__(x, y, width, height, color, text,game)

    def execute_command(self):
        """ Sets all widgets to false, initializes enemies and initializes the world objects """
        self.world.main_menu = False
        self.active = False # Deactivate main menu, and other buttons in the main menu screen
        self.world.settings_button.active = False

        if not self.world.tutorial_selected: # Show laser information on HUD if tutorial is not selected
            self.world.laser_charge_text_box.active = True
            self.world.laser_status_text_box.active = True

        self.world.wave_text_box.active = True # Show the wave counter to player

        self.world.initialize_enemies(int(self.world.enemies_counter.text), int(self.world.viruses_counter.text)) # Create the enemies and viruses

        self.world.initialise_world_objects() # Add the created enemies and viruses to the list of world objects

class RestartButton(Widget):
    """ Button used to restart the game """
    def __init__(self, x, y, width, height, color, text,game):
        super().__init__(x,y,width,height,color,text,game)

    def execute_command(self):
        """ Sets all widgets to false and activates the widgets that make up the main menu and reset key variables"""
        for widget in self.world.widgets:
            widget.active = False # Deactivate all widgets

        self.world.restarted = True # Declare that the world should be restarted


class SettingsButton(Widget):
    """ Button used to enter the settings menu"""
    def __init__(self, x, y, width, height, color, text,game):
        super().__init__(x,y,width,height,color,text,game)

    def execute_command(self):
        """ Deactivates the settings button and call the method to open the settings menu"""
        self.active = False # Deactivate itself and open the settings menu
        self.world.open_settings()

class Plus_button(Widget):
    """ Button used to increment value of parent text box """
    def __init__(self, x, y, width, height, color,text_box,game):
        super().__init__(x,y,width,height,color,"+",game)
        self.text_box = text_box # Denote a parent text box

    def execute_command(self):
        """ Increments the value in parent's text box by 1 """
        self.text_box.text = str(int(self.text_box.text)+1)

class Minus_button(Widget):
    """ Button used to decrement value of parent text box """
    def __init__(self, x, y, width, height, color,text_box,game):
        super().__init__(x,y,width,height,color,"-",game)
        self.text_box = text_box # Denote a parent text box

    def execute_command(self):
        """ Decrements the value in parent's text box by 1 '"""
        if self.text_box.text != "0":
            self.text_box.text = str(int(self.text_box.text)-1)

class Text_box(Widget):
    """ A widget used for the sole purpose of displaying text to the user """
    def __init__(self, x, y, width, height, color,text,adjustable,game):
        super().__init__(x,y,width,height,color,text,game)
        self.adjustable = adjustable
        self.active = False

        # Creates plus and minus buttons either side of it if it is supposed to be adjustable
        if adjustable:
            self.plus_button = Plus_button(x+120, y, width-10, height, color,self,game)
            self.minus_button = Minus_button(x-100, y, width-10, height, color,self,game)
            self.plus_button.active = False # Create a plus and minus button and deactivate them until needed
            self.minus_button.active = False
        else:
            self.plus_button = None # Do not create a plus and minus button if the button is not supposed to be adjustable
            self.minus_button = None

    def update(self,text):
        """ Updates the text in the text box """
        self.text = text


class Island:
    """ Circle representing the playable area """
    def __init__(self,colour, radius, cx, cy,world):
        self.colour = colour
        self.radius = radius
        self.cx = cx
        self.cy = cy # Coordinates on the player's screen
        self.wcx = cx
        self.wcy = cy # Coordinates as to where the object is in the world
        self.world = world # World that the object is in

    def draw(self):
        """ Draws the circle onto the main screen """
        pygame.draw.circle(self.world.screen, (self.colour), (self.cx, self.cy), self.radius)

class Sword:
    """ Used to represent one of the player's weapons """
    def __init__(self):
        self.cx = 0
        self.cy = 0 # Coordinates on the player's screen
        self.wcx = 0
        self.wcy = 0 # Coordinates as to where the sword is in the world
        self.radius = 27
        self.colour = (255,255,255)
        self.xvector = 0 # The vector from the player to their mouse position, which the sword should be drawn along
        self.yvector = 0

    def draw(self,screen):
        """ Draws a circle when the player swings with the sword """
        pygame.draw.circle(screen, (self.colour),(self.cx,self.cy),self.radius)

    def check_hit(self,enemies,world):
        """ Iterates through enemies and stuns any enemy that collide with the sword"""
        for enemy in enemies:
            if calc_distance(enemy,self) <= 0: # Check if any enemies are within the sword's hit-box and stun them
                enemy.take_damage_from_sword(world.sword.xvector,world.sword.yvector) # Pass information regarding in which direction the enemies should be knocked back
                enemy.sword_stunned = True

class Tree:
    """ Class used to represent a tree"""
    def __init__(self,wcx,wcy):
        self.wcx = wcx
        self.wcy = wcy # Coordinates in the game world
        self.cx = wcx
        self.cy = wcy # Coordinates on the player's screen
        self.radius = 20

    def draw(self,screen):
        """ Draw the tree on the screen """
        pygame.draw.rect(screen,(150,75,0),(self.cx-18,self.cy-93,36,115))# Draw a rectangle representing the tree trunk
        pygame.draw.circle(screen,(0,240,20),(self.cx,self.cy-163),72)# Draw a circle representing the tree's leaves
        if debugging:
            pygame.draw.circle(screen,(255,255,255),(self.cx,self.cy),self.radius) # Draw the tree's hit box at its base

class BoundingBox:
    """ Class representing area in which player should move or camera should move"""
    def __init__(self,lx=550,ty=300,width=400,height=250,world=None):
        self.lx = lx
        self.ty = ty # Coordinates of the top left corner of the rectangle on the player's screen
        self.width = width
        self.height = height
        self.s = pygame.Surface((width,height)) # Surface representing the bounding box
        self.screen = world.screen
        self.cam_cx = 0 # Attributes determining how far the player's camera has moved
        self.cam_cy = 0

    def draw(self):
        """ Draws the bounding box on the screen, only used in debugging mode"""
        self.s.set_alpha(128)
        self.s.fill((255,255,255))
        self.screen.blit(self.s,(self.lx,self.ty)) # Draws the bounding box on the screen

    def scan_for_player(self,player):
        """ Checks if there is a player heading inside the bounding box """
        if self.lx < player.hcx and player.hcx < (self.lx + self.width) and self.ty < player.hcy and (self.ty + self.height) > player.hcy:
            player.in_camera = True
            return True # Calculates if the player is in the bounding box and returns True if this is the case
        else:
            player.in_camera = False
            return False # Returns false if the player is not in the bounding box

class Health_bar():
    """ Used to represent the health bar of the player"""
    def __init__(self,world):
        self.cx = 5
        self.cy = (world.screen.get_height()-65) # Coordinates of the health bar on the player's screen
        self.width = 200
        self.height = 50 # Width and height of the health bar

    def draw(self,screen,world):
        """ Draws the health bar on the screen """
        pygame.draw.rect(screen,(0,0,0),(self.cx,self.cy,self.width,self.height))
        pygame.draw.rect(screen,(255,0,0),(self.cx,self.cy,self.width-((1-world.player.health/100)*self.width),self.height))
        # Draws the health bar onto the screen

class Player:
    """ Class representing the player """
    def __init__(self,cx,cy,world):
        self.cx = cx
        self.cy = cy # Coordinates of the player in the game world
        self.vy = 3
        self.vx = 3 # Velocity of the player in the x and y direction
        self.in_camera = True # Whether the player is in the camera or not
        self.hcx = cx
        self.hcy = cy # The coordinates of where the player is heading, based on their mouse inputs
        self.radius = 25 # Radius of the player
        self.sprinting = 1 # Multiplier to the player's speed (increased to 2 when the player is sprinting)
        self.max_health = 100 # Max health of the player
        self.health = 100 # Current health of the player
        self.colour = (0,0,0) # Colour of the player
        self.laser_trail = [] # List containing the hit-boxes generated by the laser

        self.wcx = cx # Player's coordinates in the world
        self.wcy = cy

        self.world = world # World that the player is in

        self.laser_charge = 0 # Current charge of the laser and whether the player is firing it
        self.firing_laser = False

        #For collision (coordinates of the 8 walking spots of the player)
        self.left = (0,0)
        self.up = (0,0)
        self.right = (0,0)
        self.down = (0,0)
        self.upleft = (0,0)
        self.upright = (0,0)
        self.downleft = (0,0)
        self.downright = (0,0)
        self.walking_spots = [self.left,self.right,self.down,self.up,self.upleft,self.downleft,self.downright,self.upright]
        self.collision_radius = 5

        self.left_walkable = True # Whether the walking spots are detecting obstacles (i.e. not walkable) or not detecting obstacles (i.e. walkable)
        self.right_walkable = True
        self.down_walkable = True
        self.up_walkable = True
        self.downleft_walkable = True
        self.downright_walkable = True
        self.upright_walkable = True
        self.upleft_walkable = True

        # List containing the permissions of the 8 walking spots
        self.walking_spot_permissions = [self.left_walkable,self.right_walkable,self.down_walkable,self.up_walkable,self.upleft_walkable,self.downleft_walkable,self.downright_walkable,self.upright_walkable]


    def check_walkable(self,trees):
        """ Checks to see if player is colliding with any trees """
        for i in range(len(trees)):
            for j in range(len(self.walking_spots)):
                if calc_distance_circle_and_point(trees[i],self.walking_spots[j],self.world) <= self.collision_radius:
                    self.walking_spot_permissions[j] = False # If a walking spot is colliding with a tree, flag that walking spot as unwalkable (i.e. False)

        for i in range(len(self.walking_spots)):
            if calc_distance_circle_and_point(self.world.island,self.walking_spots[i],self.world) >= self.collision_radius:
                self.walking_spot_permissions[i] = False # Set walking spot to false if the player is not on the island

        self.left_walkable = self.walking_spot_permissions[0]
        self.right_walkable = self.walking_spot_permissions[1]
        self.down_walkable = self.walking_spot_permissions[2]
        self.up_walkable = self.walking_spot_permissions[3]
        self.upleft_walkable = self.walking_spot_permissions[4]
        self.downleft_walkable = self.walking_spot_permissions[5]
        self.downright_walkable = self.walking_spot_permissions[6]
        self.upright_walkable = self.walking_spot_permissions[7]
        # Set each attribute to its corresponding walking spot permission in the list

    def move_up(self,in_camera):
        """Handle movement upwards"""
        if in_camera:
            move_ticker = MOVE_COUNTER
            self.hcy -= self.vy * self.sprinting
            self.wcy -= self.vy * self.sprinting
            return move_ticker
        else:
            move_ticker = MOVE_COUNTER
            self.hcy -= self.vy * 10
            self.world.camera_follow.cam_cy -= self.vy * self.sprinting
            self.wcy -= self.vy * self.sprinting
            return move_ticker

    def move_up_and_right(self,in_camera):
        """Handle movement upwards and to the right"""
        if in_camera:
            self.hcx += HYPOTENUSE * self.sprinting
            self.hcy += (self.vy - HYPOTENUSE) * self.sprinting
            self.wcx += HYPOTENUSE * self.sprinting
            self.wcy += (self.vy - HYPOTENUSE) * self.sprinting
        else:
            self.hcx += HYPOTENUSE * 10
            self.hcy += (self.vy - HYPOTENUSE) * 10
            self.world.camera_follow.cam_cx += HYPOTENUSE * self.sprinting
            self.world.camera_follow.cam_cy += (self.vy-HYPOTENUSE) * self.sprinting
            self.wcx += HYPOTENUSE * self.sprinting
            self.wcy += (self.vy-HYPOTENUSE) * self.sprinting

    def move_up_and_left(self,in_camera):
        """Handle movement upwards and to the left"""
        if in_camera:
            self.hcx -= HYPOTENUSE * self.sprinting
            self.hcy += (self.vy-HYPOTENUSE) * self.sprinting
            self.wcx -= HYPOTENUSE * self.sprinting
            self.wcy += (self.vy-HYPOTENUSE) * self.sprinting
        else:
            self.hcx -= HYPOTENUSE * 10
            self.hcy += (self.vy-HYPOTENUSE) * 10
            self.world.camera_follow.cam_cx -= HYPOTENUSE * self.sprinting
            self.world.camera_follow.cam_cy += (self.vy-HYPOTENUSE) * self.sprinting
            self.wcx -= HYPOTENUSE * self.sprinting
            self.wcy += (self.vy-HYPOTENUSE) * self.sprinting

    def move_down(self,in_camera):
        """Handle movement downwards"""
        if in_camera:
            move_ticker = MOVE_COUNTER
            self.hcy += self.vy * self.sprinting
            self.wcy += self.vy * self.sprinting
            return move_ticker
        else:
            move_ticker = MOVE_COUNTER
            self.hcy += self.vy * 10
            if self.world.camera_follow.scan_for_player(self):
                self.move_down(True)
            self.world.camera_follow.cam_cy += self.vy * self.sprinting
            self.wcy += self.vy * self.sprinting
            return move_ticker

    def move_down_and_left(self,in_camera):
        """Handle movement downwards and to the left"""
        if in_camera:
            self.hcx -= HYPOTENUSE * self.sprinting
            self.hcy -= (self.vy-HYPOTENUSE) * self.sprinting
            self.wcx -= HYPOTENUSE * self.sprinting
            self.wcy -= (self.vy-HYPOTENUSE) * self.sprinting
        else:
            self.hcx -= HYPOTENUSE * 10
            self.hcy -= (self.vy-HYPOTENUSE) * 10
            self.world.camera_follow.cam_cx -= HYPOTENUSE * self.sprinting
            self.world.camera_follow.cam_cy -= (self.vy-HYPOTENUSE) * self.sprinting
            self.wcx -= HYPOTENUSE * self.sprinting
            self.wcy -= (self.vy-HYPOTENUSE) * self.sprinting

    def move_down_and_right(self,in_camera):
        """Handle movement downwards and to the right"""
        if in_camera:
            self.hcx += HYPOTENUSE * self.sprinting
            self.hcy -= (self.vy-HYPOTENUSE) * self.sprinting
            self.wcx += HYPOTENUSE * self.sprinting
            self.wcy -= (self.vy-HYPOTENUSE) * self.sprinting
        else:
            self.hcx += HYPOTENUSE * 10
            self.hcy -= (self.vy-HYPOTENUSE) * 10
            self.world.camera_follow.cam_cx += HYPOTENUSE * self.sprinting
            self.world.camera_follow.cam_cy -= (self.vy-HYPOTENUSE) * self.sprinting
            self.wcx += HYPOTENUSE * self.sprinting
            self.wcy -= (self.vy-HYPOTENUSE) * self.sprinting

    def move_left(self,in_camera):
        """Handle movement left"""
        if in_camera:
            move_ticker = MOVE_COUNTER
            self.hcx -= self.vx * self.sprinting
            self.wcx -= self.vx * self.sprinting
            return move_ticker
        else:
            move_ticker = MOVE_COUNTER
            self.hcx -= self.vx * 10
            self.world.camera_follow.cam_cx -= self.vx * self.sprinting
            self.wcx -= self.vx * self.sprinting
            return move_ticker
    def move_right(self,in_camera):
        """Handle movement right"""
        if in_camera:
            move_ticker = MOVE_COUNTER
            self.hcx += self.vx * 10
            self.wcx += self.vx * self.sprinting
            return move_ticker
        else:
            move_ticker = MOVE_COUNTER
            self.hcx += self.vx * 10
            check = self.world.camera_follow.scan_for_player(self)
            if check:
                self.move_right(check)
            self.world.camera_follow.cam_cx += self.vx * self.sprinting
            self.wcx += self.vx * self.sprinting
            return move_ticker

    def draw(self,screen):
        """ Draws the player onto the screen, if debugging mode is enabled, draws each of the player's walking spots as well"""
        pygame.draw.circle(screen, self.colour, (self.cx, self.cy),self.radius)
        if debugging:
            pygame.draw.circle(screen,(34,123,35),self.left,self.collision_radius)
            pygame.draw.circle(screen,(34,123,35),self.up,self.collision_radius)
            pygame.draw.circle(screen,(34,123,35),self.right,self.collision_radius)
            pygame.draw.circle(screen,(34,123,35),self.down,self.collision_radius)
            pygame.draw.circle(screen,(34,123,35),self.downright,self.collision_radius)
            pygame.draw.circle(screen,(34,123,35),self.upright,self.collision_radius)
            pygame.draw.circle(screen,(34,123,35),self.upleft,self.collision_radius)
            pygame.draw.circle(screen,(34,123,35),self.downleft,self.collision_radius)
    def update_health(self):
        """ Handles the game ending sequence and player colour depending on their health """
        if self.health > 0:
            self.colour = (0,255 * (self.max_health - self.health)/self.max_health,0)
            return False # Returns False if the player is alive, (main menu should not be activated)
        else:
            for widget in self.world.widgets:
                widget.active = False
            return True # Returns True if the player is dead, (main menu should be activated if played has died)
    def fire_laser(self):
        """ Uses the mouse position and the player position to create a line of hitboxes that check and damage enemies"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] + self.world.camera_follow.cam_cx, mouse_pos[1] + self.world.camera_follow.cam_cy)
        # Determine the world coordinates of the mouse position
        magnitude = math.sqrt((mouse_pos[0] - self.wcx)**2 + (mouse_pos[1] - self.wcy)**2)
        self.xstep = ((mouse_pos[0] - self.wcx)/magnitude) * 20
        self.ystep = ((mouse_pos[1] - self.wcy)/magnitude) * 20
        # Calculate the vector between the player and the mouse position
        self.current_bulletx = self.wcx
        self.current_bullety = self.wcy
        # Initialise the first hit-box
        self.laser_trail.append((self.current_bulletx,self.current_bullety))
        # Append the hit-box to the list
        if self.xstep > 0:
            while self.current_bulletx < mouse_pos[0]:
                self.current_bulletx += self.xstep
                self.current_bullety += self.ystep
                self.laser_trail.append((self.current_bulletx,self.current_bullety))
        else:
            while self.current_bulletx > mouse_pos[0]:
                self.current_bulletx += self.xstep
                self.current_bullety += self.ystep
                self.laser_trail.append((self.current_bulletx,self.current_bullety))

        # Depending on whether the player's mouse position is less than or greater than the player's current position, create a hit-box at
        # each "step" and increment the coordinates for the next hit-box. Keep placing hit-boxes until the current hit-box
        # has surpassed the player's mouse position

        if debugging:
            for circle in self.laser_trail:
                pygame.draw.circle(self.world.screen, (123,123,123), (circle[0]-self.world.camera_follow.cam_cx,circle[1]-self.world.camera_follow.cam_cy),5)
        else:
            pygame.draw.line(self.world.screen, (11, 3, 252), (self.cx,self.cy),(self.laser_trail[-1][0]-self.world.camera_follow.cam_cx,self.laser_trail[-1][1]-self.world.camera_follow.cam_cy),10)

        #Draw each individual circular hit-box if debugging is enabled, otherwise, draw a line from the player to the last hit-box generated

    def check_laser_hit(self,enemies):
        """ Checks if any enemies are touching the laser's hitboxes and damages them accordingly """
        for enemy in enemies:
            for circle in self.laser_trail:
                circle = (circle[0]-self.world.camera_follow.cam_cx,circle[1]-self.world.camera_follow.cam_cy)
                if calc_distance_circle_and_point(enemy,circle,self.world) < 0:
                    enemy.health -= 5
        self.laser_trail = []

        # Compare each enemy's world position with each hit-box's world position, and damage the enemy if they are colliding

    def update_position(self):
        """ Sets the player's camera coordinates to their world coordinates - the offset the camera has moved """
        self.cx = self.wcx - self.world.camera_follow.cam_cx
        self.cy = self.wcy - self.world.camera_follow.cam_cy # Determine correct coordinates the player should be drawn on the screen at, given their world coordinates and the camera offset
        if self.in_camera: # Set player's heading coordinates to their current position, so that they can be detected moving back into bounding box
            self.hcx = self.cx
            self.hcy = self.cy

    def decrease_laser_charge(self):
        """ Decrements the laser's charge by 20 every second"""
        if self.world.frames % (FPS/20) == 0:
            self.laser_charge -= 1

    def increase_laser_charge(self):
        """ Increments the laser charge by 1 every second"""
        if self.world.frames % FPS == 0:
            self.laser_charge += 1

class Target:
    """ Class used to represent a target object, which is a small circle in the world at a point"""
    def __init__(self,wcx,wcy, world):
        self.world = world # World the target is in
        self.cx = wcx + world.camera_follow.cam_cx
        self.cy = wcy + world.camera_follow.cam_cy # Coordinate of target on player's camera
        self.wcx = wcx
        self.wcy = wcy # Coordinates of the target in the game world
        self.radius = 5
        self.health = 100 # radius and health of target
        world.targets.append(self) # Add itself to a list of all targets in the world.

    def draw(self,screen):
        """ Draws the circle onto the main screen, only called when debugging mode is enabled """
        pygame.draw.circle(screen, (255,123,123), (int(self.cx),int(self.cy)),self.radius)

class Enemy:
    """ Class representing an enemy in the game world """
    def __init__(self,cx,cy,id,world):
        self.type = "e"
        self.id = id # Type and id of enemy
        self.cx = cx # Coordinates of enemy on player screen
        self.cy = cy
        self.radius = 25 # Radius of enemy
        self.wcx = cx # Coordinates of enemy in the game world
        self.wcy = cy
        self.vx = 0 # Speed of the enemy in each direction
        self.vy = 0
        self.velocity = 3 # Magnitude of the enemy's velocity
        self.health = 100 # Health of enemy
        self.colour = (255,255,255) # Colour of enemy
        self.can_move = 1 # Multiplier of enemy's speed, set to 0 when enemy shouldn't be able to move
        self.enemies_nearby = 0 # Number of enemies nearby
        self.last_hit_time = -1 # Time since enemy last dealt damage to player
        self.image_list = [] # List of image objects that represent the enemy
        self.sword_stunned = False # Whether the enemy has been stunned by a sword
        self.sword_target = Target(self.wcx,self.wcy,world) # A target that determines where the enemy should move to once hit by the sword
        self.world = world # The world the enemy is in
        self.world.objects.append(self.sword_target)
        self.initialised = False # Variable used for determining if the enemy has been sword stunned on this frame, or if they had been sword stunned in previous frames
        for i in range(10):
            imp = pygame.image.load(f"./image/virus_death0{i}.png").convert_alpha()
            imp.set_colorkey((0, 0, 0))
            imp.convert_alpha()
            self.image_list.insert(0,imp) #Set up the list of images of enemy sprite

    def take_damage_from_sword(self,sword_xvector,sword_yvector):
        """ Creates a sword target behind the enemy in the direction of the sword vector and removes 30 health from
        the enemy"""
        self.health -= 30 # Damage enemy
        self.sword_target.wcx = self.wcx + sword_xvector *1000 # Move target in direction of sword vector
        self.sword_target.wcy = self.wcy + sword_yvector *1000
        if self.health <= 0: # Credit laser charge to player
            self.world.player.laser_charge += 5
            if self.world.player.laser_charge > 100:
                self.world.player.laser_charge = 100

    def recover_from_sword(self):
        """ Waits until the enemy has been stunned for half a second, then declares the enemy as no longer being
        stunned by the sword """
        if self.initialised == False:
            self.current_time = self.world.seconds + 0.5
            self.initialised = True
        if self.world.seconds > self.current_time: # Check if 0.5 seconds has elapsed, if so, the enemy is no longer sword stunned
            self.initialised = False
            self.sword_stunned = False


    def evaluate_health(self):
        """ If an enemy is defeated, it is removed from the list of enemies in the game world """
        if self.health <= 0:
            self.can_move = 0 # Remove enemies ability to move
            if self in self.world.enemies: # Remove enemy from list of enemies if it has died
                self.world.enemies.remove(self)
                self.world.enemies_defeated_count += 1
                self.world.regular_enemy_defeated_count += 1

    def scan_for_friendlies(self,enemies):
        """ Detects how many enemies are nearby each frame """
        self.enemies_nearby = 0
        for enemy in enemies: # Scan for nearby enemies and increment number accordinly
            if calc_distance(self,enemy) < 5 and enemy.health > 0:
                self.enemies_nearby += 1


    def draw(self,screen):
        """ Draws the enemy and its sprite onto the main screen """
        if 100 >= (self.health) >= 1:
            self.colour = (255, 255 * (self.health / 100), 255) # Draw enemy onto screen, with the colour of its hit-box proportional to its health
            screen.blit(self.image_list[self.health // 11], (self.cx - 32, self.cy - 32)) # Blit image of enemy onto screen
        if debugging:
            pygame.draw.circle(screen, self.colour, (self.cx, self.cy),self.radius) # Draw enemy hit-box if debugging

    def beeline(self,target):
        """ Has the enemy move towards a general target with cx and cy attributes, and damage that target """
        angle = math.pi

        if target.cx - self.cx != 0:
            angle = math.atan((target.cy - self.cy)/(target.cx - self.cx)) # Determine angle between horizontal and player from the enemy

        self.vx = -self.velocity * math.cos(angle) # Determine x and y components of enemy velocity
        self.vy = -self.velocity * math.sin(angle)

        if self.cx > target.cx:
            self.wcx += self.vx * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
            self.wcy += self.vy * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
        else:
            self.wcx -= self.vx * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
            self.wcy -= self.vy * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
        # Multiply velocity vector by (1 + (number of nearby enemies) * 0.2), causing the enemy to speed up when other enemies are nearby it
            
        # Apply vector to enemies coordinates, moving them towards the target specified in the argument

        if calc_distance(self,target) < 10 and self.health > 0:
            if self.world.seconds > (self.last_hit_time + 0.7):
                target.health -= 2
                self.last_hit_time = self.world.seconds
                # Deal damage to the target if the enemy is within proximity of it


class Virus(Enemy):
    """ Class used to represent a virus type enemy in the game world """
    def __init__(self,enemy_id,world):
        super().__init__(random.randint(0,500),random.randint(0,500),enemy_id,world)
        self.target = Target(0,0,world)
        self.clone_cooldown = 0 # Cooldown representing the time between creating copies of enemies
        self.colour = (255,0,0) # Colour of virus
        self.deciding_where = False # Whether the virus is decided where to move
        self.type = "v" # Type of enemy
        self.counter = 0 # Counting how long the virus should move before changing direction
        self.velocity = 1 # Velocity of virus
    def draw(self,screen):
        """ Draws a circle representing the virus onto the main screen """
        pygame.draw.circle(screen, self.colour, (self.cx, self.cy),self.radius)

    def evaluate_health(self):
        """ Checks to see if the virus is alive, changing its colour to represent its health, and removing it from the list
        of enemies if the virus has no more health """
        if 100 >= (self.health) >= 1:
            self.colour =(self.colour[0],255 * (self.health / 100),self.colour[2])
        if self.health <= 0:
            self.can_move = 0
            if self in self.world.enemies:
                # Remove enemy from list of enemies
                self.world.enemies.remove(self)
                self.world.enemies_defeated_count += 1
                self.world.viruses_defeated_count += 1

    def clone_if_can(self,enemies,enemy_id):
        """ If the cooldown for cloning is less than 0, a regular enemy is created at the viruses location """
        if self.clone_cooldown <= 0:
            self.clone_cooldown = 5
            enemies.insert(0,Enemy(self.wcx,self.wcy,enemy_id,self.world))
            enemy_id += 1
            self.world.objects.append(enemies[0])
            #Create an enemy if the clone_cooldown is 0

        return enemy_id

    def decrement_cooldown(self):
        """ Decreases the cloning ability cooldown for the viruses """
        self.clone_cooldown -= (1/FPS)


class Grenade_v2:
    """ Class used to represent a grenade object, which is thrown by the player and damages anything in a radius
    around it """
    def __init__(self,world):
        self.world = world # World the grenade is in
        self.cx = 0
        self.cy = 0 # Coordinates of the grenade on the player's screen
        self.radius = 100 # Blast radius of the grenade
        self.actual_radius = 5 # Radius of the grenade object
        self.detonation_time = 3 # Time before the grenade detonates
        self.colour = (123,123,123) # Colour of grenade
        self.exploded = False # Whether the grenade has exploded
        self.thrown = False # Whether the grenade has been thrown
        self.dx = 0
        self.dy = 0 # Vector the grenade should move by when thrown
        self.target = (0,0) # Target where the grenade should move towards

    def cook(self):
        """ Decrement the fuse timer on the grenade while it is being held """
        self.cx = self.world.player.cx
        self.cy = self.world.player.cy
        self.wcx = self.world.player.wcx
        self.wcy = self.world.player.wcy # Set coordinates to the player's position
        self.detonation_time -= (1/FPS)
        pygame.draw.circle(self.world.screen, self.colour, (self.cx, self.cy),self.actual_radius)
        if self.detonation_time <= 0:
            self.explode() # Explode itself if the fuse time reaches 0

    def throw(self,player,target=(0,0)):
        """ have the grenade move towards the player's mouse position"""
        if not self.thrown:
            self.wcx = player.wcx
            self.wcy = player.wcy
            self.thrown = True
            self.dy = target[1] - self.wcy
            self.dx = target[0] - self.wcx
            # Calculate the vector the grenade must move by

            self.world.grenades_launched_count += 1 # Increment grenades launched tracker

            magnitude = math.sqrt((self.dx ** 2) + (self.dy ** 2))
            self.dy = (self.dy / magnitude) * 5
            self.dx = (self.dx / magnitude) * 5

            self.target = (target[0],target[1]) # Initialise target attribute with the target argument given

        pygame.draw.circle(self.world.screen, self.colour, (self.cx,self.cy),self.actual_radius)
        self.dy = self.dy * 0.99
        self.dx = self.dx * 0.99 # Slowly decelerate the grenade over time
        self.detonation_time -= (1/FPS)
        if self.detonation_time <= 0:
            self.thrown = False
            self.explode() # Explode grenade if detonation time has elapsed
        for i in range(len(self.world.enemies)):
            if calc_distance(self,self.world.enemies[i]) < -95 and player.health > 0:
                self.thrown = False
                self.explode() # Explode if grenade collides with enemy
        for i in range(len(self.world.trees)):
            if calc_distance(self,self.world.trees[i]) < -95 and player.health > 0:
                self.thrown = False
                self.explode() # Explode if grenade collides with tree hit-box

        self.wcx += self.dx
        self.wcy += self.dy
        self.cx += self.dx
        self.cy += self.dy
        # Update grenades position by adding movement vector

        return target

    def explode(self):
        """ Have the grenade explode, damaging anything around it """
        pygame.mixer.find_channel(True).play(self.world.grenade_explosion)
        self.exploded = True
        pygame.draw.circle(self.world.screen, self.colour, (self.cx, self.cy), self.radius)
        # Draw a circle representing the grenade's blast
        for enemy in self.world.enemies:
            if calc_distance(self, enemy) < 0:
                enemy.health = enemy.health - 30
                if enemy.health <= 0:
                    self.world.player.laser_charge += 5
                    if self.world.player.laser_charge > 100:
                        self.world.player.laser_charge = 100

        #Check if any enemies are in blast radius and damage accordingly, credit player laser charge if an enemy dies
        if calc_distance(self, self.world.player) < 0:
            self.world.player.health = self.world.player.health - 30
        # Damage the player if they are in the blast radius

class Bullet_trail:
    """ Class used to represent the player's main weapon """
    def __init__(self,world):
        self.world = world # World the gun is in
        self.cx = 0 # Coordinates of the gun on the player's screen
        self.cy = 0
        self.radius = 5 # Radius of each hit-box
        self.color = (125,125,125) # Colour of each hit-box
        self.bullet_trail = [] # List holding each hit-box generated by the gun
        self.deadly_bullet = () # The bullet hit-box which first collides with an enemy
        self.current_bulletx = 0 # The current bullet hit-box to be added to the list
        self.current_bullety = 0
        self.fire_rate = 0 # How often the gun can be fired.

    def check_hit(self, enemies):
        """ Checks to see if there is anything colliding with the bullet hitboxes in the bullet_trail list """
        found = False
        index = 0
        got_hit_this_frame = False
        while not found and index < len(self.bullet_trail):
            # Iterate through each enemy and check if they have collided with each bullet

            for i in range(len(enemies)-1,-1,-1):
                if (calc_distance_circle_and_point(enemies[i], self.bullet_trail[index],self.world) <= 0 and got_hit_this_frame == False):
                    enemies[i].health -= 20 # Damage enemy hit by bullet
                    if enemies[i].health <= 0:
                        self.world.player.laser_charge += 5 # Credit laser charge to the player if the enemy is killed
                        if self.world.player.laser_charge > 100:
                            self.world.player.laser_charge = 100 # Make sure the laser charge cannot go above 100%

                    found = True # Stop searching for a collision
                    self.deadly_bullet = self.bullet_trail[index]
                    got_hit_this_frame = True # Declare that the enemy has got hit (so that no further bullet hit-boxes can damage the enemy)

            for i in range(len(self.world.trees)-1,-1,-1):
                if calc_distance_circle_and_point(self.world.trees[i],self.bullet_trail[index],self.world) <= 0:
                    found=True
                    self.deadly_bullet = self.bullet_trail[index]
                    got_hit_this_frame = True
                    # Check if the bullet hit-box is colliding with a tree, and if so, stop searching the additional bullet hit-boxes for collisions

            else:
                index += 1
                # Increment which bullet should be searched next
        try:
            if not found:
                self.deadly_bullet = self.bullet_trail[-1] # Set last bullet in the list to the deadly bullet if no collisions are detected.
        except:
            self.deadly_bullet = (0,0) #Set deadly bullet coordinates to (0,0) in case the bullet_trail list is empty

    def create_shot(self,player,destination,fire_rate):
        """ Creates a list of bullet hit-boxes based on the player location and their mouse position"""
        self.world.shots_fired_count += 1
        if self.fire_rate <= 0:
            # Calculate vector between player and target destination argument
            self.fire_rate = fire_rate
            magnitude = math.sqrt((destination[0] - player.cx) ** 2 + (destination[1] - player.cy) ** 2)
            self.xstep = ((destination[0] - player.cx) / magnitude) * 20
            self.ystep = ((destination[1] - player.cy) / magnitude) * 20
            self.current_bulletx = player.cx
            self.current_bullety = player.cy
            self.bullet_trail.append((self.current_bulletx, self.current_bullety)) # Append the bullet hit-box to the list of hit-boxes

            for i in range(20):
                # Create a hit-box every step of the vector
                self.current_bulletx += self.xstep
                self.current_bullety += self.ystep
                self.bullet_trail.append((self.current_bulletx, self.current_bullety))
    def decrement_cooldown(self,fire_rate):
        """ Decreases the cooldown on the creation of a bullet trail """
        self.fire_rate = self.fire_rate - (1/FPS)


    def draw(self, player, screen):
        """Draws the bullet trail onto the main screen, if debugging mode is enabled, the indvidual bullet hitboxes are drawn instead """
        if debugging:
            for bullet in self.bullet_trail:
                pygame.draw.circle(screen, (123,123,123), (bullet[0],bullet[1]), 3)
        else:
            pygame.draw.line(screen,(238, 255, 0),(player.cx,player.cy),(self.deadly_bullet[0],self.deadly_bullet[1]),4)

    def clean_shot(self):
        """ Empty the bullet trail list """
        self.bullet_trail = []


class GameWorld:
    """ Class representing the game world """
    def __init__(self):
        self.screen = pygame.display.set_mode((1500, 900))
        self.menu_screen = pygame.Surface((1500, 900))
        # Initialise the menu screen, and the screen where the gameplay would take place

        self.seconds_passed = 0
        self.current_time_wave_ended = 0 # Variables used to record the time at which an event has happened and how many seconds have passed since the event occurred
        self.initializing_next_wave = True # Variable used to handle code which should be called only one when the wave has just ended
        self.objects = [] # The list of all objects in the game world, used to make sure they are drawn correctly on the player's screen based on the player's camera offset
        self.keys = pygame.key.get_pressed() # The list storing which keys have been pressed
        self.player = Player(600,300,self) # The player object in the game world
        self.sword = Sword() # The player's sword
        self.island = Island((0, 255, 60,50),1000,750,450,self)#The object representing the island in the game world.
        self.enemies = [] # The list which stores all enemies, including regular enemies and viruses
        self.viruses = [] # The list containing all the viruses
        self.current_enemy_id = 0 # The current enemy id, incremented by one every time an enemy is created, gives each enemy a unique id
        self.trees = [Tree(random.randint(-200,1550),random.randint(-350,1250)) for i in range(15)] # A list of tree objects randomly generated at random places
        self.targets = [] # A list containing all the targets in the game world
        self.key_g_held_down = False
        self.key_g_not_pressed = True # Two booleans holding the value of whether the G key is being held down, and whether the G key is not being pressed (useful for detecting when the G key is both pressed and released)
        self.active_grenades = [] # A list containing the active grenades in the world
        self.camera_follow = BoundingBox(world=self) # A BoundingBox object representing the region in which the player should move with the world stationary on the screen. Or if the player should remain still and the world should move around them instead
        self.health_bar = Health_bar(self) # A health bar object representing how much health the player has on the player's screen
        self.current_wave = 1 # The current wave the game is on
        self.victory = False # Whether the player has won or not

        self.widgets = [] # A list of all widgets in the game
        self.active_widgets = [] # A list of all the active widgets in the game, (active widgets should be drawn on the screen and active button widgets can be interacted with by the player)


        self.laser_charge_text_box = Text_box(600,750,300,100,(255,255,255),str(self.player.laser_charge)+"%",False,self)
        self.laser_status_text_box = Text_box(600,850,300,50,(255,255,255),"Laser not ready",False,self)
        # Two text box objects representing the player's laser charge on the screen and the status of the player's laser

        self.frames = 0
        self.seconds = 0 # Attributes representing the number of seconds and number of frames that have passed since the start of thegame
        self.bullet_system = Bullet_trail(self) # A Bullet_trail object representing the player's gun

        self.gunshot = pygame.mixer.Sound(os.path.join('sounds','Gunshot.wav'))
        self.gunshot.set_volume(0.1)
        self.sword_sfx = pygame.mixer.Sound(os.path.join('sounds','sword_swing.wav'))
        self.sword_sfx.set_volume(0.1)
        self.grenade_explosion = pygame.mixer.Sound(os.path.join('sounds','Grenade_sound.wav'))
        self.grenade_explosion.set_volume(0.1)
        self.laser_sfx = pygame.mixer.Sound(os.path.join('sounds','energy_beam.wav'))
        self.laser_sfx.set_volume(0.1)
        # Various sound effects used throughout the game

        self.ss = pygame.mixer.Sound(os.path.join('sounds', 'SneSni.wav'))
        self.am = pygame.mixer.Sound(os.path.join('sounds', 'AMis.wav'))
        self.fad = pygame.mixer.Sound(os.path.join('sounds', 'FluaDuc.wav'))
        self.qd = pygame.mixer.Sound(os.path.join('sounds', 'QuiDog.wav'))
        self.SoTI = pygame.mixer.Sound(os.path.join('sounds', 'SoTI.wav'))
        self.music_played = False
        # The soundtracks that play throughout the game

        self.running = True
        self.main_menu = True
        self.tutorial_selected = True
        # Booleans declaring whether the game is running, whether the player is in the main_menu, and whether the player wants to play the tutorial

        self.start_button = StartButton(450,600,300,100,(255,255,255),"start",self)
        # Button object used to start the game

        self.settings_button = SettingsButton(850,600,300,100,(255,255,255),"settings",self)
        self.settings_open = False
        # Button used to open the settings menu

        self.restart_button = RestartButton(1050,350,370,100,(255,255,255),"click here to restart",self)
        self.restart_button.active = False
        self.restarted = False
        # Button used to restart the game

        self.enemies_text_box = Text_box(450,300,300,75,(255,255,255),"enemies",False,self)
        self.enemies_counter = Text_box(550,400,100,50,(255,255,255),"1",True,self)
        # Text box and adjustable counter allowing the player to change the number of enemies on wave 1

        self.viruses_text_box = Text_box(450,500,300,75,(255,255,255),"viruses",False,self)
        self.viruses_counter = Text_box(550,600,100,50,(255,255,255),"0",True,self)
        # Text box representing number of viruses that should spawn on wave one, able to be adjusted by the player in the settings menu

        self.back_button = BackButton(50,50,100,70,(255,255,255),"<",self)
        # Button allowing the player to return to the original main menu from the settings menu

        self.congrats = Text_box(450,100,200,100,(255,255,255),"congrats",False,self)
        # A test box congratulating the player (shown upon reaching wave 10)

        self.you_lose = Text_box(450,100,200,100,(255,255,255),"you lose",False,self)
        # A text box telling the player they have lost (shown upon player death)

        self.enemies_defeated = Text_box(450,200,500,100,(255,255,255),"Total enemies defeated: 0",False,self)
        self.enemies_defeated_count = 0
        # A text box showing how many enemies have died since the game began

        self.grenades_launched = Text_box(450,300,500,100,(255,255,255),"Grenades launched: 0",False,self)
        self.grenades_launched_count = 0
        # A text box showing how many grenades have been launched since the game began

        self.viruses_defeated = Text_box(450,400,500,100,(255,255,255),"Viruses defeated: 0",False,self)
        self.viruses_defeated_count = 0
        # A text box showing how many viruses were defeated since the game began

        self.regular_enemies_defeated = Text_box(450, 500, 500, 100, (255, 255, 255), "Regular enemies defeated: 0", False, self)
        self.regular_enemy_defeated_count = 0
        # A text box recording how many regular enemies have been defeated

        self.shots_fired = Text_box(450,600,500,100,(255,255,255),"Shots fired: 0",False,self)
        self.shots_fired_count = 0
        # Text box recording how many shots the player has fired with their gun since the start of the game

        self.waves_reached = Text_box(450,700,500,100,(255,255,255),"Wave reached: 1",False,self)
        # A text box showing how many wave the player reached before they died (Only showed on game loss)

        self.wave_text_box = Text_box(50,25,250,50,(255,255,255),"wave 1",False,self)
        self.wave_text_box.active = False
        self.next_wave_time = Text_box(50,100,200,75,(255,255,255),"0:05",False,self)
        self.next_wave_time.active = False
        # Two text boxes that declare to the player what the current wave is, and when the next wave will begin

        self.warning_1 = Text_box(900, 300, 500, 100, (255, 255, 255), "Are you sure about this?", False, self)
        self.warning_2 = Text_box(900, 450, 500, 100, (255, 255, 255), "The game is going to be impossible", False, self)
        self.warning_3 = Text_box(775, 600, 700, 100, (255, 255, 255), "This number of enemies is not recommended", False, self)
        # Warning text boxes that are shown if the player selects a high number of enemies

        self.tutorial_surface = pygame.Surface((1500,900))
        # The surface that covers the screen transparently when

        self.tutorial_stage = 0
        # The current stage of the tutorial

        self.tutorial_active = True # Whether the tutorial should be shown on the screen
        self.tutorial_selected = True # Whether the player has selected they would like to play with the tutorial

        self.click_to_continue = Text_box(1050,750,400,100,(255,255,255),"Click anywhere to continue",False,self)

        self.tutorial_movement = Text_box(350,600,300,100,(255,255,255),"WASD to move",False,self)
        self.sprint_tutorial = Text_box(350,675,300,50,(255,255,255),"shift to sprint",False,self)
        self.tutorial_gun = Text_box(850,600,300,100,(255,255,255),"left click to shoot",False,self)

        self.tutorial_sword = Text_box(250,600,400,100,(255,255,255),"right click to swing sword",False,self)
        self.tutorial_grenade = Text_box(850,600,400,100,(255,255,255),"press G to launch a grenade",False,self)

        self.tutorial_laser = Text_box(425,600,650,100,(255,255,255),"Hold F to fire laser when charge is over 50%",False,self)
        # Text boxes displaying various information about how certain weapons are controlled by the player in the game

        self.current_time_after_wave_began = 0
        # Records how long the wave has been going on for


    def handle_inputs(self):
        """ Handles all inputs the player can make in the game world """
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not self.tutorial_active:
                        self.bullet_system.create_shot(self.player, pygame.mouse.get_pos(), 0.1)
                        self.bullet_system.check_hit(self.enemies)
                        # Create a list of hit-boxes between the player and their mouse position and then check if there is a collision with a valid target (e.g. Enemy or Tree)

                        pygame.mixer.find_channel(True).play(self.gunshot)
                        # Play the gunshot sound effect

                        self.handle_buttons()
                        # Check if any buttons are being pressed
                    else:
                        self.tutorial_stage += 1
                        # Progress the tutorial stage


                if event.button == 3:

                    pygame.mixer.find_channel(True).play(self.sword_sfx)

                    mouse_pos = pygame.mouse.get_pos()
                    # Play the sword sound effect and determine the player's mouse position

                    self.sword.xvector = mouse_pos[0] - self.player.cx
                    self.sword.yvector = mouse_pos[1] - self.player.cy
                    # Get the vector between the player's position and their mouse position

                    magnitude = math.sqrt(self.sword.xvector ** 2 + self.sword.yvector ** 2)
                    # Get the magnitude of the vector using the pythagorean theorem

                    self.sword.xvector = self.sword.xvector / magnitude
                    self.sword.yvector = self.sword.yvector / magnitude
                    # Divide each vector by the magnitude to normalise the vector

                    self.sword.cx = self.player.cx + (self.sword.xvector * 30)
                    self.sword.cy = self.player.cy + (self.sword.yvector * 30)
                    self.sword.wcx = self.player.wcx + (self.sword.xvector * 30)
                    self.sword.wcy = self.player.wcy + (self.sword.yvector * 30)
                    # Set the sword object part way along the normalised vector

                    self.sword.draw(self.screen)
                    self.sword.check_hit(self.enemies,self)
                    # Draw the sword object on the game screen and check if the sword has collided with anything

        self.key_g_held_down,self.key_g_not_pressed = self.handle_grenade_logic(self.key_g_held_down, self.key_g_not_pressed)
        # Handle the grenade logic, while preserving the state of whether the G key is being held down and whether the G key has not been pressed yet

        self.handle_laser_inputs()
        # Handle the F key input and determine how the laser weapon should respond

        if not self.tutorial_active:
            self.handle_movement() # Handles player movement

    def initialize_enemies(self,enemy_count,virus_count):
        """ Creates enemies and adds them to the list of viruses and enemies """
        for i in range(enemy_count):  # How many enemies should be created
            self.enemies.append(Enemy(random.randint(0, 750), random.randint(0, 450), self.current_enemy_id,self))
            self.current_enemy_id += 1
            # Create an enemy in a random position and increment the current enemy id, so that the next enemy has a unique id

        for i in range(virus_count):  # How many viruses should be created
            self.viruses.append(Virus(self.current_enemy_id,self))
            self.current_enemy_id += 1
            # Create a virus and increment the enemy id by one so each virus has a unique id

    def update_collision_hitboxes(self):
        """ Updates the walking spots of the player as they move around the world """
        self.player.left = (self.player.cx - 25, self.player.cy)
        self.player.up = (self.player.cx, self.player.cy - 25)
        self.player.right = (self.player.cx + 25, self.player.cy)
        self.player.down = (self.player.cx, self.player.cy + 25)
        self.player.upleft = (self.player.cx - 18, self.player.cy - 18)
        self.player.downright = (self.player.cx + 18, self.player.cy + 18)
        self.player.downleft = (self.player.cx - 18, self.player.cy + 18)
        self.player.upright = (self.player.cx + 18, self.player.cy - 18)

    def display_menu(self):
        """ Displays the main meny before the game starts """
        self.menu_screen.fill((200,255,200))
        self.draw_buttons(self.menu_screen)
        self.screen.blit(self.menu_screen,(0,0))
        self.active_widgets = []

        for button in self.widgets:
            if button.active:
                self.active_widgets.append(button)
                if button.adjustable:
                    self.active_widgets.append(button.plus_button)
                    self.active_widgets.append(button.minus_button)

        # Empty the list of active widgets and add every widget flagged as "active" to the list

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_buttons()
        # Handle buttons when the player clicks


        if self.player.health <= 0:
            self.music_played = False
            self.handle_soundtrack()
            # Tell the game to handle the soundtrack when the player has died

        if int(self.viruses_counter.text) + int(self.enemies_counter.text) >= 27 and self.settings_open:
            self.warning_1.active = True
        else:
            self.warning_1.active = False
        if int(self.viruses_counter.text) + int(self.enemies_counter.text) >= 37 and self.settings_open:
            self.warning_2.active = True
        else:
            self.warning_2.active = False
        if int(self.viruses_counter.text) + int(self.enemies_counter.text) >= 47 and self.settings_open:
            self.warning_3.active = True
        else:
            self.warning_3.active = False

        # Show warning to the player depending on the number of enemies they have selected
    def draw_island_and_background(self):
        """ Draws the island and the background """
        self.screen.fill((107, 191, 255))
        self.island.draw()

    def draw_enemies_player_and_trees(self):
        """ Draws enemies, players and trees onto the main screen """
        if debugging:
            self.camera_follow.draw()
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.trees = sorted(self.trees,key=lambda tree:tree.cy) #Order trees so that the ones with the highest y coordinates are drawn first

        for tree in self.trees:
            tree.draw(self.screen)

    def handle_sword_logic(self):
        """ Handles enemy movement when they have been stunned and when they have not been stunned by the sword"""
        for enemy in self.enemies:
            if debugging:
                enemy.sword_target.draw()
            if not enemy.sword_stunned:
                if enemy.type == "e":
                    enemy.beeline(self.player) # Regular enemies should move towards the player
                else:
                    enemy.velocity = 1
                    if enemy.deciding_where:
                        enemy.target = Target(enemy.wcx + 45*random.randint(-30,30),enemy.wcy + 45*random.randint(-30, 30),self)
                        self.objects.append(enemy.target)
                        enemy.counter = 3
                        enemy.deciding_where = False
                        # The enemy determines a target at a random position around them
                        if calc_distance(enemy.target,self.island) > 0:
                            enemy.deciding_where = True
                            # If the position is not on the island, the code above is re-run and a new target is created
                    else:
                        if debugging:
                            enemy.target.draw(self.screen)
                        enemy.beeline(enemy.target)
                        enemy.counter -= (1/FPS) # Decrement a timer counting how long the enemy has been following a specific target
                        # Have the enemy move towards the target they previously created
                        if enemy.counter <= 0:
                            enemy.deciding_where = True
                            # Create a new target to move towards after 3 seconds
            else:
                enemy.velocity = 3
                enemy.beeline(enemy.sword_target)
                enemy.recover_from_sword()
                # When the enemy has been hit by the sword, have them move towards their sword target and then have them recover from the sword.

    def handle_grenade_logic(self, key_g_held_down, key_g_not_pressed):
        """ Calls the grenade's methods depending on the player's inputs of the G key """
        mouse_pos = (0,0)
        if key_g_held_down and key_g_not_pressed:
            self.active_grenades.append(Grenade_v2(self))
            self.objects.append(self.active_grenades[-1])
            key_g_not_pressed = False
            # When the G key is pressed down initially, create a grenade object and append it to the list of active grenades
        if key_g_held_down and self.active_grenades:
            self.active_grenades[-1].cook()
            # While the G key is being held down, decrement the fuse timer of each grenade
        if self.keys[pygame.K_g]:
            key_g_held_down = True
        else:
            key_g_held_down = False
        # Record when the G key is being held down

        if not key_g_held_down and key_g_not_pressed == False:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (mouse_pos[0] + self.camera_follow.cam_cx, mouse_pos[1] + self.camera_follow.cam_cy)
            if self.active_grenades:
                self.active_grenades[-1].throw(self.player, mouse_pos)
            key_g_not_pressed = True
            # Have the grenade move towards the player's mouse position when the G key has been released

        for grenade in self.active_grenades:
            # Handle the grenade being thrown and the grenade exploding by calling the respective methods
            if grenade.exploded:
                self.active_grenades.remove(grenade)
            elif grenade.thrown:
                grenade.throw(self.player, mouse_pos)

        return key_g_held_down, key_g_not_pressed
        # Return values back to the main game object

    def handle_laser_inputs(self):
        """ Calls the player's laser methods, depending on the user's input of the F key """
        laser_channel = pygame.mixer.Channel(19)
        if not self.tutorial_active:
            if self.player.firing_laser:
                self.player.fire_laser()
                self.player.check_laser_hit(self.enemies)
                self.player.decrease_laser_charge()
                # Decrease the laser charge while the laser is being fired
            elif self.keys[pygame.K_f] and self.player.laser_charge > 50:
                self.player.firing_laser = True
                laser_channel.play(self.laser_sfx, -1)
                # Play the laser sound effect while the laser is being fired
            if (not self.keys[pygame.K_f] or self.player.laser_charge <= 0) and self.player.firing_laser:
                self.player.firing_laser = False
                laser_channel.stop()
                # Stop the sound effect when the player stops firing their laser
            if not self.player.firing_laser and self.player.laser_charge <= 99:
                self.player.increase_laser_charge()
                # Increment the player's laser charge when they are not firing their laser

    def handle_movement(self):
        """ Handles player's movement, depending on what movement keys the player has pressed down """
        if self.keys[pygame.K_LSHIFT] or self.keys[pygame.K_RSHIFT]:
            self.player.sprinting = 2
        else:
            self.player.sprinting = 1
        # Detect if the player is sprinting or not
        self.player.check_walkable(self.trees) # Check if the player can walk given the trees in the game world
        move_ticker = 0 # Set timer that records how over the player can move one step
        if self.keys[
            pygame.K_w] and self.player.up_walkable and self.player.upright_walkable and self.player.upleft_walkable:
            if move_ticker == 0:
                # If the player is holding W and can move in that direction, they should do so
                move_ticker = self.player.move_up(self.player.in_camera)

                if self.keys[
                    pygame.K_a] and self.player.left_walkable and self.player.upleft_walkable and self.player.downleft_walkable:
                    #If the player is holding W and A, they should move up and left
                    self.player.move_up_and_left(self.player.in_camera)
                if self.keys[
                    pygame.K_d] and self.player.right_walkable and self.player.upright_walkable and self.player.downright_walkable:
                    # If the player is holding W and D, they should move up and right
                    self.player.move_up_and_right(self.player.in_camera)
        if self.keys[
            pygame.K_s] and self.player.down_walkable and self.player.downleft_walkable and self.player.downright_walkable:
            if move_ticker == 0:
                # If the player is hold S, and they can move in that direction, they should do so
                move_ticker = self.player.move_down(self.player.in_camera)
                if self.keys[
                    pygame.K_a] and self.player.left_walkable and self.player.upleft_walkable and self.player.downleft_walkable:
                    # If the player is holding S and A, and they can move in that direction, then they move down and left
                    self.player.move_down_and_left(self.player.in_camera)
                if self.keys[
                    pygame.K_d] and self.player.right_walkable and self.player.upright_walkable and self.player.downright_walkable:
                    # If the player is holding S and D, they should move down and right if they can do so
                    self.player.move_down_and_right(self.player.in_camera)
        if self.keys[
            pygame.K_a] and self.player.left_walkable and self.player.upleft_walkable and self.player.downleft_walkable:
            if move_ticker == 0:
                self.player.move_left(self.player.in_camera)
                # If the player can move left and the A key is being held down, they should move left
        if self.keys[
            pygame.K_d] and self.player.right_walkable and self.player.upright_walkable and self.player.downright_walkable:
            if move_ticker == 0:
                self.player.move_right(self.player.in_camera)
                # If the player can move right and the D key is being held down, they should move right

    def update_frames_and_time(self):
        """ Increment's the number of frames and calculates the number of seconds that have passed since the
        start of the game"""
        self.frames = self.frames + 1
        self.seconds = self.frames / FPS

    def update_item_positions_relative_to_camera(self):
        """ Updates all items positions relative to the player's camera offset """
        for item in self.objects:
            item.cx = item.wcx - self.camera_follow.cam_cx
            item.cy = item.wcy - self.camera_follow.cam_cy

    def reset_and_prepare_for_next_frame(self):
        """ Calls key functions to reset certain objects in the game world and also checks to see if a new wave should
        start or if the player has won or lost the game"""

        self.bullet_system.clean_shot() # Remove any hit-boxes generated if the player shot the gun in the last frame
        self.main_menu = self.player.update_health() # Activate the main menu if the player has died
        self.health_bar.draw(self.screen,self) # Draw the health bar onto the screen

        self.active_widgets = []

        for button in self.widgets:
            if button.active:
                self.active_widgets.append(button)
        # Check for any active buttons and append them to the active_widgets list

        self.draw_buttons(self.screen) #Draw all active widgets onto the screen

        self.laser_charge_text_box.update(str(self.player.laser_charge) + "%")
        if self.player.firing_laser:
            self.laser_status_text_box.update("Laser is firing")
            self.laser_status_text_box.color = (255,255,0)
        elif self.player.laser_charge <= 50:
            self.laser_status_text_box.update("Laser not ready")
            self.laser_status_text_box.color = (255,0,0)
        else:
            self.laser_status_text_box.update("Laser ready")
            self.laser_status_text_box.color = (0,255,0)
        # Update the laser charge and laser status text boxes, allowing the player to see the status of
        # the laser and whether it is ready to fire

        for enemy in self.enemies:
            enemy.evaluate_health()
            enemy.scan_for_friendlies(self.enemies)
        for virus in self.viruses:
            if virus.health > 0:
                self.current_enemy_id = virus.clone_if_can(self.enemies, self.current_enemy_id)
                virus.decrement_cooldown()
            virus.evaluate_health()
            virus.scan_for_friendlies(self.enemies)
        # Evaluate the health for each enemy and virus, let enemies scan for friendlies to correctly apply the movement speed increase
        # Have the virus create another enemy if it is able to, and decrement its cooldown every frame

        self.camera_follow.scan_for_player(self.player) # Check to see if the player is entering or exiting the bounding box
        self.update_collision_hitboxes()
        self.player.walking_spots = [self.player.left, self.player.right, self.player.down, self.player.up,
                                      self.player.upleft, self.player.downleft, self.player.downright,
                                      self.player.upright]
        # Update the list of walking_spots for the player with their correct position based on where the player currently is

        if not self.player.in_camera:
            self.player.hcx = self.player.cx
            self.player.hcy = self.player.cy
        # Set player's heading coordinates to their current position, so that the game can detect when the player is
        # moving back into the bounding box

        self.bullet_system.decrement_cooldown(0.1) # Decrease the cooldown for how long the player must wait before being able to shoot the gun again

        if not self.enemies:
            if self.initializing_next_wave:
                self.next_wave_time.active = True
                self.current_time_wave_ended = self.seconds
                self.initializing_next_wave = False
                self.next_wave_time.active = True
                # Show the next wave timer and record the current time the wave ended
            if (self.seconds - self.current_time_wave_ended) >= 1:
                self.current_time_wave_ended = self.seconds
                self.seconds_passed += 1 # Count the number of seconds that have passed since the end of the last wave
                self.next_wave_time.update(f"0:0{int(5 - self.seconds_passed)}") # Update timer text box so player can see how much time is left before the next wave begins
                if self.seconds_passed >= 5:
                    self.seconds_passed = 0
                    self.current_time_after_wave_began = 0
                    self.next_wave_time.update(f"0:0{int(5 - self.seconds_passed)}")
                    self.current_wave += 1
                    # Increment current wave and reset wave timer.

                    self.waves_reached.update(f"Waves reached: {self.current_wave}") # Update current wave tracker
                    if self.current_wave == 11:
                        self.victory = True
                        self.main_menu = True
                        # The player has survived wave 10, they have won and should be returned to the main menu
                    self.wave_text_box.update(f"wave {self.current_wave}")
                    # Update the wave text box showing what wave the player is currently on
                    if (self.current_wave + 1) % 2 == 0:
                        self.music_played = False
                        # Every second wave declare that music has not been played, causing the music to be handled again,
                        # which chooses the correct soundtrack to play for the current wave
                    self.next_wave_time.active = False
                    self.initializing_next_wave = True
                    # Reset attributes as the next wave has begun and the timer should no longer be visible to the player
                    self.enemies_counter.text = str(int(self.enemies_counter.text) + 1)
                    self.viruses_counter.text = str(int(self.viruses_counter.text) + 1) # Add 1 to the number of enemies and viruses that were spawned last wave
                    self.initialize_enemies(int(world.enemies_counter.text), int(world.viruses_counter.text)) # Initialise the enemies for the next wave
                    self.objects = []
                    self.initialise_world_objects() # Reinitialise the objects in the world, including the newly spawned enemies

        self.current_time_after_wave_began += (1/FPS)
        #Handle subsequent tutorial messages
        if self.current_wave == 2 and self.tutorial_selected and self.current_time_after_wave_began == (2/FPS):
            self.tutorial_stage += 1
            self.tutorial_active = True
            # Display the second tutorial message

        if self.current_wave == 3 and self.tutorial_selected and self.current_time_after_wave_began == (2/FPS):
            self.tutorial_stage += 1
            self.tutorial_active = True
            self.laser_charge_text_box.active = True
            self.laser_status_text_box.active = True
            # Display the third tutorial message and show the player the laser status and charge on their HUD

        if self.main_menu:
            self.grenades_launched.update("Grenades launched: "+str(self.grenades_launched_count))
            self.shots_fired.update("Shots fired: "+str(self.shots_fired_count))
            self.enemies_defeated.update("Total enemies defeated: "+str(self.enemies_defeated_count))
            self.regular_enemies_defeated.update("Regular enemies defeated: " + str(self.regular_enemy_defeated_count))
            self.viruses_defeated.update("Viruses defeated: "+str(self.viruses_defeated_count))
            # Update statistics if the player is going to go to the main menu

        if self.victory:
            for widget in self.widgets:
                widget.active = False
            self.congrats.active = True
            self.grenades_launched.active = True
            self.enemies_defeated.active = True
            self.regular_enemies_defeated.active = True
            self.viruses_defeated.active = True
            self.shots_fired.active = True
            self.restart_button.active = True
            # Display relevant statistics for winning the game

        if self.main_menu and not self.victory:
            for widget in self.widgets:
                widget.active = False
            self.you_lose.active = True
            self.grenades_launched.active = True
            self.enemies_defeated.active = True
            self.regular_enemies_defeated.active = True
            self.viruses_defeated.active = True
            self.shots_fired.active = True
            self.waves_reached.active = True
            self.restart_button.active = True
            # Display relavent statistics for losing the game





    def draw_bullet_trail(self):
        """ Draws the bullet trail onto the main screen if there is one """
        if len(self.bullet_system.bullet_trail) > 0:
            self.bullet_system.draw(self.player,self.screen)

    def allow_debug_options(self):
        """ Allows certain keys to be pressed for debugging """
        if self.keys[pygame.K_UP]:
            self.player.in_camera = False #Forcibly set the player's in_camera attribute to false when the up arrow key is pressed
        if self.keys[pygame.K_h]:
            self.player.cx = 600
            self.player.cy = 300
            self.player.hcx = 600
            self.player.hcy = 300
            self.player.wcx = 600
            self.player.wcy = 300
            self.camera_follow.cam_cx = 0
            self.camera_follow.cam_cy = 0
            # Reset the player's position to the starting position when the H key is pressed
        pygame.draw.circle(self.screen, (255, 50, 255), (self.player.hcx, self.player.hcy), 10)
        # Draw a circle used to represent where the game thinks the player is heading

    def initialise_world_objects(self):
        """ Loads all viruses, enemies, targets, trees and the island into the world.objects list """
        self.objects.append(self.island)
        for i in range(len(self.trees)):
            self.objects.append(self.trees[i])
        for virus in world.viruses:
            world.enemies.append(virus)
        for enemy in world.enemies:
            world.objects.append(enemy)
        for target in world.targets:
            world.objects.append(target)

    def draw_buttons(self,screen):
        """ Draws any active buttons onto the screen """
        for button in self.active_widgets:
            button.draw(screen)

    def handle_buttons(self):
        """ Check to see if any active button is colliding with the player's mouse position """
        for button in self.active_widgets:
            if button.rect.collidepoint(pygame.mouse.get_pos()):
                button.execute_command()

    def open_settings(self):
        """ Enables key widgets for the settings menu """
        for widget in self.widgets:
            widget.active = False

        self.enemies_text_box.active = True
        self.enemies_counter.active = True
        self.back_button.active = True
        self.viruses_counter.active = True
        self.viruses_text_box.active = True
        self.settings_open = True

    def handle_soundtrack(self):
        """ Plays the correct music depending on the wave number """
        if self.music_played == False:
            pygame.mixer.stop()
            self.music_played = True
            if self.main_menu:
                pass # Music is stopped and no more music is played
            elif 1 <= self.current_wave <= 2:
                self.ss.set_volume(0.3)
                self.ss.play(-1)
                # Play the soundtrack for waves 1 and 2
            elif 3 <= self.current_wave <= 4:
                self.fad.set_volume(0.3)
                self.fad.play(-1)
                # Play the soundtrack for waves 3 and 4
            elif 5 <= self.current_wave <= 6:
                self.qd.set_volume(0.3)
                self.qd.play(-1)
                # Play the soundtrack for waves 5 and 6
            elif 7 <= self.current_wave <= 8:
                self.am.set_volume(0.3)
                self.am.play(-1)
                # Play the soundtrack for waves 7 and 8
            else:
                self.SoTI.set_volume(0.3)
                self.SoTI.play(-1)
                # Play the soundtrack for any other waves (wave 9 and 10)

    def update_tutorial_frames(self):
        """ Updates the widgets used in the tutorial"""
        self.active_widgets = []

        for button in self.widgets:
            if button.active:
                self.active_widgets.append(button)

        self.draw_buttons(self.screen)

    def handle_tutorial(self):
        """ Displays the correct widgets depending on the tutorial stage number"""
        if self.tutorial_stage == 0:
            self.tutorial_movement.active = True
            self.tutorial_gun.active = True
            self.click_to_continue.active = True
            self.sprint_tutorial.active = True

            self.tutorial_surface.set_alpha(128)
            self.tutorial_surface.fill((255, 255, 255))

            self.draw_enemies_player_and_trees()

            self.screen.blit(self.tutorial_surface, (0, 0))

            self.update_tutorial_frames()
            # Display text boxes teaching the player how to move, sprint and shoot their gun
        elif self.tutorial_stage == 2:
            self.click_to_continue.active = True
            self.tutorial_sword.active = True
            self.tutorial_grenade.active = True

            self.draw_enemies_player_and_trees()

            self.screen.blit(self.tutorial_surface, (0, 0))

            self.update_tutorial_frames()
            # Display text boxes teaching the player how to use the sword and grenade

        elif self.tutorial_stage == 4:
            self.click_to_continue.active = True
            self.tutorial_laser.active = True

            self.draw_enemies_player_and_trees()

            self.screen.blit(self.tutorial_surface, (0, 0))

            self.update_tutorial_frames()

            # Display text boxes teaching the player how to use the laser weapon

        elif self.tutorial_stage % 2 == 1:
            self.tutorial_movement.active = False
            self.tutorial_gun.active = False
            self.sprint_tutorial.active = False
            self.tutorial_grenade.active = False
            self.tutorial_sword.active = False
            self.click_to_continue.active = False
            self.tutorial_laser.active = False
            self.tutorial_active = False
            # Deactivate the tutorial screen whenever the tutorial stage is an odd number


world = GameWorld() # Create the game world


if world.tutorial_selected:
    world.tutorial_active = True
else:
    world.tutorial_active = False
# Activate tutorial if tutorial is selected

while world.running:

    if world.main_menu:
        world.display_menu() # Display the main menu

        if world.restarted == True:
            world = GameWorld()
            # Create a new game world if the player wishes to restart

    else:
        world.update_frames_and_time() # Keep the frames and seconds that have passed since the start of the game up to date

        world.draw_island_and_background()

        world.handle_inputs()  # Handles left click, right click, G key, F key and movement
                               # Allowing the player to shoot, use the sword, throw a grenade, fire their laser, and move respectively

        if not world.tutorial_active:

            world.draw_bullet_trail()
            # Draw the gunshot if the player has just shot the gun

            world.draw_enemies_player_and_trees()
            # Draw the enemies, the player, and the trees onto the screen

            world.handle_sword_logic()
            # Handle the enemy's movement, depending on whether they have been hit by the sword or not

            world.keys = pygame.key.get_pressed()
            # Get the keys pressed by the player

            world.player.update_position()
            # Update the player's camera coordinates, depending on their world coordinates and how far the camera has moved

            world.player.walking_spot_permissions = [True for i in range(8)]
            # Reset the player's walking spot permissions to True for all 8 of the player's walking spots

            world.update_item_positions_relative_to_camera()
            # Update the position of the items in the "world.objects" list, generating their camera coordinates from their world coordinates and the camera's offset

            world.draw_buttons(world.screen)
            # Draw any active widgets onto the world screen

            if debugging:
                world.allow_debug_options() # e.g. pressing H to return to initial positions

            world.reset_and_prepare_for_next_frame()
            # Prepare for the next frame by performing key functions such as checking if the player is alive and updating the health of the enemies

            world.handle_soundtrack()
            # Play the correct music depending on the wave the player is on
        else:
            world.handle_tutorial()
            # Display the tutorial to the player if the tutorial screen is currently active

        fpsClock.tick(FPS)
        # Move to the next frame at a rate denoted by the FPS constant
    pygame.display.flip()
    # Update to the next frame by redrawing the display surface

pygame.quit()
# Quite the game if the above while loop is ever broken by "world.running" being set to False