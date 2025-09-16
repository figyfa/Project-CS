import socket
import pygame
import random
import math

IP_PROXY = "127.0.0.1"
PORT = 8000

pygame.init()

screen = pygame.display.set_mode((1500, 900))

running = True

debugging = True

FPS = 60
fpsClock = pygame.time.Clock()

def calc_distance(pointA, pointB):
    return math.sqrt((pointA.cx - pointB.cx)**2 + (pointA.cy - pointB.cy)**2) - pointA.radius - pointB.radius

def calc_distance_circle_and_point(pointA, pointB):
    return math.sqrt((pointA.cx - pointB[0])**2 + (pointA.cy - pointB[1])**2) - pointA.radius

class Island:
    def __init__(self,colour, radius, cx, cy):
        self.colour = colour
        self.radius = radius
        self.cx = cx
        self.cy = cy

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

    def draw(self):
        self.s.set_alpha(128)
        self.s.fill((255,255,255))
        self.screen.blit(self.s,(self.lx,self.ty))

    def scan_for_player(self,player2):
        if self.lx < player2.hcx - 5 and player2.hcx + 5 < (self.lx + self.width) and self.ty < player2.hcy - 5 and (self.ty + self.height) > player2.hcy:
            #print("player2 detected")
            player2.in_camera = True
        else:
            player2.in_camera = False



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
        self.wcx = 0
        self.wcy = 0

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
        #print("Player drawn at",self.cx,self.cy)
    def update_health(self):
        self.colour = (0,255 * (100 - self.health)/100,0)
    def fire_laser(self):
        mouse_pos = pygame.mouse.get_pos()
        magnitude = math.sqrt((mouse_pos[0] - self.cx)**2 + (mouse_pos[1] - self.cy)**2)
        self.xstep = ((mouse_pos[0] - self.cx)/magnitude) * 20
        self.ystep = ((mouse_pos[1] - self.cy)/magnitude) * 20
        self.current_bulletx = self.cx
        self.current_bullety = self.cy
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
                pygame.draw.circle(screen, (123,123,123), (circle[0],circle[1]),5)
        else:
            pygame.draw.line(screen, (11, 3, 252), (self.cx,self.cy),(self.laser_trail[-1][0],self.laser_trail[-1][1]),10)



    def check_laser_hit(self,enemies):
        for enemy in enemies:
            for circle in self.laser_trail:
                print(calc_distance_circle_and_point(enemy,circle))
                if calc_distance_circle_and_point(enemy,circle) < 0:
                    enemy.health -= 5
        self.laser_trail = []



class Player2 (Player):
    def __init__(self,cx,cy):
        super().__init__(cx,cy)


    def recv_and_send_data(self,user_input):
        my_socket.send(user_input.encode())
        print(f"Sent {user_input}")
        data = my_socket.recv(1024).decode()
        print(f"Received {data}")

        data = data.split(" ")
        print(data)
        player.cx = float(data[0])
        player.cy = float(data[1])

        enemies = []

        for i in range(2,len(data),3):
            print(data[i+2])
            if data[i+2] == "enemy":
                enemies.append(Enemy(float(data[i]),float(data[i+1])))
            if data[i+2] == "virus":
                enemies.append(Virus(float(data[i]),float(data[i+1])))

        return enemies
    def rectify(self):
        player.cx -= player.wcx
        player.cy -= player.wcy

        print(f"Rectified data {self.cx} {self.cy}")

class Enemy:
    def __init__(self,cx,cy):
        self.cx = cx
        self.cy = cy
        self.radius = 25
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
            print(self.image_list)
        if self.health <= 0:
            self.can_move = 0
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

    def beeline(self,player2):
        angle = math.pi
        if player2.cx - enemy.cx != 0:
            angle = math.atan((player2.cy - enemy.cy)/(player2.cx - enemy.cx))
        #print(angle/math.pi*180)
        self.vx = -3 * math.cos(angle)
        self.vy = -3 * math.sin(angle)

        if enemy.cx > player2.cx:
            self.cx += self.vx * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
            self.cy += self.vy * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
        else:
            self.cx -= self.vx * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
            self.cy -= self.vy * self.can_move * (1 + ((self.enemies_nearby) * 0.2))

        if calc_distance(self,player2) < 10 and self.health > 0:
            if seconds > (self.last_hit_time + 0.7):
                player2.health -= 2
                self.last_hit_time = seconds
                print("player2 hit")


class Virus(Enemy):
    def __init__(self,cx,cy):
        super().__init__(cx,cy)
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
            viruses.remove(self)

    def clone_if_can(self,enemies):
        if self.clone_cooldown <= 0:
            self.clone_cooldown = 5
            enemies.insert(0,Enemy(self.cx,self.cy))
            world.objects.append(enemies[0])

    def decrement_cooldown(self):
        self.clone_cooldown -= (1/FPS)

    def beeline(self,player2):
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
                    self.cx += self.tx
                    self.cy += self.ty
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

    def cook(self):
        self.cx = player2.cx
        self.cy = player2.cy
        print("cooking")
        self.detonation_time -= (1/FPS)
        pygame.draw.circle(screen, self.colour, (self.cx, self.cy),self.actual_radius)
        if self.detonation_time <= 0:
            print("Exploding in hand")
            self.explode()

    def throw(self,player2,target):
        if not self.thrown:
            self.cx = player2.cx
            self.cy = player2.cy
            self.thrown = True
            self.pos = (self.cx,self.cy)
            self.dy = target[1] - self.cy
            self.dx = target[0] - self.cx

            magnitude = math.sqrt((self.dx ** 2) + (self.dy ** 2))
            self.dy = (self.dy / magnitude) * 5
            self.dx = (self.dx / magnitude) * 5


        print("throwing")
        pygame.draw.circle(screen, self.colour, (self.cx,self.cy),self.actual_radius)
        print(target)
        print(self.pos)
        self.detonation_time -= (1/FPS)
        if self.detonation_time <= 0:
            print("Exploding while travelling")
            self.thrown = False
            self.explode()
        for i in range(len(enemies)):
            if calc_distance_circle_and_point(enemies[i],self.pos) < 5 and player2.health > 0:
                self.thrown = False
                print("Exploding on collision")
                self.explode()

        self.cx += self.dx
        self.cy += self.dy

        self.pos = (self.cx,self.cy)

    def explode(self):
        print("exploding")
        self.exploded = True
        pygame.draw.circle(screen, self.colour, (self.cx, self.cy), self.radius)
        for enemy in enemies:
            if calc_distance(self, enemy) < 0:
                enemy.health = enemy.health - 30
        if calc_distance(self, player2) < 0:
            player2.health = player2.health - 30

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

    def create_shot(self,player2,destination,fire_rate):
        if self.fire_rate <= 0:
            self.fire_rate = fire_rate
            magnitude = math.sqrt((destination[0] - player2.cx) ** 2 + (destination[1] - player2.cy) ** 2)
            self.xstep = ((destination[0] - player2.cx) / magnitude) * 20
            self.ystep = ((destination[1] - player2.cy) / magnitude) * 20
            self.current_bulletx = player2.cx
            self.current_bullety = player2.cy
            self.bullet_trail.append((self.current_bulletx, self.current_bullety))

            for i in range(20):
                self.current_bulletx += self.xstep
                self.current_bullety += self.ystep
                self.bullet_trail.append((self.current_bulletx, self.current_bullety))
    def decrement_cooldown(self,fire_rate):
        self.fire_rate = self.fire_rate - (1/FPS)


    def draw(self, player2):
        if debugging:
            for bullet in self.bullet_trail:
                pygame.draw.circle(screen, (123,123,123), (bullet[0],bullet[1]), 3)
        else:
            pygame.draw.line(screen,(238, 255, 0),(player2.cx,player2.cy),(self.deadly_bullet[0],self.deadly_bullet[1]),4)

    def clean_shot(self):
        self.bullet_trail = []


class GameWorld:
    def __init__(self,player2):
        self.objects = []
        self.keys = pygame.key.get_pressed()
        self.player2 = player2

    def move_camera(self,direction):
        for item in self.objects:
            if len(direction) == 1:
                if "down" in direction:
                    item.cy = item.cy - 3 * player2.sprinting


                if "up" in direction:
                    item.cy = item.cy + 3 * player2.sprinting


                if "left" in direction:
                    item.cx = item.cx + 3 * player2.sprinting

                if "right" in direction:
                    item.cx = item.cx - 3 * player2.sprinting

            else:
                if "down" in direction and "left" in direction:
                    item.cy = item.cy - 2.121 * player2.sprinting
                    item.cx = item.cx + 2.121 * player2.sprinting


                if "up" in direction and "left" in direction:
                    item.cy = item.cy + 2.121 * player2.sprinting
                    item.cx = item.cx + 2.121 * player2.sprinting


                if "right" in direction and "down" in direction:
                    item.cx = item.cx - 2.121 * player2.sprinting
                    item.cy = item.cy - 2.121 * player2.sprinting

                if "right" in direction and "up" in direction:
                    item.cx = item.cx - 2.121 * player2.sprinting
                    item.cy = item.cy + 2.121 * player2.sprinting

island = Island((0, 255, 60,50),1000,750,450)

camera_follow = BoundingBox()
key_g_not_pressed = True
player = Player(600,300)
player2 = Player2(600,300)
players = [player2,player2]
world = GameWorld(player2)
world.objects.append(island)
world.objects.append(player2)
enemies = []
active_grenades = []

pygame.font.init()
my_font = pygame.font.SysFont('Comic Sans MS', 30)

text_surface = my_font.render('Click mouse to start', False, (0, 0, 0))

viruses = []
main_menu = True
for virus in viruses:
    enemies.append(virus)
for enemy in enemies:
    world.objects.append(enemy)
bullet_system = Bullet_trail()
frames = 0
key_g_held_down = False

    # Use a breakpoint in the code line below to debug your script.
my_socket = socket.socket()
my_socket.connect((IP_PROXY, PORT))
data = [0,0]

while running:
    frames = frames + 1
    seconds = frames / FPS

    island.draw()
    player2.draw()
    player.draw()

    data[0] = player2.cx
    data[1] = player2.cy


    user_input = (f"{str(data[0])} {str(data[1])}")
    user_input = ''.join(user_input)

    enemies = player2.recv_and_send_data(user_input)
    player2.rectify()

    print(enemies)
    for enemy in enemies:
        print(f"{enemy} drawn")
        print(f"{(enemy.cx,enemy.cy)}")
        enemy.draw()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False



    keys = pygame.key.get_pressed()
    move_ticker = 0

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
                # print("Moving up",player2.cx,player2.cy)
                if keys[pygame.K_a]:
                    player2.hcx -= 2.121 * player2.sprinting
                    player2.hcy += 0.879 * player2.sprinting
                    player2.cx = player2.hcx
                    # print("Moving up and left")
                if keys[pygame.K_d]:
                    player2.hcx += 2.121 * player2.sprinting
                    player2.hcy += 0.879 * player2.sprinting
                    player2.cx = player2.hcx

        if keys[pygame.K_s]:
            if move_ticker == 0:
                move_ticker = 10
                player2.hcy += 3 * player2.sprinting
                player2.cy = player2.hcy
                # print("Moving down")
                if keys[pygame.K_a]:
                    player2.hcx -= 2.121 * player2.sprinting
                    player2.hcy -= 0.879 * player2.sprinting
                    player2.cx = player2.hcx
                if keys[pygame.K_d]:
                    # print("Moving down and right")
                    player2.hcx += 2.121 * player2.sprinting
                    player2.hcy -= 0.879 * player2.sprinting
                    player2.cx = player2.hcx

        if keys[pygame.K_a]:
            if move_ticker == 0:
                move_ticker = 10
                player2.hcx -= 3 * player2.sprinting
                player2.cx = player2.hcx
                # print("moving left")

        if keys[pygame.K_d]:
            if move_ticker == 0:
                move_ticker = 10
                player2.hcx += 3 * player2.sprinting
                player2.cx = player2.hcx
                # print("moving right")

    else:
        moved = False
        if keys[pygame.K_w] and not moved:
            if move_ticker == 0:
                if not keys[pygame.K_a] and not keys[pygame.K_d]:
                    move_ticker = 10
                    world.move_camera(["up"])
                    player2.hcy = player2.cy - 3 * player2.sprinting
                    player2.wcy = player2.wcy - 3 * player2.sprinting
                    moved = True
                if keys[pygame.K_a] and not moved:
                    world.move_camera(["up", "left"])
                    player2.hcx = player2.cx - 3 * player2.sprinting
                    player2.hcy = player2.cy - 3 * player2.sprinting
                    player2.wcx = player2.wcx - 3 * player2.sprinting
                    player2.wcy = player2.wcy - 3 * player2.sprinting
                    moved = True
                if keys[pygame.K_d] and not moved:
                    world.move_camera(["up", "right"])
                    player2.hcx = player2.cx + 3 * player2.sprinting
                    player2.hcy = player2.cy - 3 * player2.sprinting
                    player2.wcx = player2.wcx + 3 * player2.sprinting
                    player2.wcy = player2.wcy - 3 * player2.sprinting
                    moved = True

        if keys[pygame.K_s] and not moved:
            if move_ticker == 0:
                if not keys[pygame.K_a] and not keys[pygame.K_d]:
                    move_ticker = 10
                    world.move_camera(["down"])
                    player2.hcy = player2.cy + 3 * player2.sprinting
                    player2.wcy = player2.wcy + 3 * player2.sprinting
                    moved = True
                if keys[pygame.K_a] and not moved:
                    world.move_camera(["down", "left"])
                    player2.hcx = player2.cx - 3 * player2.sprinting
                    player2.hcy = player2.cy + 3 * player2.sprinting
                    player2.wcx = player2.wcx - 3 * player2.sprinting
                    player2.wcy = player2.wcy + 3 * player2.sprinting
                    moved = True
                if keys[pygame.K_d] and not moved:
                    world.move_camera(["down", "right"])
                    player2.hcx = player2.cx + 3 * player2.sprinting
                    player2.hcy = player2.cy + 3 * player2.sprinting
                    player2.wcx = player2.wcx + 3 * player2.sprinting
                    player2.wcy = player2.wcy + 3 * player2.sprinting
                    moved = True

        if keys[pygame.K_a] and not moved:
            if move_ticker == 0:
                move_ticker = 10
                world.move_camera(["left"])
                player2.hcx = player2.cx - 3 * player2.sprinting
                player2.wcx = player2.wcx - 3 * player2.sprinting
                moved = True

        if keys[pygame.K_d] and not moved:
            if move_ticker == 0:
                move_ticker = 10
                world.move_camera(["right"])
                player2.hcx = player2.cx + 3 * player2.sprinting
                player2.wcx = player2.wcx + 3 * player2.sprinting
                moved = True

    if not keys[pygame.K_w] and not keys[pygame.K_a] and not keys[pygame.K_d] and not keys[pygame.K_s]:
        player2.decelerate()
        # print("decellerating")

    player2.cx = player2.hcx
    player2.cy = player2.hcy
    if debugging:
        if keys[pygame.K_UP]:
            player2.in_camera = False
        pygame.draw.circle(screen, (255, 50, 255), (player2.hcx, player2.hcy), 10)

    if running == False:
        user_input = "EXIT"

    print(f"the data is {data}")
    if user_input == "EXIT":
        break
    pygame.display.flip()
my_socket.close()