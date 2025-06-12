import pygame
import math
import random

pygame.init()

screen = pygame.display.set_mode((1500, 900))

running = True

debugging = False

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
        self.vy = 0
        self.vx = 0
        self.in_camera = True
        self.hcx = cx
        self.hcy = cy
        self.radius = 25
        self.sprinting = 1
        self.health = 100
        self.colour = (0,0,0)
        self.laser_trail = []
        self.first_run = True
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
        if self.health <= 0:
            self.can_move = 0

    def clean_up(self):
        self.got_hit_this_frame = False

    def scan_for_friendlies(self,enemies):
        self.enemies_nearby = 0
        for enemy in enemies:
            if calc_distance(self,enemy) < 5 and enemy.health > 0:
                self.enemies_nearby += 1


    def draw(self):
        pygame.draw.circle(screen, self.colour, (self.cx, self.cy),self.radius)

    def beeline(self,player):
        angle = math.pi
        if player.cx - enemy.cx != 0:
            angle = math.atan((player.cy - enemy.cy)/(player.cx - enemy.cx))
        #print(angle/math.pi*180)
        self.vx = -3 * math.cos(angle)
        self.vy = -3 * math.sin(angle)

        if enemy.cx > player.cx:
            self.cx += self.vx * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
            self.cy += self.vy * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
        else:
            self.cx -= self.vx * self.can_move * (1 + ((self.enemies_nearby) * 0.2))
            self.cy -= self.vy * self.can_move * (1 + ((self.enemies_nearby) * 0.2))

        if calc_distance(self,player) < 10 and self.health > 0:
            if seconds > (self.last_hit_time + 0.7):
                player.health -= 2
                self.last_hit_time = seconds
                print("player hit")


class Virus(Enemy):
    def __init__(self):
        super().__init__(random.randint(0,500),random.randint(0,500))
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

    def clone_if_can(self,enemies):
        if self.clone_cooldown <= 0:
            self.clone_cooldown = 5
            enemies.insert(0,Enemy(self.cx,self.cy))
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
                    self.cx += self.tx
                    self.cy += self.ty
                    self.counter -= (1/FPS)

            if self.counter <= 0:
                self.deciding_where = True

class Grenade:
    def __init__(self):
        self.cooking = False
        self.thrown = False
        self.exploded = False
        self.current_time = 0
        self.current_time_decided = False
        self.cx = 0
        self.cy = 0
        self.colour = (123,52,231)
        self.distance_travelled = 0
        self.radius = 100
        self.key_g_not_pressed = True
        self.x_step = 1
        self.y_step = 1
        self.grenade_active = False
        self.capacity = 3

    def arm(self):
        print("Arming")
        if self.grenade_active == False:
            self.grenade_active = True
            self.cooking = True
            if self in world.objects:
                world.objects.remove(self)
            if not self.current_time_decided:
                self.current_time = seconds
                self.current_time_decided = True
                print("Cooking 1")
            print("Cooking 2")

            if seconds >= self.current_time + 3 and self.thrown == False:
                self.current_time_decided = False
                self.cooking = False
                print("Exploding in hand")
                self.explode()

    def throw(self,direction):
        self.cooking = False

        #print(seconds,self.current_time+3,self.distance_travelled)
        if self.thrown == False:
            world.objects.append(self)
            print("Added")
            self.grenade_active = True

            self.cx = player.cx
            self.cy = player.cy
            dy = direction[1] - player.cy
            dx = direction[0] - player.cx

            magnitude = math.sqrt((dx * dx) + (dy * dy))

            self.y_step = dy/magnitude
            self.x_step = dx/magnitude
            #print(magnitude)
            #print(self.x_step,self.y_step)

        self.thrown = True
        if seconds <= self.current_time + 3 and self.distance_travelled < 3000 and self.thrown and self.grenade_active:
            self.cx = self.cx + self.x_step * (5 - (self.distance_travelled * 0.02))
            self.cy = self.cy + self.y_step * (5 - (self.distance_travelled * 0.02))
            #print(self.x_step,self.y_step)

            self.distance_travelled += 1

            pygame.draw.circle(screen,(252,231,223),(self.cx,self.cy),10)

            for enemy in enemies:
                if math.sqrt((self.cx - enemy.cx) ** 2 + (self.cy - enemy.cy) ** 2) < (10 + enemy.radius):
                    self.grenade_active = False
                    self.thrown = False
                    self.explode()

            '''
            if direction[0] > self.cx:
                if self.angle_to_horz > 0:
                    self.cx = self.cx + 10
                    self.cy = self.cy - math.tan(self.angle_to_horz)
                elif self.angle_to_horz <= 0:
                    self.cx = self.cx + 10
                    self.cy = self.cy + math.tan(self.angle_to_horz)
            else:
                if self.angle_to_horz > 0:
                    self.cx = self.cx - 10
                    self.cy = self.cy - math.tan(self.angle_to_horz)
                elif self.angle_to_horz <= 0:
                    self.cx = self.cx - 10
                    self.cy = self.cy + math.tan(self.angle_to_horz)

            self.distance_travelled += 1
            '''

        elif seconds > self.current_time + 3:
            print("Exploding after thrown")
            self.current_time_decided = False
            self.exploded = True
            self.thrown = False
            self.explode()

    def explode(self):
        self.exploded = False
        self.grenade_active = False
        pygame.draw.circle(screen, self.colour, (self.cx, self.cy), self.radius)
        for enemy in enemies:
            if calc_distance(self,enemy) < 0:
                enemy.health = enemy.health - 30
        if calc_distance(self,player) < 0:
            player.health = player.health - 30

        self.key_g_not_pressed = True
        self.distance_travelled = 0
        print(f"Damage administered around {self.cx,self.cy}")
        if self in world.objects:
            world.objects.remove(self)

        self.current_time_decided = False





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
player = Player(600,300)
world = GameWorld(player)
grenade = Grenade()
world.objects.append(island)
enemies = [Enemy(random.randint(0,750),random.randint(0,450)) for i in range(5)]
viruses = [Virus() for j in range(1)]
for virus in viruses:
    enemies.append(virus)
for enemy in enemies:
    world.objects.append(enemy)
bullet_system = Bullet_trail()
frames = 0
while running:
    frames = frames + 1
    seconds = frames / FPS
    #print(seconds)
    #print(fpsClock)
    screen.fill((107, 191, 255))
    island.draw()
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

            bullet_system.create_shot(player,pygame.mouse.get_pos(),0.2)
            bullet_system.check_hit(enemies)
            #print(enemy.health)

    if keys[pygame.K_g] and grenade.key_g_not_pressed:
        grenade.key_g_not_pressed = False
        grenade.arm()

    #print(keys[pygame.K_g],grenade.key_g_not_pressed)

    if not keys[pygame.K_g] and grenade.key_g_not_pressed == False:
        mouse_pos = pygame.mouse.get_pos()
        grenade.throw(mouse_pos)

    if keys[pygame.K_g] and grenade.key_g_not_pressed == False:
        mouse_pos = pygame.mouse.get_pos()
        grenade.throw(mouse_pos)

    if keys[pygame.K_f]:
        player.fire_laser()
        player.check_laser_hit(enemies)

    #print(grenade.key_g_not_pressed)
    if grenade.exploded:
        grenade.key_g_not_pressed = True


    move_ticker = 0
    if len(bullet_system.bullet_trail) > 0:
        bullet_system.draw(player)

    if keys[pygame.K_LSHIFT]:
        player.sprinting = 2
    else:
        player.sprinting = 1

    if player.in_camera:
        if keys[pygame.K_w]:
            if move_ticker == 0:
                move_ticker = 10
                player.hcy -= 3 * player.sprinting
                player.cy = player.hcy
                #print("Moving up",player.cx,player.cy)
                if keys[pygame.K_a]:
                    player.hcx -= 2.121 * player.sprinting
                    player.hcy += 0.879 * player.sprinting
                    player.cx = player.hcx
                    #print("Moving up and left")
                if keys[pygame.K_d]:
                    player.hcx += 2.121 * player.sprinting
                    player.hcy += 0.879 * player.sprinting
                    player.cx = player.hcx

        if keys[pygame.K_s]:
            if move_ticker == 0:
                move_ticker = 10
                player.hcy += 3 * player.sprinting
                player.cy = player.hcy
                #print("Moving down")
                if keys[pygame.K_a]:
                    player.hcx -= 2.121 * player.sprinting
                    player.hcy -= 0.879 * player.sprinting
                    player.cx = player.hcx
                if keys[pygame.K_d]:
                    #print("Moving down and right")
                    player.hcx += 2.121 * player.sprinting
                    player.hcy -= 0.879 * player.sprinting
                    player.cx = player.hcx

        if keys[pygame.K_a]:
            if move_ticker == 0:
                move_ticker = 10
                player.hcx -= 3 * player.sprinting
                player.cx = player.hcx
                #print("moving left")

        if keys[pygame.K_d]:
            if move_ticker == 0:
                move_ticker = 10
                player.hcx += 3 * player.sprinting
                player.cx = player.hcx
                #print("moving right")

    else:
        moved = False
        if keys[pygame.K_w] and not moved:
            if move_ticker == 0:
                if not keys[pygame.K_a] and not keys[pygame.K_d]:
                    move_ticker = 10
                    world.move_camera(["up"])
                    player.hcy = player.cy - 3 * player.sprinting
                    moved = True
                if keys[pygame.K_a] and not moved:
                    world.move_camera(["up", "left"])
                    player.hcx = player.cx - 3 * player.sprinting
                    player.hcy = player.cy - 3 * player.sprinting
                    moved = True
                if keys[pygame.K_d] and not moved:
                    world.move_camera(["up", "right"])
                    player.hcx = player.cx + 3 * player.sprinting
                    player.hcy = player.cy - 3 * player.sprinting
                    moved = True

        if keys[pygame.K_s] and not moved:
            if move_ticker == 0:
                if not keys[pygame.K_a] and not keys[pygame.K_d]:
                    move_ticker = 10
                    world.move_camera(["down"])
                    player.hcy = player.cy + 3 * player.sprinting
                    moved = True
                if keys[pygame.K_a] and not moved:
                    world.move_camera(["down", "left"])
                    player.hcx = player.cx - 3 * player.sprinting
                    player.hcy = player.cy + 3 * player.sprinting
                    moved = True
                if keys[pygame.K_d] and not moved:
                    world.move_camera(["down", "right"])
                    player.hcx = player.cx + 3 * player.sprinting
                    player.hcy = player.cy + 3 * player.sprinting
                    moved = True

        if keys[pygame.K_a] and not moved:
            if move_ticker == 0:
                move_ticker = 10
                world.move_camera(["left"])
                player.hcx = player.cx - 3 * player.sprinting
                moved = True


        if keys[pygame.K_d] and not moved:
            if move_ticker == 0:
                move_ticker = 10
                world.move_camera(["right"])
                player.hcx = player.cx + 3 * player.sprinting
                moved = True



    if debugging:
        if keys[pygame.K_UP]:
            player.in_camera = False
        pygame.draw.circle(screen,(255,50,255),(player.hcx,player.hcy),10)

    bullet_system.clean_shot()
    player.update_health()

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

    camera_follow.scan_for_player(player)

    if 1 == 1:
        bullet_system.decrement_cooldown(0.2)

    pygame.display.flip()
    fpsClock.tick(FPS)

pygame.quit()