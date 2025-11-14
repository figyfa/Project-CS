import pygame
import math
import random
import socket

IP_PROXY = "127.0.0.1"
PORT = 8000

pygame.init()

screen = pygame.display.set_mode((1500, 900))

running = True

debugging = True

FPS = 60
fpsClock = pygame.time.Clock()

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
        self.health = 100
        self.colour = (0,0,0)
        self.laser_trail = []
        self.first_run = True
        self.wcx = 600
        self.wcy = 300

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
        pygame.draw.circle(screen, self.colour, (self.wcx-camera_follow.cam_cx, self.wcy-camera_follow.cam_cy),self.radius)
        #print("Player drawn at",self.cx,self.cy)
    def update_health(self):
        self.colour = (0,255 * (100 - self.health)/100,0)
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
            pygame.draw.line(screen, (11, 3, 252), (self.cx,self.cy),(self.laser_trail[-1][0],self.laser_trail[-1][1]),10)



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


    def recv_and_send_data(self,user_input):
        my_socket.send(user_input.encode())

        print(f"World coordinate: {self.wcx},{self.wcy}")
        # print(f"Sent {user_input}")
        data = my_socket.recv(10000).decode()
        print(f"Received {data}")
        data_processed = True

        data = data.split(" ")
        print(data)
        player.wcx = float(data[0])
        player.wcy = float(data[1])

        enemies = []

        for i in range(2, len(data), 3):
            # print(data[i+2])
            if data[i + 2] == "e":
                enemies.append(Enemy(float(data[i]), float(data[i + 1])))
            if data[i + 2] == "v":
                enemies.append(Virus(float(data[i]), float(data[i + 1])))

        return enemies

    def rectify(self):
        player.cx = player.wcx - camera_follow.cam_cx
        player.cy = player.wcy - camera_follow.cam_cy

        print(f"Rectified data {player.cx} {player.cy}")

class Enemy:
    def __init__(self,cx,cy):
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
                print("player hit")


class Virus(Enemy):
    def __init__(self,wx,wy):
        super().__init__(wx,wy)
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

    def clone_if_can(self,enemies):
        if self.clone_cooldown <= 0:
            self.clone_cooldown = 5
            enemies.insert(0,Enemy(self.wcx,self.wcy))
            world.objects.append(enemies[0])

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
        self.detonation_time = 5
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
        found = False
        index = 0
        got_hit_this_frame = False
        while not found and index < len(self.bullet_trail):

            for i in range(len(enemies)-1,-1,-1):
                if calc_distance_circle_and_point(enemies[i], self.bullet_trail[index]) <= 0 and got_hit_this_frame == False:
                    enemies[i].health -= 20
                    #print(enemy.health)
                    #print("oof")
                    #print(enemy.colour)
                    found = True
                    self.deadly_bullet = self.bullet_trail[index]
                    got_hit_this_frame = True

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

    def move_camera(self,direction):
        for item in self.objects:
            if len(direction) == 1:
                if "down" in direction:
                    item.cy = item.cy - 3 * player.sprinting


                if "up" in direction:
                    item.cy = item.cy + 3 * player.sprinting


                if "left" in direction:
                    item.cx = item.cx + 3 * player.sprinting

                if "right" in direction:
                    item.cx = item.cx - 3 * player.sprinting

            else:
                if "down" in direction and "left" in direction:
                    item.cy = item.cy - 2.121 * player.sprinting
                    item.cx = item.cx + 2.121 * player.sprinting


                if "up" in direction and "left" in direction:
                    item.cy = item.cy + 2.121 * player.sprinting
                    item.cx = item.cx + 2.121 * player.sprinting


                if "right" in direction and "down" in direction:
                    item.cx = item.cx - 2.121 * player.sprinting
                    item.cy = item.cy - 2.121 * player.sprinting

                if "right" in direction and "up" in direction:
                    item.cx = item.cx - 2.121 * player.sprinting
                    item.cy = item.cy + 2.121 * player.sprinting




island = Island((0, 255, 60,50),1000,750,450)

camera_follow = BoundingBox()
key_g_not_pressed = True
player = Player(600,300)
player2 = Player2(600,300)
players = [player,player2]
world = GameWorld(player)
world.objects.append(island)
world.objects.append(player2)
enemies = []
active_grenades = []

pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)

text_surface = my_font.render('Waiting for host', False, (0, 0, 0))

viruses = []
main_menu = True
for virus in viruses:
    enemies.append(virus)
for enemy in enemies:
    world.objects.append(enemy)
bullet_system = Bullet_trail()
frames = 0
key_g_held_down = False


data = [player2.wcx,player2.wcy]

while running:

    if main_menu:
        menu_screen = pygame.Surface((1500,900))
        menu_screen.fill((255,255,45))
        screen.blit(menu_screen,(0,0))
        screen.blit(text_surface, (750, 450))

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

        try:
            my_socket = socket.socket()
            my_socket.connect((IP_PROXY, PORT))
            main_menu = False
        except:
            pass
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
        player2.draw()

        data[0] = player2.wcx
        data[1] = player2.wcy

        user_input = (f"{str(data[0])} {str(data[1])}")
        user_input = ''.join(user_input)

        if frames % 1 == 0:
            enemies = player2.recv_and_send_data(user_input)
            player2.rectify()

        player2.rectify()


        if debugging:
            camera_follow.draw()
        player.draw()
        for enemy in enemies:
            enemy.draw()
            enemy.beeline(player)
        keys = pygame.key.get_pressed()
        world.keys = pygame.key.get_pressed()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:

                bullet_system.create_shot(player2,pygame.mouse.get_pos(),0.1)
                bullet_system.check_hit(enemies)
                #print(enemy.health)

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
                active_grenades[-1].throw(player2,mouse_pos)
            key_g_not_pressed = True

        if keys[pygame.K_f]:
            player2.fire_laser()
            player2.check_laser_hit(enemies)

        #print(grenade.key_g_not_pressed)
        for grenade in active_grenades:
            if grenade.exploded:
                print("Grenade exploded")
                active_grenades.remove(grenade)
            elif grenade.thrown:
                grenade.throw(player2,mouse_pos)


        move_ticker = 0
        if len(bullet_system.bullet_trail) > 0:
            bullet_system.draw(player2)

        if keys[pygame.K_LSHIFT]:
            player2.sprinting = 2
        else:
            player2.sprinting = 1

        if player2.in_camera:
            if keys[pygame.K_w]:
                if move_ticker == 0:
                    move_ticker = 10
                    player2.hcy -= 3 * player2.sprinting
                    player2.cy = player2.hcy
                    player2.wcy -= 3 * player2.sprinting
                    #print("Moving up",player2.cx,player2.cy)
                    if keys[pygame.K_a]:
                        player2.hcx -= 2.121 * player2.sprinting
                        player2.hcy += 0.879 * player2.sprinting
                        player2.cx = player2.hcx
                        player2.wcx -= 2.121 * player2.sprinting
                        player2.wcy += 0.879 * player2.sprinting
                        #print("Moving up and left")
                    if keys[pygame.K_d]:
                        player2.hcx += 2.121 * player2.sprinting
                        player2.hcy += 0.879 * player2.sprinting
                        player2.cx = player2.hcx
                        player2.wcx += 2.121 * player2.sprinting
                        player2.wcy += 0.879 * player2.sprinting
                        #print("Moving up and right")

            if keys[pygame.K_s]:
                if move_ticker == 0:
                    move_ticker = 10
                    player2.hcy += 3 * player2.sprinting
                    player2.cy = player2.hcy
                    player2.wcy += 3 * player2.sprinting
                    #print("Moving down")
                    if keys[pygame.K_a]:
                        player2.hcx -= 2.121 * player2.sprinting
                        player2.hcy -= 0.879 * player2.sprinting
                        player2.cx = player2.hcx
                        player2.wcx -= 2.121 * player2.sprinting
                        player2.wcy -= 0.879 * player2.sprinting
                        #print("Moving down and left")
                    if keys[pygame.K_d]:
                        #print("Moving down and right")
                        player2.hcx += 2.121 * player2.sprinting
                        player2.hcy -= 0.879 * player2.sprinting
                        player2.cx = player2.hcx
                        player2.wcx += 2.121 * player2.sprinting
                        player2.wcy -= 0.879 * player2.sprinting

            if keys[pygame.K_a]:
                if move_ticker == 0:
                    move_ticker = 10
                    player2.hcx -= 3 * player2.sprinting
                    player2.cx = player2.hcx
                    player2.wcx -= 3 * player2.sprinting
                    #print("moving left")

            if keys[pygame.K_d]:
                if move_ticker == 0:
                    move_ticker = 10
                    player2.hcx += 3 * player2.sprinting
                    player2.cx = player2.hcx
                    player2.wcx += 3 * player2.sprinting
                    #print("moving right")

        else:
            if keys[pygame.K_w]:
                if move_ticker == 0:
                    move_ticker = 10
                    player2.hcy -= 3 * player2.sprinting
                    camera_follow.cam_cy -= 3 * player2.sprinting
                    player2.wcy -= 3 * player2.sprinting
                    #print("Moving up",player2.cx,player2.cy)
                    if keys[pygame.K_a]:
                        player2.hcx -= 2.121 * player2.sprinting
                        player2.hcy += 0.879 * player2.sprinting
                        camera_follow.cam_cx -= 2.121 * player2.sprinting
                        camera_follow.cam_cy += 0.879 * player2.sprinting
                        player2.wcx -= 2.121 * player2.sprinting
                        player2.wcy += 0.879 * player2.sprinting
                        #print("Moving up and left")
                    if keys[pygame.K_d]:
                        player2.hcx += 2.121 * player2.sprinting
                        player2.hcy += 0.879 * player2.sprinting
                        camera_follow.cam_cx += 2.121 * player2.sprinting
                        camera_follow.cam_cy += 0.879 * player2.sprinting
                        player2.wcx += 2.121 * player2.sprinting
                        player2.wcy += 0.879 * player2.sprinting
                        #print("Moving up and right")

            if keys[pygame.K_s]:
                if move_ticker == 0:
                    move_ticker = 10
                    player2.hcy += 3 * player2.sprinting
                    camera_follow.cam_cy += 3 * player2.sprinting
                    player2.wcy += 3 * player2.sprinting
                    #print("Moving down")
                    if keys[pygame.K_a]:
                        player2.hcx -= 2.121 * player2.sprinting
                        player2.hcy -= 0.879 * player2.sprinting
                        camera_follow.cam_cx -= 2.121 * player2.sprinting
                        camera_follow.cam_cy -= 0.879 * player2.sprinting
                        player2.wcx -= 2.121 * player2.sprinting
                        player2.wcy -= 0.879 * player2.sprinting
                        #print("Moving left and down")
                    if keys[pygame.K_d]:
                        #print("Moving down and right")
                        player2.hcx += 2.121 * player2.sprinting
                        player2.hcy -= 0.879 * player2.sprinting
                        camera_follow.cam_cx += 2.121 * player2.sprinting
                        camera_follow.cam_cy -= 0.879 * player2.sprinting
                        player2.wcx += 2.121 * player2.sprinting
                        player2.wcy -= 0.879 * player2.sprinting

            if keys[pygame.K_a]:
                if move_ticker == 0:
                    move_ticker = 10
                    player2.hcx -= 3 * player2.sprinting
                    camera_follow.cam_cx -= 3 * player2.sprinting
                    player2.wcx -= 3 * player2.sprinting
                    #print("moving left")

            if keys[pygame.K_d]:
                if move_ticker == 0:
                    move_ticker = 10
                    player2.hcx += 3 * player2.sprinting
                    camera_follow.cam_cx += 3 * player2.sprinting
                    player2.wcx += 3 * player2.sprinting
                    #print("moving right")

        for enemy in enemies:
            world.objects.append(enemy)
        for virus in viruses:
            world.objects.append(virus)
        for grenade in active_grenades:
            world.objects.append(grenade)

        world.objects.append(island)


        for item in world.objects:
            item.cx = item.wcx - camera_follow.cam_cx
            item.cy = item.wcy - camera_follow.cam_cy
            if type(item) != Player:
                world.objects.remove(item)

        if frames % 20 == 0:
            player2.hcx = player2.wcx - camera_follow.cam_cx
            player2.hcy = player2.wcy - camera_follow.cam_cy

        if not keys[pygame.K_w] and not keys[pygame.K_a] and not keys[pygame.K_d] and not keys[pygame.K_s]:
            player2.hcx = player2.wcx - camera_follow.cam_cx
            player2.hcy = player2.wcy - camera_follow.cam_cy




        if debugging:
            if keys[pygame.K_UP]:
                player2.in_camera = False
            if keys[pygame.K_h]:
                player2.cx = 600
                player2.cy = 300
                player2.hcx = 600
                player2.hcy = 300
                player2.wcx = 600
                player2.wcy = 300
                camera_follow.cam_cx = 0
                camera_follow.cam_cy = 0
            pygame.draw.circle(screen,(255,50,255),(player2.hcx,player2.hcy),10)

        bullet_system.clean_shot()
        player2.update_health()

        for enemy in enemies:
            enemy.evaluate_health()
            enemy.clean_up()
            enemy.scan_for_friendlies(enemies)
            #print(enemy.health)

        for virus in viruses:
            if virus.health > 0:
                virus.clone_if_can(enemies)
                virus.decrement_cooldown()
            virus.evaluate_health()
            virus.clean_up()
            virus.scan_for_friendlies(enemies)

        camera_follow.scan_for_player(player2)

        if not player2.in_camera:
            player2.hcx = player2.cx
            player2.hcy = player2.cy

        if 1 == 1: #some high level logic right here (you need a computer science degree to understand)
            bullet_system.decrement_cooldown(0.1)


        fpsClock.tick(FPS)
    pygame.display.flip()

pygame.quit()