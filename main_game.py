import pygame
import math
import random
import socket

HYPOTENUSE = 2.121

IP = "127.0.0.1"
PORT = 8000

pygame.init()

screen = pygame.display.set_mode((1500, 900))

running = True

debugging = True

FPS = 60
fpsClock = pygame.time.Clock()
pygame.display.set_caption("Server")

def calc_distance(pointA, pointB):
    return math.sqrt((pointA.wcx - pointB.wcx)**2 + (pointA.wcy - pointB.wcy)**2) - pointA.radius - pointB.radius

def calc_distance_circle_and_point(pointA, pointB):
    return math.sqrt((pointA.wcx - pointB[0]-camera_follow.cam_cx)**2 + (pointA.wcy - pointB[1] - camera_follow.cam_cy)**2) - pointA.radius

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
        if debugging:
            pygame.draw.circle(screen, (self.colour),(self.cx,self.cy),self.radius)

    def check_hit(self,enemies):
        for enemy in enemies:
            if calc_distance(enemy,self) <= 0:
                enemy.take_damage_from_sword(sword.xvector,sword.yvector)
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
    def __init__(self,lx=450,ty=200,width=600,height=500,screen=screen):
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
        else:
            player.in_camera = False

class Health_bar():
    def __init__(self):
        self.cx = 5
        self.cy = (screen.get_height()-65)
        self.width = 200
        self.height = 50

    def draw(self):
        pygame.draw.rect(screen,(0,0,0),(self.cx,self.cy,self.width,self.height))
        pygame.draw.rect(screen,(255,0,0),(self.cx,self.cy,self.width-((1-player.health/100)*self.width),self.height))


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

        #For collision
        self.left = (self.cx - 30,self.cy)
        self.up = (self.cx,self.cy - 10)
        self.right = (self.cx + 10,self.cy)
        self.down = (self.cx,self.cy+10)
        self.upleft = (self.cx,self.cy)
        self.upright = (self.cx,self.cy)
        self.downleft = (self.cx,self.cy)
        self.downright = (self.cx,self.cy)
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
            if calc_distance_circle_and_point(island,self.walking_spots[i]) >= self.collision_radius:
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
            move_ticker = 10
            self.hcy -= 3 * self.sprinting
            self.cy = self.hcy
            self.wcy -= 3 * self.sprinting
            # print("Moving up",self.cx,self.cy)
            return move_ticker
        else:
            move_ticker = 10
            self.hcy -= 3 * self.sprinting
            camera_follow.cam_cy -= 3 * self.sprinting
            self.wcy -= 3 * self.sprinting
            # print("Moving up",self.cx,self.cy)
            return move_ticker
    def move_up_and_right(self,in_camera):
        if in_camera:
            self.hcx += HYPOTENUSE * self.sprinting
            self.hcy += 0.879 * self.sprinting
            self.cx = self.hcx
            self.wcx += HYPOTENUSE * self.sprinting
            self.wcy += 0.879 * self.sprinting
            # print("Moving up and right")
        else:
            self.hcx += HYPOTENUSE * self.sprinting
            self.hcy += 0.879 * self.sprinting
            camera_follow.cam_cx += HYPOTENUSE * self.sprinting
            camera_follow.cam_cy += 0.879 * self.sprinting
            self.wcx += HYPOTENUSE * self.sprinting
            self.wcy += 0.879 * self.sprinting
            # print("Moving up and right")
    def move_up_and_left(self,in_camera):
        if in_camera:
            self.hcx -= HYPOTENUSE * self.sprinting
            self.hcy += 0.879 * self.sprinting
            self.cx = self.hcx
            self.wcx -= HYPOTENUSE * self.sprinting
            self.wcy += 0.879 * self.sprinting
            # print("Moving up and left")
        else:
            self.hcx -= HYPOTENUSE * self.sprinting
            self.hcy += 0.879 * self.sprinting
            camera_follow.cam_cx -= HYPOTENUSE * self.sprinting
            camera_follow.cam_cy += 0.879 * self.sprinting
            self.wcx -= HYPOTENUSE * self.sprinting
            self.wcy += 0.879 * self.sprinting
            # print("Moving up and left")
    def move_down(self,in_camera):
        if in_camera:
            move_ticker = 10
            self.hcy += 3 * self.sprinting
            self.cy = self.hcy
            self.wcy += 3 * self.sprinting
            return move_ticker
        else:
            move_ticker = 10
            self.hcy += 3 * self.sprinting
            camera_follow.cam_cy += 3 * self.sprinting
            self.wcy += 3 * self.sprinting
            # print("Moving down")
            return move_ticker
    def move_down_and_left(self,in_camera):
        if in_camera:
            self.hcx -= HYPOTENUSE * self.sprinting
            self.hcy -= 0.879 * self.sprinting
            self.cx = self.hcx
            self.wcx -= HYPOTENUSE * self.sprinting
            self.wcy -= 0.879 * self.sprinting
            # print("Moving down and left")
        else:
            self.hcx -= HYPOTENUSE * self.sprinting
            self.hcy -= 0.879 * self.sprinting
            camera_follow.cam_cx -= HYPOTENUSE * self.sprinting
            camera_follow.cam_cy -= 0.879 * self.sprinting
            self.wcx -= HYPOTENUSE * self.sprinting
            self.wcy -= 0.879 * self.sprinting
            # print("Moving left and down")
    def move_down_and_right(self,in_camera):
        if in_camera:
            # print("Moving down and right")
            self.hcx += HYPOTENUSE * self.sprinting
            self.hcy -= 0.879 * self.sprinting
            self.cx = self.hcx
            self.wcx += HYPOTENUSE * self.sprinting
            self.wcy -= 0.879 * self.sprinting
        else:
            # print("Moving down and right")
            self.hcx += HYPOTENUSE * self.sprinting
            self.hcy -= 0.879 * self.sprinting
            camera_follow.cam_cx += HYPOTENUSE * self.sprinting
            camera_follow.cam_cy -= 0.879 * self.sprinting
            self.wcx += HYPOTENUSE * self.sprinting
            self.wcy -= 0.879 * self.sprinting
    def move_left(self,in_camera):
        if in_camera:
            move_ticker = 10
            self.hcx -= 3 * self.sprinting
            self.cx = self.hcx
            self.wcx -= 3 * self.sprinting
            # print("moving left")
            return move_ticker
        else:
            move_ticker = 10
            self.hcx -= 3 * self.sprinting
            camera_follow.cam_cx -= 3 * self.sprinting
            self.wcx -= 3 * self.sprinting
            #print("moving left")
            return move_ticker
    def move_right(self,in_camera):
        if in_camera:
            move_ticker = 10
            self.hcx += 3 * self.sprinting
            self.cx = self.hcx
            self.wcx += 3 * self.sprinting
            # print("moving right")
            return move_ticker
        else:
            move_ticker = 10
            self.hcx += 3 * self.sprinting
            camera_follow.cam_cx += 3 * self.sprinting
            self.wcx += 3 * self.sprinting
            print("moving right")
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
            return True
    def fire_laser(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos = (mouse_pos[0] + camera_follow.cam_cx, mouse_pos[1] + camera_follow.cam_cy)
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
                pygame.draw.circle(screen, (123,123,123), (circle[0]-camera_follow.cam_cx,circle[1]-camera_follow.cam_cy),5)
        else:
            pygame.draw.line(screen, (11, 3, 252), (self.cx,self.cy),(self.laser_trail[-1][0]-camera_follow.cam_cx,self.laser_trail[-1][1]-camera_follow.cam_cy),10)



    def check_laser_hit(self,enemies):
        for enemy in enemies:
            for circle in self.laser_trail:
                circle = (circle[0]-camera_follow.cam_cx,circle[1]-camera_follow.cam_cy)
                if calc_distance_circle_and_point(enemy,circle) < 0:
                    enemy.health -= 5
        self.laser_trail = []



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
        self.cx = self.wcx - camera_follow.cam_cx
        self.cy = self.wcy - camera_follow.cam_cy

        print(f"Original data: {self.wcx},{self.wcy}")
        print(f"Rectified data {self.cx} {self.cy}")

class Target:
    def __init__(self,cx,cy):
        self.cx = cx
        self.cy = cy
        self.wcx = cx
        self.wcy = cy
        self.radius = 5
        self.health = 100

    def draw(self):
        pygame.draw.circle(screen, (255,123,123), (int(self.cx),int(self.cy)),self.radius)

class Enemy:
    def __init__(self,cx,cy,id):
        self.id = id
        self.cx = cx
        self.cy = cy
        self.radius = 25
        self.wcx = cx
        self.wcy = cy
        self.vx = 0
        self.vy = 0
        self.health = 100
        self.colour = (255,255,255)
        self.got_hit_this_frame = False
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
    '''
    def get_hit(self,bullets):
        found = False
        index = 0
        while not found and index < len(bullets):
            if calc_distance_circle_and_point(self, bullets[index]) <= 0 and self.got_hit_this_frame == False:
                self.health -= 20
                self.got_hit_this_frame = True
                print("oof")
                print(self.colour)
                found = True
            else:
                index += 1
    '''
    def take_damage_from_sword(self,sword_xvector,sword_yvector):
        print("enemy hit")
        self.health -= 30
        self.got_hit_this_frame = True
        self.sword_target.wcx = self.wcx + sword_xvector *1000
        self.sword_target.wcy = self.wcy + sword_yvector *1000

    def recover_from_sword(self):
        if self.initialised == False:
            self.current_time = seconds + 0.5
            self.initialised = True
        if seconds > self.current_time:
            self.initialised = False
            self.sword_stunned = False


    def evaluate_health(self):
        if 100 >= (self.health) >= 1:
            self.colour =(255,255 * (self.health / 100),255)
            screen.blit(self.image_list[self.health//11], (self.cx-32,self.cy-32))
            #print(self.image_list)
        if self.health <= 0:
            self.can_move = 0
            if self in enemies:
                enemies.remove(self)

    def clean_up(self):
        self.got_hit_this_frame = False

    def scan_for_friendlies(self,enemies):
        self.enemies_nearby = 0
        for enemy in enemies:
            if calc_distance(self,enemy) < 5 and enemy.health > 0:
                self.enemies_nearby += 1


    def draw(self):
        if debugging:
            pygame.draw.circle(screen, self.colour, (self.cx, self.cy),self.radius)

    def beeline(self,player):
        angle = math.pi

        if player.cx - enemy.cx != 0:
            angle = math.atan((player.cy - enemy.cy)/(player.cx - enemy.cx))
        #print(angle/math.pi*180)
        self.vx = -3 * math.cos(angle)
        self.vy = -3 * math.sin(angle)

        if enemy.cx > player.cx:
            self.wcx += self.vx * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
            self.wcy += self.vy * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
        else:
            self.wcx -= self.vx * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
            self.wcy -= self.vy * self.can_move * (1 + ((self.enemies_nearby) * 0.2))

        if calc_distance(self,player) < 10 and self.health > 0:
            if seconds > (self.last_hit_time + 0.7):
                player.health -= 2
                self.last_hit_time = seconds
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
        self.clone_cooldown = 0
        self.colour = (255,0,0)
        self.deciding_where = False
        self.tx = 0
        self.ty = 0
        self.counter = 0

    def draw(self):
        pygame.draw.circle(screen, self.colour, (self.cx, self.cy),self.radius)

    def evaluate_health(self):
        if 100 >= (self.health) >= 1:
            self.colour =(self.colour[0],255 * (self.health / 100),self.colour[2])
        if self.health <= 0:
            self.can_move = 0
            if self in enemies:
                enemies.remove(self)

    def clone_if_can(self,enemies,enemy_id):
        if self.clone_cooldown <= 0:
            self.clone_cooldown = 5
            enemies.insert(0,Enemy(self.wcx,self.wcy,enemy_id))
            enemy_id += 1
            world.objects.append(enemies[0])

        return enemy_id

    def decrement_cooldown(self):
        self.clone_cooldown -= (1/FPS)

    def beeline(self,player):
        if self.health > 0:
            if self.deciding_where:
                self.tx = random.randint(-30,30)
                self.ty = random.randint(-30,30)
                self.deciding_where = False
                self.counter = 3

            elif not self.deciding_where:
                self.deciding_where = False
                magnitude = math.sqrt((self.tx)**2 + (self.ty)**2)
                if magnitude == 0:
                    self.deciding_where = True
                else:
                    self.tx = self.tx / magnitude
                    self.ty = self.ty / magnitude
                    self.wcx += self.tx
                    self.wcy += self.ty
                    self.counter -= (1/FPS)

            if self.counter <= 0:
                self.deciding_where = True

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
        self.cx = player.cx
        self.cy = player.cy
        self.wcx = player.wcx
        self.wcy = player.wcy
        print("cooking")
        self.detonation_time -= (1/FPS)
        pygame.draw.circle(screen, self.colour, (self.cx, self.cy),self.actual_radius)
        if self.detonation_time <= 0:
            print("Exploding in hand")
            self.explode()

    def throw(self,player,target):
        if not self.thrown:
            self.wcx = player.wcx
            self.wcy = player.wcy
            self.thrown = True
            self.pos = (self.cx,self.cy)
            self.dy = target[1] - self.wcy
            self.dx = target[0] - self.wcx

            magnitude = math.sqrt((self.dx ** 2) + (self.dy ** 2))
            self.dy = (self.dy / magnitude) * 5
            self.dx = (self.dx / magnitude) * 5

            self.target = (target[0],target[1])

        print("throwing")
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
        for i in range(len(enemies)):
            if calc_distance(self,enemies[i]) < -95 and player.health > 0:
                self.thrown = False
                #print("Exploding on collision")
                self.explode()
        for i in range(len(trees)):
            if calc_distance(self,trees[i]) < -95 and player.health > 0:
                self.thrown = False
                self.explode()

        self.wcx += self.dx
        self.wcy += self.dy
        self.cx += self.dx
        self.cy += self.dy

        self.pos = (self.wcx,self.wcy)

    def explode(self):
        print("exploding")
        self.exploded = True
        pygame.draw.circle(screen, self.colour, (self.cx, self.cy), self.radius)
        for enemy in enemies:
            if calc_distance(self, enemy) < 0:
                enemy.health = enemy.health - 30
        if calc_distance(self, player) < 0:
            player.health = player.health - 30

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
                    #print(enemy.health)
                    #print("oof")
                    #print(enemy.colour)
                    found = True
                    self.deadly_bullet = self.bullet_trail[index]
                    got_hit_this_frame = True

            for i in range(len(trees)-1,-1,-1):
                if calc_distance_circle_and_point(trees[i],self.bullet_trail[index]) <= 0:
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
    def __init__(self,player):
        self.objects = []
        self.keys = pygame.key.get_pressed()
        self.player = player

island = Island((0, 255, 60,50),1000,750,450)

enemy_id = 0

camera_follow = BoundingBox()
key_g_not_pressed = True
player = Player(600,300)
#player2 = Player2(600,300)
players = [player] #,player2]
world = GameWorld(player)
world.objects.append(island)
#world.objects.append(player2)
enemies = []
trees = [Tree(random.randint(-200,1550),random.randint(-350,1250)) for i in range(15)] # How many trees
for i in range(len(trees)):
    world.objects.append(trees[i])
for i in range(3): # How many enemies
    enemies.append(Enemy(random.randint(0,750),random.randint(0,450),enemy_id))
    enemy_id += 1
active_grenades = []

health_bar = Health_bar()

singleplayer = True

pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)

text_surface = my_font.render('Click mouse to start', False, (0, 0, 0))
viruses = []
for i in range(5): # How many viruses
    viruses.append(Virus(enemy_id))
    enemy_id += 1
main_menu = True
for virus in viruses:
    enemies.append(virus)
for enemy in enemies:
    world.objects.append(enemy)
bullet_system = Bullet_trail()
frames = 0
key_g_held_down = False
sword = Sword()
sword_xvector = 0
sword_yvector = 0

'''
#server_socket.listen()
print("server on")
#(proxy_socket, proxy_address) = server_socket.accept()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((IP,PORT))


server_socket.settimeout(10)
print("Time out set")
server_socket.listen()

try:
    (proxy_socket, proxy_address) = server_socket.accept()
except:
    print("Connection timed out, starting singleplayer")
    singleplayer = True

#server_socket.setblocking(False)
'''
while running:

    if main_menu:
        print("Main Menu")
        menu_screen = pygame.Surface((1500,900))
        menu_screen.fill((255,255,45))
        screen.blit(menu_screen,(0,0))
        screen.blit(text_surface, (750, 450))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main_menu = False
        pygame.display.flip()
    else:
        #print(camera_follow.cam_cx)
        #print(camera_follow.cam_cy)

        frames = frames + 1
        seconds = frames / FPS
        #print(seconds)
        #print(fpsClock)

        #print(enemies)

        screen.fill((107, 191, 255))
        island.draw()
        #player2.draw()
        #print("I GOT HERE GGS")
        '''
        if frames % 1 == 0 and not singleplayer:
            singleplayer = player2.recv_and_send_data()
            #print("data sent")
            player2.rectify()
        '''


        if debugging:
            camera_follow.draw()
        player.draw()
        for tree in trees:
            tree.draw()
        for enemy in enemies:
            enemy.draw()
            if debugging:
                enemy.sword_target.draw()
            if not enemy.sword_stunned:
                enemy.beeline(player)
            else:
                enemy.beeline(enemy.sword_target) # Composition
                enemy.recover_from_sword()
        keys = pygame.key.get_pressed()
        world.keys = pygame.key.get_pressed()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    bullet_system.create_shot(player,pygame.mouse.get_pos(),0.1)
                    bullet_system.check_hit(enemies)
                    #print(enemy.health)
                if event.button == 3:
                    mouse_pos = pygame.mouse.get_pos()

                    sword.xvector = mouse_pos[0] - player.cx
                    sword.yvector = mouse_pos[1] - player.cy

                    magnitude = math.sqrt(sword.xvector**2 + sword.yvector**2)

                    sword.xvector = sword.xvector / magnitude
                    sword.yvector = sword.yvector / magnitude

                    sword.cx = player.cx + (sword.xvector*30)
                    sword.cy = player.cy + (sword.yvector*30)
                    sword.wcx = player.wcx + (sword.xvector*30)
                    sword.wcy = player.wcy + (sword.yvector*30)

                    sword.draw()
                    sword.check_hit(enemies)

        if key_g_held_down and key_g_not_pressed:
            print("Created grenade")
            active_grenades.append(Grenade_v2())
            world.objects.append(active_grenades[-1])
            key_g_not_pressed = False

        if key_g_held_down and active_grenades:
            print("Grenade cooking")
            active_grenades[-1].cook()

        if keys[pygame.K_g]:
            key_g_held_down = True
        else:
            key_g_held_down = False

        #print(active_grenades)

        #print(keys[pygame.K_g],grenade.key_g_not_pressed)


        if not key_g_held_down and key_g_not_pressed == False:
            mouse_pos = pygame.mouse.get_pos()
            mouse_pos = (mouse_pos[0] + camera_follow.cam_cx, mouse_pos[1] + camera_follow.cam_cy)
            print("Key g just released")
            if active_grenades:
                active_grenades[-1].throw(player,mouse_pos)
            key_g_not_pressed = True

        if keys[pygame.K_f]:
            player.fire_laser()
            player.check_laser_hit(enemies)

        #print(grenade.key_g_not_pressed)
        for grenade in active_grenades:
            if grenade.exploded:
                print("Grenade exploded")
                active_grenades.remove(grenade)
            elif grenade.thrown:
                grenade.throw(player,mouse_pos)


        move_ticker = 0
        if len(bullet_system.bullet_trail) > 0:
            bullet_system.draw(player)

        if keys[pygame.K_LSHIFT]:
            player.sprinting = 2
        else:
            player.sprinting = 1

        player.check_walkable(trees)

        if keys[pygame.K_w] and player.up_walkable and player.upright_walkable and player.upleft_walkable:
            if move_ticker == 0:
                move_ticker = player.move_up(player.in_camera)

                if keys[pygame.K_a] and player.left_walkable and player.upleft_walkable and player.downleft_walkable:
                    player.move_up_and_left(player.in_camera)
                if keys[pygame.K_d] and player.right_walkable and player.upright_walkable and player.downright_walkable:
                    player.move_up_and_right(player.in_camera)

        if keys[pygame.K_s] and player.down_walkable and player.downleft_walkable and player.downright_walkable:
            if move_ticker == 0:
                move_ticker = player.move_down(player.in_camera)
                #print("Moving down")
                if keys[pygame.K_a] and player.left_walkable and player.upleft_walkable and player.downleft_walkable:
                    player.move_down_and_left(player.in_camera)
                if keys[pygame.K_d] and player.right_walkable and player.upright_walkable and player.downright_walkable:
                    player.move_down_and_right(player.in_camera)


        if keys[pygame.K_a] and player.left_walkable and player.upleft_walkable and player.downleft_walkable:
            if move_ticker == 0:
                move_ticker = player.move_left(player.in_camera)

        if keys[pygame.K_d] and player.right_walkable and player.upright_walkable and player.downright_walkable:
            if move_ticker == 0:
                move_ticker = player.move_right(player.in_camera)



        player.walking_spot_permissions = [True for i in range(8)]

        for item in world.objects:
            item.cx = item.wcx - camera_follow.cam_cx
            item.cy = item.wcy - camera_follow.cam_cy

        '''
        if frames % 20 == 0:
            player.hcx = player.wcx - camera_follow.cam_cx
            player.hcy = player.wcy - camera_follow.cam_cy
            print(player.wcx)
            print(camera_follow.cam_cx)
            '''

        if not keys[pygame.K_w] and not keys[pygame.K_a] and not keys[pygame.K_d] and not keys[pygame.K_s]:
            #player.decelerate()
            #print("decellerating")
            pass




        if debugging:
            if keys[pygame.K_UP]:
                player.in_camera = False
            if keys[pygame.K_h]:
                player.cx = 600
                player.cy = 300
                player.hcx = 600
                player.hcy = 300
                player.wcx = 600
                player.wcy = 300
                camera_follow.cam_cx = 0
                camera_follow.cam_cy = 0
            pygame.draw.circle(screen,(255,50,255),(player.hcx,player.hcy),10)

        bullet_system.clean_shot()
        main_menu = player.update_health()
        health_bar.draw()

        for enemy in enemies:
            enemy.evaluate_health()
            enemy.clean_up()
            enemy.scan_for_friendlies(enemies)
            #print(enemy.health)

        for virus in viruses:
            if virus.health > 0:
                enemy_id = virus.clone_if_can(enemies,enemy_id)
                virus.decrement_cooldown()
            virus.evaluate_health()
            virus.clean_up()
            virus.scan_for_friendlies(enemies)

        camera_follow.scan_for_player(player)

        player.left = (player.cx - 25, player.cy)
        player.up = (player.cx, player.cy - 25)
        player.right = (player.cx + 25, player.cy)
        player.down = (player.cx, player.cy + 25)
        player.upleft = (player.cx-18,player.cy-18)
        player.downright = (player.cx+18,player.cy+18)
        player.downleft = (player.cx-18,player.cy+18)
        player.upright = (player.cx+18,player.cy-18)

        player.walking_spots = [player.left,player.right,player.down,player.up,player.upleft,player.downleft,player.downright,player.upright]

        if not player.in_camera:
            player.hcx = player.cx
            player.hcy = player.cy

        if 1 == 1: #some high level logic right here (you need a computer science degree to understand)
            bullet_system.decrement_cooldown(0.1)


        fpsClock.tick(FPS)
    pygame.display.flip()

pygame.quit()