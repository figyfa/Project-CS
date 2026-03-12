import pygame
import math
import random
import socket
import os

MOVE_COUNTER = 10

HYPOTENUSE = 2.121

IP = "127.0.0.1"
PORT = 8000

pygame.init()

pygame.mixer.init()


screen = pygame.display.set_mode((1500, 900))
menu_screen = pygame.Surface((1500, 900))

running = True

debugging = False

FPS = 60
fpsClock = pygame.time.Clock()
pygame.display.set_caption("Game")

def calc_distance(pointA, pointB):
    return math.sqrt((pointA.wcx - pointB.wcx)**2 + (pointA.wcy - pointB.wcy)**2) - pointA.radius - pointB.radius

def calc_distance_circle_and_point(pointA, pointB):
    return math.sqrt((pointA.wcx - pointB[0]-world.camera_follow.cam_cx)**2 + (pointA.wcy - pointB[1] - world.camera_follow.cam_cy)**2) - pointA.radius


class Widget():
    def __init__(self, x, y, width, height, color,text,game):
        self.cx = x
        self.cy = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.active = True
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont('comicsans', 30)
        self.text_color = (0,0,0)
        self.text_render = self.font.render(self.text, True, self.text_color)
        self.center_rect = self.text_render.get_rect(center = self.rect.center)
        self.adjustable = False
        game.widgets.append(self)

    def draw(self,screen):
        self.text_render = self.font.render(self.text, True, self.text_color)
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_render, self.center_rect)

    def execute_command(self):
        pass

class BackButton(Widget):
    def __init__(self, x, y, width, height, color,text,game):
        super().__init__(x,y,width,height,color,text,game)
        self.active = False

    def execute_command(self):
        for button in world.widgets:
            button.active = False

        world.settings_open = False

        world.start_button.active = True
        world.settings_button.active = True

class StartButton(Widget):
    def __init__(self, x, y, width, height, color, text,game):
        super().__init__(x, y, width, height, color, text,game)

    def execute_command(self):
        global main_menu
        main_menu = False
        self.active = False
        world.settings_button.active = False

        world.laser_charge_text_box.active = True
        world.wave_text_box.active = True

        world.initialize_enemies(int(world.enemies_counter.text), int(world.viruses_counter.text))

        world.initialise_world_objects()

class SettingsButton(Widget):
    def __init__(self, x, y, width, height, color, text,game):
        super().__init__(x,y,width,height,color,text,game)

    def execute_command(self):
        self.active = False
        world.open_settings()

class Plus_button(Widget):
    def __init__(self, x, y, width, height, color,text_box,game):
        super().__init__(x,y,width,height,color,"+",game)
        self.text_box = text_box

    def execute_command(self):
        print(self.text_box.text)
        self.text_box.text = str(int(self.text_box.text)+1)

class Minus_button(Widget):
    def __init__(self, x, y, width, height, color,text_box,game):
        super().__init__(x,y,width,height,color,"-",game)
        self.text_box = text_box

    def execute_command(self):
        if self.text_box.text != "0":
            print(self.text_box.text)
            self.text_box.text = str(int(self.text_box.text)-1)

class Text_box(Widget):
    def __init__(self, x, y, width, height, color,text,adjustable,game):
        super().__init__(x,y,width,height,color,text,game)
        self.adjustable = adjustable
        self.active = False

        if adjustable:
            self.plus_button = Plus_button(x+120, y, width-10, height, color,self,game)
            self.minus_button = Minus_button(x-100, y, width-10, height, color,self,game)
            self.plus_button.active = False
            self.minus_button.active = False
        else:
            self.plus_button = None
            self.minus_button = None

    def update(self,text):
        self.text = text


class Island:
    def __init__(self,colour, radius, cx, cy):
        self.colour = colour
        self.radius = radius
        self.cx = cx
        self.cy = cy
        self.wcx = cx
        self.wcy = cy

    def draw(self):
        pygame.draw.circle(screen, (self.colour), (self.cx, self.cy), self.radius)

class Gun:
    def __init__(self):
        self.equipped = True
        self.hcx = 0
        self.hcy = 0

class Sword:
    def __init__(self):
        self.cx = 0
        self.cy = 0
        self.wcx = 0
        self.wcy = 0
        self.radius = 27
        self.colour = (255,255,255)
        self.xvector = 0
        self.yvector = 0

    def draw(self):
        pygame.draw.circle(screen, (self.colour),(self.cx,self.cy),self.radius)

    def check_hit(self,enemies):
        for enemy in enemies:
            if calc_distance(enemy,self) <= 0:
                enemy.take_damage_from_sword(world.sword.xvector,world.sword.yvector)
                enemy.sword_stunned = True

class Tree:
    def __init__(self,wcx,wcy):
        self.wcx = wcx
        self.wcy = wcy
        self.cx = wcx
        self.cy = wcy
        self.radius = 20

    def draw(self):
        pygame.draw.rect(screen,(150,75,0),(self.cx-18,self.cy-93,36,115))
        pygame.draw.circle(screen,(0,240,20),(self.cx,self.cy-163),72)
        if debugging:
            pygame.draw.circle(screen,(255,255,255),(self.cx,self.cy),self.radius)

class BoundingBox:
    def __init__(self,lx=550,ty=300,width=400,height=250,screen=screen):
        self.lx = lx
        self.ty = ty
        self.width = width
        self.height = height
        self.s = pygame.Surface((width,height))
        self.screen = screen
        self.cam_cx = 0
        self.cam_cy = 0

    def draw(self):
        self.s.set_alpha(128)
        self.s.fill((255,255,255))
        self.screen.blit(self.s,(self.lx,self.ty))

    def scan_for_player(self,player):
        if self.lx < player.hcx - 5 and player.hcx + 5 < (self.lx + self.width) and self.ty < player.hcy - 5 and (self.ty + self.height) > player.hcy:
            #print("player detected")
            player.in_camera = True
            return True
        else:
            player.in_camera = False
            return False

class Health_bar():
    def __init__(self):
        self.cx = 5
        self.cy = (screen.get_height()-65)
        self.width = 200
        self.height = 50

    def draw(self):
        pygame.draw.rect(screen,(0,0,0),(self.cx,self.cy,self.width,self.height))
        pygame.draw.rect(screen,(255,0,0),(self.cx,self.cy,self.width-((1-world.player.health/100)*self.width),self.height))




class Player:
    def __init__(self,cx,cy):
        self.cx = cx
        self.cy = cy
        self.vy = 3
        self.vx = 3
        self.vxy = math.sqrt(self.vx**2 + self.vy**2)
        self.in_camera = True
        self.hcx = cx
        self.hcy = cy
        self.radius = 25
        self.sprinting = 1
        self.max_health = 100
        self.health = 100
        self.colour = (0,0,0)
        self.laser_trail = []
        self.first_run = True
        self.wcx = 600
        self.wcy = 300

        self.laser_charge = 0
        self.firing_laser = False

        #For collision
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

        self.left_walkable = True
        self.right_walkable = True
        self.down_walkable = True
        self.up_walkable = True
        self.downleft_walkable = True
        self.downright_walkable = True
        self.upright_walkable = True
        self.upleft_walkable = True

        self.walking_spot_permissions = [self.left_walkable,self.right_walkable,self.down_walkable,self.up_walkable,self.upleft_walkable,self.downleft_walkable,self.downright_walkable,self.upright_walkable]


    def check_walkable(self,trees):
        for i in range(len(trees)):
            for j in range(len(self.walking_spots)):
                if calc_distance_circle_and_point(trees[i],self.walking_spots[j]) <= self.collision_radius:
                    self.walking_spot_permissions[j] = False
                    #print(f"{self.walking_spots[j]} FOUND UNWALKABLE")

        for i in range(len(self.walking_spots)):
            if calc_distance_circle_and_point(world.island,self.walking_spots[i]) >= self.collision_radius:
                self.walking_spot_permissions[i] = False

        self.left_walkable = self.walking_spot_permissions[0]
        self.right_walkable = self.walking_spot_permissions[1]
        self.down_walkable = self.walking_spot_permissions[2]
        self.up_walkable = self.walking_spot_permissions[3]
        self.upleft_walkable = self.walking_spot_permissions[4]
        self.downleft_walkable = self.walking_spot_permissions[5]
        self.downright_walkable = self.walking_spot_permissions[6]
        self.upright_walkable = self.walking_spot_permissions[7]

    def move_up(self,in_camera):
        if in_camera:
            move_ticker = MOVE_COUNTER
            self.hcy -= self.vy * self.sprinting
            #self.cy = self.hcy
            self.wcy -= self.vy * self.sprinting
            # print("Moving up",self.cx,self.cy)
            return move_ticker
        else:
            move_ticker = MOVE_COUNTER
            self.hcy -= self.vy * 10
            world.camera_follow.cam_cy -= self.vy * self.sprinting
            self.wcy -= self.vy * self.sprinting
            # print("Moving up",self.cx,self.cy)
            return move_ticker

    def move_up_and_right(self,in_camera):
        if in_camera:
            self.hcx += HYPOTENUSE * self.sprinting
            self.hcy += (self.vy - HYPOTENUSE) * self.sprinting
            #self.cx = self.hcx
            self.wcx += HYPOTENUSE * self.sprinting
            self.wcy += (self.vy - HYPOTENUSE) * self.sprinting
            # print("Moving up and right")
        else:
            self.hcx += HYPOTENUSE * 10
            self.hcy += (self.vy - HYPOTENUSE) * 10
            world.camera_follow.cam_cx += HYPOTENUSE * self.sprinting
            world.camera_follow.cam_cy += (self.vy-HYPOTENUSE) * self.sprinting
            self.wcx += HYPOTENUSE * self.sprinting
            self.wcy += (self.vy-HYPOTENUSE) * self.sprinting
            # print("Moving up and right")

    def move_up_and_left(self,in_camera):
        if in_camera:
            self.hcx -= HYPOTENUSE * self.sprinting
            self.hcy += (self.vy-HYPOTENUSE) * self.sprinting
            #self.cx = self.hcx
            self.wcx -= HYPOTENUSE * self.sprinting
            self.wcy += (self.vy-HYPOTENUSE) * self.sprinting
            # print("Moving up and left")
        else:
            self.hcx -= HYPOTENUSE * 10
            self.hcy += (self.vy-HYPOTENUSE) * 10
            world.camera_follow.cam_cx -= HYPOTENUSE * self.sprinting
            world.camera_follow.cam_cy += (self.vy-HYPOTENUSE) * self.sprinting
            self.wcx -= HYPOTENUSE * self.sprinting
            self.wcy += (self.vy-HYPOTENUSE) * self.sprinting
            # print("Moving up and left")

    def move_down(self,in_camera):
        if in_camera:
            move_ticker = MOVE_COUNTER
            self.hcy += self.vy * self.sprinting
            #self.cy = self.hcy
            self.wcy += self.vy * self.sprinting
            return move_ticker
        else:
            move_ticker = MOVE_COUNTER
            self.hcy += self.vy * 10
            if world.camera_follow.scan_for_player(self):
                self.move_down(True)
            world.camera_follow.cam_cy += self.vy * self.sprinting
            self.wcy += self.vy * self.sprinting
            # print("Moving down")
            return move_ticker

    def move_down_and_left(self,in_camera):
        if in_camera:
            self.hcx -= HYPOTENUSE * self.sprinting
            self.hcy -= (self.vy-HYPOTENUSE) * self.sprinting
            #self.cx = self.hcx
            self.wcx -= HYPOTENUSE * self.sprinting
            self.wcy -= (self.vy-HYPOTENUSE) * self.sprinting
            # print("Moving down and left")
        else:
            self.hcx -= HYPOTENUSE * 10
            self.hcy -= (self.vy-HYPOTENUSE) * 10
            world.camera_follow.cam_cx -= HYPOTENUSE * self.sprinting
            world.camera_follow.cam_cy -= (self.vy-HYPOTENUSE) * self.sprinting
            self.wcx -= HYPOTENUSE * self.sprinting
            self.wcy -= (self.vy-HYPOTENUSE) * self.sprinting
            # print("Moving left and down")

    def move_down_and_right(self,in_camera):
        if in_camera:
            # print("Moving down and right")
            self.hcx += HYPOTENUSE * self.sprinting
            self.hcy -= (self.vy-HYPOTENUSE) * self.sprinting
            #self.cx = self.hcx
            self.wcx += HYPOTENUSE * self.sprinting
            self.wcy -= (self.vy-HYPOTENUSE) * self.sprinting
        else:
            # print("Moving down and right")
            self.hcx += HYPOTENUSE * 10
            self.hcy -= (self.vy-HYPOTENUSE) * 10
            world.camera_follow.cam_cx += HYPOTENUSE * self.sprinting
            world.camera_follow.cam_cy -= (self.vy-HYPOTENUSE) * self.sprinting
            self.wcx += HYPOTENUSE * self.sprinting
            self.wcy -= (self.vy-HYPOTENUSE) * self.sprinting

    def move_left(self,in_camera):
        if in_camera:
            move_ticker = MOVE_COUNTER
            self.hcx -= self.vx * self.sprinting
            #self.cx = self.hcx
            self.wcx -= self.vx * self.sprinting
            # print("moving left")
            return move_ticker
        else:
            move_ticker = MOVE_COUNTER
            self.hcx -= self.vx * 10
            world.camera_follow.cam_cx -= self.vx * self.sprinting
            self.wcx -= self.vx * self.sprinting
            #print("moving left")
            return move_ticker
    def move_right(self,in_camera):
        if in_camera:
            move_ticker = MOVE_COUNTER
            self.hcx += self.vx * 10
            #self.cx = self.hcx
            self.wcx += self.vx * self.sprinting
            # print("moving right")
            return move_ticker
        else:
            move_ticker = MOVE_COUNTER
            self.hcx += self.vx * 10
            check = world.camera_follow.scan_for_player(self)
            #print(check)
            if check:
                self.move_right(check)
            world.camera_follow.cam_cx += self.vx * self.sprinting
            self.wcx += self.vx * self.sprinting
            #print("moving right")
            return move_ticker
    def decelerate(self):
        if self.vx < 0:
            self.vx += 0.1
        elif self.vx > 0:
            self.vx -= 0.1
        if self.vy > 0:
            self.vy -= 0.1
        elif self.vy < 0:
            self.vy += 0.1
    def draw(self):
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
        #print("Player drawn at",self.cx,self.cy)
    def update_health(self):
        if self.health > 0:
            self.colour = (0,255 * (self.max_health - self.health)/self.max_health,0)
            return False
        else:
            print("Game over")
            for widget in world.widgets:
                widget.active = False
            return True
    def fire_laser(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] + world.camera_follow.cam_cx, mouse_pos[1] + world.camera_follow.cam_cy)
        magnitude = math.sqrt((mouse_pos[0] - self.wcx)**2 + (mouse_pos[1] - self.wcy)**2)
        self.xstep = ((mouse_pos[0] - self.wcx)/magnitude) * 20
        self.ystep = ((mouse_pos[1] - self.wcy)/magnitude) * 20
        self.current_bulletx = self.wcx
        self.current_bullety = self.wcy
        self.laser_trail.append((self.current_bulletx,self.current_bullety))
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

        if debugging:
            for circle in self.laser_trail:
                pygame.draw.circle(screen, (123,123,123), (circle[0]-world.camera_follow.cam_cx,circle[1]-world.camera_follow.cam_cy),5)
        else:
            pygame.draw.line(screen, (11, 3, 252), (self.cx,self.cy),(self.laser_trail[-1][0]-world.camera_follow.cam_cx,self.laser_trail[-1][1]-world.camera_follow.cam_cy),10)



    def check_laser_hit(self,enemies):
        for enemy in enemies:
            for circle in self.laser_trail:
                circle = (circle[0]-world.camera_follow.cam_cx,circle[1]-world.camera_follow.cam_cy)
                if calc_distance_circle_and_point(enemy,circle) < 0:
                    enemy.health -= 5
        self.laser_trail = []

    def update_position(self):
        self.cx = self.wcx - world.camera_follow.cam_cx
        self.cy = self.wcy - world.camera_follow.cam_cy
        if self.in_camera:
            self.hcx = self.cx
            self.hcy = self.cy

    def decrease_laser_charge(self):
        if world.frames % (FPS/20) == 0:
            self.laser_charge -= 1

    def increase_laser_charge(self):
        if world.frames % FPS == 0:
            self.laser_charge += 1


class Player2 (Player):
    def __init__(self,cx,cy):
        super().__init__(cx,cy)


    def recv_and_send_data(self):
        '''


        data_to_proxy = f"{int(player.wcx)} {int(player.wcy)} {int(player2.health)}"
        print(f"Data to proxy {data_to_proxy}")
        enemy_data = ''
        print(f"world x:{player.wcx},world y: {player.wcy}, player1 health:{player.health}, player2 health:{player2.health}")
        for enemy in enemies:
            if enemy not in viruses:
                enemy_data_temp = f" {int(enemy.wcx)} {int(enemy.wcy)} {int(enemy.health)} e"
                enemy_data += enemy_data_temp
            else:
                enemy_data_temp = f" {int(enemy.wcx)} {int(enemy.wcy)} {int(enemy.health)} v"
                enemy_data += enemy_data_temp
        data_to_proxy += enemy_data
        #print(f"Received {data}")
        server_socket.send(data_to_proxy.encode())
        #print(data)
        #print(f"Sent {data_to_proxy}")
        try:
            data = server_socket.recv(1024)
        except socket.timeout:
            print("Connection timed out, starting singleplayer")
            singleplayer = True
            return singleplayer

        data = data.decode().split(" ")
        try:
            print(data)
            self.wcx = float(data[0])
            self.wcy = float(data[1])

            for enemy in enemies:
                enemy.health = int(data[enemies.index(enemy)+2])
        except:
            print("Data not sent")

        singleplayer = False
        return singleplayer
        '''
        pass


    def rectify(self):
        self.cx = self.wcx - world.camera_follow.cam_cx
        self.cy = self.wcy - world.camera_follow.cam_cy

        print(f"Original data: {self.wcx},{self.wcy}")
        print(f"Rectified data {self.cx} {self.cy}")

class Target:
    def __init__(self,wcx,wcy):
        self.cx = wcx + world.camera_follow.cam_cx
        self.cy = wcy + world.camera_follow.cam_cy
        self.wcx = wcx
        self.wcy = wcy
        self.radius = 5
        self.health = 100
        world.targets.append(self)

    def draw(self):
        pygame.draw.circle(screen, (255,123,123), (int(self.cx),int(self.cy)),self.radius)

class Enemy:
    def __init__(self,cx,cy,id):
        self.type = "e"
        self.id = id
        self.cx = cx
        self.cy = cy
        self.radius = 25
        self.wcx = cx
        self.wcy = cy
        self.vx = 0
        self.vy = 0
        self.SPEED = 3
        self.health = 100
        self.colour = (255,255,255)
        self.can_move = 1
        self.enemies_nearby = 0
        self.last_hit_time = -1
        self.image_list = []
        self.sword_stunned = False
        self.sword_target = Target(self.wcx,self.wcy)
        world.objects.append(self.sword_target)
        self.initialised = False
        for i in range(10):
            imp = pygame.image.load(f"./image/virus_death0{i}.png").convert_alpha()
            imp.set_colorkey((0, 0, 0))
            imp.convert_alpha()
            self.image_list.insert(0,imp)

    def take_damage_from_sword(self,sword_xvector,sword_yvector):
        print("enemy hit")
        self.health -= 30
        self.sword_target.wcx = self.wcx + sword_xvector *1000
        self.sword_target.wcy = self.wcy + sword_yvector *1000
        if self.health <= 0:
            world.player.laser_charge += 5
            if world.player.laser_charge > 100:
                world.player.laser_charge = 100

    def recover_from_sword(self):
        if self.initialised == False:
            self.current_time = world.seconds + 0.5
            self.initialised = True
        if world.seconds > self.current_time:
            self.initialised = False
            self.sword_stunned = False


    def evaluate_health(self):
        if self.health <= 0:
            self.can_move = 0
            if self in world.enemies:
                world.enemies.remove(self)
                world.enemies_defeated_count += 1
                world.bacteria_defeated_count += 1

    def scan_for_friendlies(self,enemies):
        self.enemies_nearby = 0
        for enemy in enemies:
            if calc_distance(self,enemy) < 5 and enemy.health > 0:
                self.enemies_nearby += 1


    def draw(self):
        if 100 >= (self.health) >= 1:
            self.colour = (255, 255 * (self.health / 100), 255)
            screen.blit(self.image_list[self.health // 11], (self.cx - 32, self.cy - 32))
            # print(self.image_list)
        if debugging:
            pygame.draw.circle(screen, self.colour, (self.cx, self.cy),self.radius)

    def beeline(self,player):
        angle = math.pi

        if player.cx - self.cx != 0:
            angle = math.atan((player.cy - self.cy)/(player.cx - self.cx))

        #print(angle/math.pi*180)
        self.vx = -self.SPEED * math.cos(angle)
        self.vy = -self.SPEED * math.sin(angle)

        if self.cx > player.cx:
            self.wcx += self.vx * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
            self.wcy += self.vy * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
        else:
            self.wcx -= self.vx * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
            self.wcy -= self.vy * self.can_move * (1 + ((self.enemies_nearby) * 0.2))

        if calc_distance(self,player) < 10 and self.health > 0:
            if world.seconds > (self.last_hit_time + 0.7):
                player.health -= 2
                self.last_hit_time = world.seconds
                #print("player hit")
        '''
        if calc_distance(self,player2) < 10 and self.health > 0:
            if seconds > (self.last_hit_time + 0.7):
                player2.health -= 2
                self.last_hit_time = seconds
                print("player hit")
        '''


class Virus(Enemy):
    def __init__(self,enemy_id):
        super().__init__(random.randint(0,500),random.randint(0,500),enemy_id)
        self.target = Target(0,0)
        self.clone_cooldown = 0
        self.colour = (255,0,0)
        self.deciding_where = False
        self.type = "v"
        self.tx = 0
        self.ty = 0
        self.counter = 0
        self.SPEED = 1
    def draw(self):
        pygame.draw.circle(screen, self.colour, (self.cx, self.cy),self.radius)

    def evaluate_health(self):
        if 100 >= (self.health) >= 1:
            self.colour =(self.colour[0],255 * (self.health / 100),self.colour[2])
        if self.health <= 0:
            self.can_move = 0
            if self in world.enemies:
                world.enemies.remove(self)
                world.enemies_defeated_count += 1
                world.viruses_defeated_count += 1

    def clone_if_can(self,enemies,enemy_id):
        if self.clone_cooldown <= 0:
            self.clone_cooldown = 5
            enemies.insert(0,Enemy(self.wcx,self.wcy,enemy_id))
            enemy_id += 1
            world.objects.append(enemies[0])

        return enemy_id

    def decrement_cooldown(self):
        self.clone_cooldown -= (1/FPS)

    def get_target(self):
        self.tx = random.randint(-30, 30) * 45
        self.ty = random.randint(-30, 30) * 45
        self.target = Target(self.wcx + self.tx, self.wcy + self.ty)
        self.deciding_where = False
        self.counter = 3


class Grenade_v2:
    def __init__(self):
        self.cx = 0
        self.cy = 0
        self.radius = 100
        self.actual_radius = 5
        self.detonation_time = 3
        self.colour = (123,123,123)
        self.exploded = False
        self.thrown = False
        self.pos = ()
        self.dx = 0
        self.dy = 0
        self.target = (0,0)

    def cook(self):
        self.cx = world.player.cx
        self.cy = world.player.cy
        self.wcx = world.player.wcx
        self.wcy = world.player.wcy
        print("cooking")
        self.detonation_time -= (1/FPS)
        pygame.draw.circle(screen, self.colour, (self.cx, self.cy),self.actual_radius)
        if self.detonation_time <= 0:
            print("Exploding in hand")
            self.explode()

    def throw(self,player,target=(0,0)):
        if not self.thrown:
            self.wcx = player.wcx
            self.wcy = player.wcy
            self.thrown = True
            self.pos = (self.cx,self.cy)
            self.dy = target[1] - self.wcy
            self.dx = target[0] - self.wcx

            world.grenades_launched_count += 1

            magnitude = math.sqrt((self.dx ** 2) + (self.dy ** 2))
            self.dy = (self.dy / magnitude) * 5
            self.dx = (self.dx / magnitude) * 5

            self.target = (target[0],target[1])

        print("throwing",self.thrown)
        pygame.draw.circle(screen, self.colour, (self.cx,self.cy),self.actual_radius)
        self.dy = self.dy * 0.99
        self.dx = self.dx * 0.99
        #print(target)
        print(self.pos)
        self.detonation_time -= (1/FPS)
        if self.detonation_time <= 0:
            #print("Exploding while travelling")
            self.thrown = False
            self.explode()
        for i in range(len(world.enemies)):
            if calc_distance(self,world.enemies[i]) < -95 and player.health > 0:
                self.thrown = False
                #print("Exploding on collision")
                self.explode()
        for i in range(len(world.trees)):
            if calc_distance(self,world.trees[i]) < -95 and player.health > 0:
                self.thrown = False
                self.explode()

        self.wcx += self.dx
        self.wcy += self.dy
        self.cx += self.dx
        self.cy += self.dy

        self.pos = (self.wcx,self.wcy)

        return target

    def explode(self):
        print("exploding")
        self.exploded = True
        pygame.draw.circle(screen, self.colour, (self.cx, self.cy), self.radius)
        for enemy in world.enemies:
            if calc_distance(self, enemy) < 0:
                enemy.health = enemy.health - 30
                if enemy.health <= 0:
                    world.player.laser_charge += 5
                    if world.player.laser_charge > 100:
                        world.player.laser_charge = 100
        if calc_distance(self, world.player) < 0:
            world.player.health = world.player.health - 30

class Bullet_trail:
    def __init__(self):
        self.cx = 0
        self.cy = 0
        self.radius = 5
        self.color = (125,125,125)
        self.bullet_trail = []
        self.deadly_bullet = ()
        self.current_bulletx = 0
        self.current_bullety = 0
        self.fire_rate = 0

    def check_hit(self, enemies):
        scanning_for_trees = True
        found = False
        index = 0
        got_hit_this_frame = False
        while not found and index < len(self.bullet_trail):

            for i in range(len(enemies)-1,-1,-1):
                if (calc_distance_circle_and_point(enemies[i], self.bullet_trail[index]) <= 0 and got_hit_this_frame == False):
                    enemies[i].health -= 20
                    if enemies[i].health <= 0:
                        world.player.laser_charge += 5
                        if world.player.laser_charge > 100:
                            world.player.laser_charge = 100
                    #print(enemy.health)
                    #print("oof")
                    #print(enemy.colour)
                    found = True
                    self.deadly_bullet = self.bullet_trail[index]
                    got_hit_this_frame = True

            for i in range(len(world.trees)-1,-1,-1):
                if calc_distance_circle_and_point(world.trees[i],self.bullet_trail[index]) <= 0:
                    found=True
                    self.deadly_bullet = self.bullet_trail[index]
                    got_hit_this_frame = True
                    print("Hit tree")

            else:
                index += 1
        try:
            if not found:
                self.deadly_bullet = self.bullet_trail[-1]
        except:
            self.deadly_bullet = ()

    def create_shot(self,player,destination,fire_rate):
        world.shots_fired_count += 1
        if self.fire_rate <= 0:
            self.fire_rate = fire_rate
            magnitude = math.sqrt((destination[0] - player.cx) ** 2 + (destination[1] - player.cy) ** 2)
            self.xstep = ((destination[0] - player.cx) / magnitude) * 20
            self.ystep = ((destination[1] - player.cy) / magnitude) * 20
            self.current_bulletx = player.cx
            self.current_bullety = player.cy
            self.bullet_trail.append((self.current_bulletx, self.current_bullety))

            for i in range(20):
                self.current_bulletx += self.xstep
                self.current_bullety += self.ystep
                self.bullet_trail.append((self.current_bulletx, self.current_bullety))
    def decrement_cooldown(self,fire_rate):
        self.fire_rate = self.fire_rate - (1/FPS)


    def draw(self, player):
        if debugging:
            for bullet in self.bullet_trail:
                pygame.draw.circle(screen, (123,123,123), (bullet[0],bullet[1]), 3)
        else:
            pygame.draw.line(screen,(238, 255, 0),(player.cx,player.cy),(self.deadly_bullet[0],self.deadly_bullet[1]),4)

    def clean_shot(self):
        self.bullet_trail = []


class GameWorld:
    def __init__(self):
        self.seconds_passed = 0
        self.current_time = 0
        self.initializing_next_wave = True
        self.objects = []
        self.keys = pygame.key.get_pressed()
        self.player = Player(600,300)
        self.sword = Sword()
        self.island = Island((0, 255, 60,50),1000,750,450)
        self.enemies = []
        self.viruses = []
        self.current_enemy_id = 0
        self.trees = [Tree(random.randint(-200,1550),random.randint(-350,1250)) for i in range(15)] # How many trees
        self.targets = []
        self.key_g_held_down = False
        self.key_g_not_pressed = True
        self.active_grenades = []
        self.camera_follow = BoundingBox()
        self.health_bar = Health_bar()
        self.current_wave = 1
        self.victory = False

        self.widgets = []
        self.active_widgets = []


        self.laser_charge_text_box = Text_box(600,750,300,100,(255,255,255),str(self.player.laser_charge)+"%",False,self)
        self.laser_charge_text_box.active = False

        self.players = [self.player]
        self.frames = 0
        self.seconds = 0
        self.text_surface = None
        self.bullet_system = Bullet_trail()


        self.ss = pygame.mixer.Sound(os.path.join('sounds', 'SneSni.wav'))
        self.am = pygame.mixer.Sound(os.path.join('sounds', 'AMis.wav'))
        self.fad = pygame.mixer.Sound(os.path.join('sounds', 'FluaDuc.wav'))
        self.qd = pygame.mixer.Sound(os.path.join('sounds', 'QuiDog.wav'))
        self.SoTI = pygame.mixer.Sound(os.path.join('sounds', 'SoTI.wav'))
        self.music_played = False



        self.start_button = StartButton(450,600,300,100,(255,255,255),"start",self)

        self.settings_button = SettingsButton(850,600,300,100,(255,255,255),"settings",self)
        self.settings_open = False

        self.enemies_text_box = Text_box(450,300,300,75,(255,255,255),"enemies",False,self)
        self.enemies_counter = Text_box(550,400,100,50,(255,255,255),"1",True,self)

        self.viruses_text_box = Text_box(450,500,300,75,(255,255,255),"viruses",False,self)
        self.viruses_counter = Text_box(550,600,100,50,(255,255,255),"0",True,self)
        self.virus_count = int(self.viruses_counter.text)

        self.back_button = BackButton(50,50,100,70,(255,255,255),"<",self)

        self.congrats = Text_box(450,100,200,100,(255,255,255),"congrats",False,self)

        self.you_lose = Text_box(450,100,200,100,(255,255,255),"you lose",False,self)

        self.enemies_defeated = Text_box(450,200,500,100,(255,255,255),"Enemies defeated: 0",False,self)
        self.enemies_defeated_count = 0

        self.grenades_launched = Text_box(450,300,500,100,(255,255,255),"Grenades launched: 0",False,self)
        self.grenades_launched_count = 0

        self.viruses_defeated = Text_box(450,400,500,100,(255,255,255),"Viruses defeated: 0",False,self)
        self.viruses_defeated_count = 0

        self.bacteria_defeated = Text_box(450,500,500,100,(255,255,255),"Bacteria defeated: 0",False,self)
        self.bacteria_defeated_count = 0

        self.shots_fired = Text_box(450,600,500,100,(255,255,255),"Shots fired: 0",False,self)
        self.shots_fired_count = 0

        self.waves_reached = Text_box(450,700,500,100,(255,255,255),"Wave reached: 1",False,self)

        self.wave_text_box = Text_box(50,25,250,50,(255,255,255),"wave 1",False,self)
        self.wave_text_box.active = False
        self.next_wave_time = Text_box(50,100,200,75,(255,255,255),"0:05",False,self)
        self.next_wave_time.active = False

        self.msf = Text_box(900,300,500,100,(255,255,255),"Are you sure about this?",False,self)
        self.emsf = Text_box(900,450,500,100,(255,255,255),"The game is going to be impossible",False,self)
        self.eemsf = Text_box(900,600,500,100,(255,255,255),"Well, you asked for it",False,self)

    def handle_inputs(self):
        global running, main_menu
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.bullet_system.create_shot(self.player, pygame.mouse.get_pos(), 0.1)
                    self.bullet_system.check_hit(self.enemies)

                    self.handle_buttons()
                    # print(enemy.health)

                if event.button == 3:
                    mouse_pos = pygame.mouse.get_pos()

                    self.sword.xvector = mouse_pos[0] - self.player.cx
                    self.sword.yvector = mouse_pos[1] - self.player.cy

                    magnitude = math.sqrt(self.sword.xvector ** 2 + self.sword.yvector ** 2)

                    self.sword.xvector = self.sword.xvector / magnitude
                    self.sword.yvector = self.sword.yvector / magnitude

                    self.sword.cx = self.player.cx + (self.sword.xvector * 30)
                    self.sword.cy = self.player.cy + (self.sword.yvector * 30)
                    self.sword.wcx = self.player.wcx + (self.sword.xvector * 30)
                    self.sword.wcy = self.player.wcy + (self.sword.yvector * 30)

                    self.sword.draw()
                    self.sword.check_hit(self.enemies)

        self.key_g_held_down,self.key_g_not_pressed = self.handle_grenade_logic(self.key_g_held_down, self.key_g_not_pressed)

        self.handle_laser_inputs()

        self.handle_movement() # Handles player movement

    def initialize_enemies(self,enemy_count,virus_count):
        for i in range(enemy_count):  # How many enemies
            self.enemies.append(Enemy(random.randint(0, 750), random.randint(0, 450), self.current_enemy_id))
            self.current_enemy_id += 1

        for i in range(virus_count):  # How many viruses
            self.viruses.append(Virus(self.current_enemy_id))
            self.current_enemy_id += 1

    def update_collision_hitboxes(self):
        self.player.left = (self.player.cx - 25, self.player.cy)
        self.player.up = (self.player.cx, self.player.cy - 25)
        self.player.right = (self.player.cx + 25, self.player.cy)
        self.player.down = (self.player.cx, self.player.cy + 25)
        self.player.upleft = (self.player.cx - 18, self.player.cy - 18)
        self.player.downright = (self.player.cx + 18, self.player.cy + 18)
        self.player.downleft = (self.player.cx - 18, self.player.cy + 18)
        self.player.upright = (self.player.cx + 18, self.player.cy - 18)

    def display_menu(self):
        global running,main_menu,menu_screen
        menu_screen.fill((255, 212, 45))
        self.draw_buttons(menu_screen)
        screen.blit(menu_screen,(0,0))
        self.active_widgets = []

        for button in self.widgets:
            if button.active:
                self.active_widgets.append(button)
                if button.adjustable:
                    self.active_widgets.append(button.plus_button)
                    self.active_widgets.append(button.minus_button)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_buttons()

        if self.player.health <= 0:
            self.music_played = False
            self.handle_soundtrack()

        if int(self.viruses_counter.text) + int(self.enemies_counter.text) >= 27 and self.settings_open:
            self.msf.active = True
        else:
            self.msf.active = False
        if int(self.viruses_counter.text) + int(self.enemies_counter.text) >= 37 and self.settings_open:
            self.emsf.active = True
        else:
            self.emsf.active = False
        if int(self.viruses_counter.text) + int(self.enemies_counter.text) >= 47 and self.settings_open:
            self.eemsf.active = True
        else:
            self.eemsf.active = False
    def draw_island_and_background(self):
        screen.fill((107, 191, 255))
        self.island.draw()

    def draw_enemies_player_and_trees(self):
        if debugging:
            self.camera_follow.draw()
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        for tree in self.trees:
            tree.draw()

    def handle_sword_logic(self):
        for enemy in self.enemies:
            if debugging:
                enemy.sword_target.draw()
            if not enemy.sword_stunned:
                if enemy.type == "e":
                    enemy.beeline(self.player)
                else:
                    enemy.SPEED = 1
                    if enemy.deciding_where:
                        enemy.target = Target(enemy.wcx + 45*random.randint(-30,30),enemy.wcy + 45*random.randint(-30, 30))
                        self.objects.append(enemy.target)
                        enemy.counter = 3
                        enemy.deciding_where = False
                        if calc_distance(enemy.target,self.island) > 0:
                            enemy.deciding_where = True
                    else:
                        if debugging:
                            enemy.target.draw()
                        enemy.beeline(enemy.target)
                        enemy.counter -= (1/FPS)
                        if enemy.counter <= 0:
                            enemy.deciding_where = True
            else:
                enemy.SPEED = 3
                enemy.beeline(enemy.sword_target)  # Composition
                enemy.recover_from_sword()

    def handle_grenade_logic(self, key_g_held_down, key_g_not_pressed):
        mouse_pos = (0,0)
        if key_g_held_down and key_g_not_pressed:
            print("Created grenade")
            self.active_grenades.append(Grenade_v2())
            self.objects.append(self.active_grenades[-1])
            key_g_not_pressed = False
        if key_g_held_down and self.active_grenades:
            print("Grenade cooking")
            self.active_grenades[-1].cook()
        if self.keys[pygame.K_g]:
            key_g_held_down = True
        else:
            key_g_held_down = False
        if not key_g_held_down and key_g_not_pressed == False:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (mouse_pos[0] + self.camera_follow.cam_cx, mouse_pos[1] + self.camera_follow.cam_cy)
            print("Key g just released")
            if self.active_grenades:
                self.active_grenades[-1].throw(self.player, mouse_pos)
            key_g_not_pressed = True

        for grenade in self.active_grenades:
            if grenade.exploded:
                print("Grenade exploded")
                self.active_grenades.remove(grenade)
            elif grenade.thrown:
                grenade.throw(self.player, mouse_pos)

        return key_g_held_down, key_g_not_pressed

    def handle_laser_inputs(self):
        if self.keys[pygame.K_f] and self.player.laser_charge > 50:
            self.player.firing_laser = True
        if self.player.firing_laser:
            self.player.fire_laser()
            self.player.check_laser_hit(self.enemies)
            self.player.decrease_laser_charge()
        if not self.keys[pygame.K_f] or self.player.laser_charge <= 0:
            self.player.firing_laser = False
        if not self.player.firing_laser and self.player.laser_charge <= 99:
            self.player.increase_laser_charge()

    def handle_movement(self):
        if self.keys[pygame.K_LSHIFT]:
            self.player.sprinting = 2
        else:
            self.player.sprinting = 1
        self.player.check_walkable(self.trees)
        move_ticker = 0
        if self.keys[
            pygame.K_w] and self.player.up_walkable and self.player.upright_walkable and self.player.upleft_walkable:
            if move_ticker == 0:
                move_ticker = self.player.move_up(self.player.in_camera)

                if self.keys[
                    pygame.K_a] and self.player.left_walkable and self.player.upleft_walkable and self.player.downleft_walkable:
                    self.player.move_up_and_left(self.player.in_camera)
                if self.keys[
                    pygame.K_d] and self.player.right_walkable and self.player.upright_walkable and self.player.downright_walkable:
                    self.player.move_up_and_right(self.player.in_camera)
        if self.keys[
            pygame.K_s] and self.player.down_walkable and self.player.downleft_walkable and self.player.downright_walkable:
            if move_ticker == 0:
                move_ticker = self.player.move_down(self.player.in_camera)
                # print("Moving down")
                if self.keys[
                    pygame.K_a] and self.player.left_walkable and self.player.upleft_walkable and self.player.downleft_walkable:
                    self.player.move_down_and_left(self.player.in_camera)
                if self.keys[
                    pygame.K_d] and self.player.right_walkable and self.player.upright_walkable and self.player.downright_walkable:
                    self.player.move_down_and_right(self.player.in_camera)
        if self.keys[
            pygame.K_a] and self.player.left_walkable and self.player.upleft_walkable and self.player.downleft_walkable:
            if move_ticker == 0:
                move_ticker = self.player.move_left(self.player.in_camera)
        if self.keys[
            pygame.K_d] and self.player.right_walkable and self.player.upright_walkable and self.player.downright_walkable:
            if move_ticker == 0:
                move_ticker = self.player.move_right(self.player.in_camera)

    def update_frames_and_time(self):
        self.frames = self.frames + 1
        self.seconds = self.frames / FPS

    def update_item_positions_relative_to_camera(self):
        for item in self.objects:
            item.cx = item.wcx - self.camera_follow.cam_cx
            item.cy = item.wcy - self.camera_follow.cam_cy

    def reset_and_prepare_for_next_frame(self):
        global main_menu
        self.bullet_system.clean_shot()
        main_menu = self.player.update_health()
        self.health_bar.draw()

        self.active_widgets = []

        for button in self.widgets:
            if button.active:
                self.active_widgets.append(button)

        #print(self.active_widgets)

        for button in self.active_widgets:
            button.draw(screen)

        self.laser_charge_text_box.update(str(self.player.laser_charge) + "%")

        for enemy in self.enemies:
            enemy.evaluate_health()
            enemy.scan_for_friendlies(self.enemies)
            # print(enemy.health)
        for virus in self.viruses:
            if virus.health > 0:
                self.current_enemy_id = virus.clone_if_can(self.enemies, self.current_enemy_id)
                virus.decrement_cooldown()
            virus.evaluate_health()
            virus.scan_for_friendlies(self.enemies)
        self.camera_follow.scan_for_player(self.player)
        self.update_collision_hitboxes()
        self.player.walking_spots = [self.player.left, self.player.right, self.player.down, self.player.up,
                                      self.player.upleft, self.player.downleft, self.player.downright,
                                      self.player.upright]
        if not self.player.in_camera:
            self.player.hcx = self.player.cx
            self.player.hcy = self.player.cy

        self.bullet_system.decrement_cooldown(0.1)

        if not self.enemies:
            if self.initializing_next_wave:
                print("Wave cleared")
                self.next_wave_time.active = True
                self.current_time = self.seconds
                self.initializing_next_wave = False
                self.next_wave_time.active = True
            if (self.seconds - self.current_time) >= 1:
                self.current_time = self.seconds
                self.seconds_passed += 1
                self.next_wave_time.update(f"0:0{int(5 - self.seconds_passed)}")
                if self.seconds_passed >= 5:
                    self.seconds_passed = 0
                    self.next_wave_time.update(f"0:0{int(5 - self.seconds_passed)}")
                    self.current_wave += 1
                    self.waves_reached.update(f"Waves reached: {self.current_wave}")
                    if self.current_wave == 11:
                        print("Victory")
                        self.victory = True
                        main_menu = True
                    self.wave_text_box.update(f"wave {self.current_wave}")
                    if (self.current_wave + 1) % 2 == 0:
                        self.virus_count += 1
                        self.music_played = False
                    self.next_wave_time.active = False
                    self.initializing_next_wave = True
                    self.enemies_counter.text = str(int(self.enemies_counter.text) + 1)
                    self.viruses_counter.text = str(int(self.viruses_counter.text) + 1)
                    self.initialize_enemies(int(world.enemies_counter.text), int(world.viruses_counter.text))
                    self.objects = []
                    self.initialise_world_objects()

        if main_menu:
            self.grenades_launched.update("Grenades launched: "+str(self.grenades_launched_count))
            self.shots_fired.update("Shots fired: "+str(self.shots_fired_count))
            self.enemies_defeated.update("Enemies defeated: "+str(self.enemies_defeated_count))
            self.bacteria_defeated.update("Bacteria defeated: "+str(self.bacteria_defeated_count))
            self.viruses_defeated.update("Viruses defeated: "+str(self.viruses_defeated_count))

        if self.victory:
            print("You win")
            for widget in self.widgets:
                widget.active = False
            self.congrats.active = True
            self.grenades_launched.active = True
            self.enemies_defeated.active = True
            self.bacteria_defeated.active = True
            self.viruses_defeated.active = True
            self.shots_fired.active = True

        if main_menu and not self.victory:
            print("You lose")
            for widget in self.widgets:
                widget.active = False
            self.you_lose.active = True
            self.grenades_launched.active = True
            self.enemies_defeated.active = True
            self.bacteria_defeated.active = True
            self.viruses_defeated.active = True
            self.shots_fired.active = True
            self.waves_reached.active = True





    def draw_bullet_trail(self):
        if len(self.bullet_system.bullet_trail) > 0:
            self.bullet_system.draw(self.player)

    def allow_debug_options(self):
        if self.keys[pygame.K_UP]:
            self.player.in_camera = False
        if self.keys[pygame.K_h]:
            self.player.cx = 600
            self.player.cy = 300
            self.player.hcx = 600
            self.player.hcy = 300
            self.player.wcx = 600
            self.player.wcy = 300
            self.camera_follow.cam_cx = 0
            self.camera_follow.cam_cy = 0
        pygame.draw.circle(screen, (255, 50, 255), (self.player.hcx, self.player.hcy), 10)

    def initialise_world_objects(self):
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
        for button in self.active_widgets:
            button.draw(screen)

    def handle_buttons(self):
        for button in self.active_widgets:
            if button.rect.collidepoint(pygame.mouse.get_pos()):
                button.execute_command()

    def open_settings(self):
        for widget in self.widgets:
            widget.active = False

        self.enemies_text_box.active = True
        self.enemies_counter.active = True
        self.back_button.active = True
        self.viruses_counter.active = True
        self.viruses_text_box.active = True
        self.settings_open = True

    def handle_soundtrack(self):
        if self.music_played == False:
            pygame.mixer.stop()
            self.music_played = True
            if self.player.health <= 0:
                pass
            elif 1 <= self.current_wave <= 2:
                self.ss.play(-1)
                print("Playing ss")
            elif 3 <= self.current_wave <= 4:
                self.fad.play(-1)
                print("fad")
            elif 5 <= self.current_wave <= 6:
                self.qd.play(-1)
                print("qd")
            elif 7 <= self.current_wave <= 8:
                self.am.play(-1)
                print("am")
            else:
                self.SoTI.play(-1)
                print("SoTIs")


world = GameWorld()
singleplayer = True
main_menu = True


while running:

    if main_menu:
        world.display_menu()
    else:
        world.update_frames_and_time()

        world.draw_island_and_background()

        world.handle_inputs() #Handles left click, right click, g key, f key and movement

        world.draw_bullet_trail()

        world.draw_enemies_player_and_trees()

        world.handle_sword_logic()

        world.keys = pygame.key.get_pressed()

        world.player.update_position()

        world.player.walking_spot_permissions = [True for i in range(8)]

        world.update_item_positions_relative_to_camera()

        world.draw_buttons(screen)

        if debugging:
            world.allow_debug_options() # Eg press h to return to initial positions

        world.reset_and_prepare_for_next_frame()

        world.handle_soundtrack()

        fpsClock.tick(FPS)
    pygame.display.flip()

pygame.quit()