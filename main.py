import pygame
import math
import random

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
    def draw(self):
        pygame.draw.circle(screen, (0,0,0), (self.cx, self.cy),self.radius)
        #print("Player drawn at",self.cx,self.cy)

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

    def get_hit(self,bullets):
        for bullet in bullets:
            if calc_distance_circle_and_point(enemy, bullet) <= 0 and self.got_hit_this_frame == False:
                self.health -= 20
                self.got_hit_this_frame = True
                print("oof")
                print(self.colour)

    def evaluate_health(self):
        if 1 >= (self.health / 100) >= 0:
            self.colour =(255,255 * (self.health / 100),255)
            if self.health <= 0:
                print("dead")
                self.can_move = 0

    def clean_up(self):
        self.got_hit_this_frame = False

    def scan_for_friendlies(self,enemies):
        self.enemies_nearby = 0
        for enemy in enemies:
            if calc_distance(self,enemy) < 5:
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
            self.cx += self.vx * self.can_move * (self.enemies_nearby)
            self.cy += self.vy * self.can_move * (self.enemies_nearby)
        else:
            self.cx -= self.vx * self.can_move * (self.enemies_nearby)
            self.cy -= self.vy * self.can_move * (self.enemies_nearby)

        if calc_distance(self,player) < 10:
            pass
            #print("Attacking")


class Bullet_trail:
    def __init__(self):
        self.cx = 0
        self.cy = 0
        self.radius = 5
        self.color = (125,125,125)
        self.bullet_trail = []

    def create_shot(self,player,destination,enemy):
        self.cx = player.cx
        self.cy = player.cy
        if (destination[0] - player.cx) != 0:
            gradient = (destination[1] - player.cy) / (destination[0] - player.cx)
        else:
            gradient = 9999
        gradient = abs(gradient)

        if destination[1] < player.cy and destination[0] > player.cx:
            print("Shooting up and right")
            if gradient > 1:
                for i in range(20):
                    self.bullet_trail.append((self.cx,self.cy))
                    self.cy -= (enemy.radius - 2)
                    self.cx += (1/gradient)* (enemy.radius - 2)


            elif 0 <= gradient <= 1:
                for i in range(20):
                    self.bullet_trail.append((self.cx,self.cy))
                    self.cx += (enemy.radius - 2)
                    self.cy -= gradient * (enemy.radius - 2)

        elif destination[1] < player.cy and destination[0] < player.cx:
            print("shooting up and left")
            if gradient > 1:
                for i in range(20):
                    self.bullet_trail.append((self.cx,self.cy))
                    self.cy -= (enemy.radius - 2)
                    self.cx -= (1/gradient) * (enemy.radius - 2)
            elif 0 <= gradient <= 1:
                for i in range(20):
                    self.bullet_trail.append((self.cx,self.cy))
                    self.cx -= (enemy.radius - 2)
                    self.cy -= gradient * (enemy.radius - 2)

        elif destination[1] > player.cy and destination[0] < player.cx:
            print("shooting down and left")
            if gradient > 1:
                for i in range(20):
                    self.bullet_trail.append((self.cx,self.cy))
                    self.cy += (enemy.radius - 2)
                    self.cx -= (1/gradient) * (enemy.radius - 2)

            elif 0 <= gradient <= 1:
                for i in range(20):
                    self.bullet_trail.append((self.cx,self.cy))
                    self.cx -= (enemy.radius - 2)
                    self.cy += gradient * (enemy.radius - 2)

        elif destination[1] > player.cy and destination[0] > player.cx:
            print("Shooting down and right")
            if gradient > 1:
                for i in range(20):
                    self.bullet_trail.append((self.cx,self.cy))
                    self.cy += (enemy.radius - 2)
                    self.cx += (1/gradient) * (enemy.radius - 2)

            elif 0 <= gradient <= 1:
                for i in range(20):
                    self.bullet_trail.append((self.cx,self.cy))
                    self.cx += (enemy.radius - 2)
                    self.cy += gradient * (enemy.radius - 2)
    def draw(self):
        for bullet in self.bullet_trail:
            pygame.draw.circle(screen, (123,123,123), (bullet[0],bullet[1]), 3)

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
world.objects.append(island)
enemies = [Enemy(random.randint(0,750),random.randint(0,450)) for i in range(5)]
for enemy in enemies:
    world.objects.append(enemy)
bullet_system = Bullet_trail()
while running:
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
            for enemy in enemies:
                bullet_system.create_shot(player,pygame.mouse.get_pos(),enemy)
                enemy.get_hit(bullet_system.bullet_trail)


    move_ticker = 0
    if len(bullet_system.bullet_trail) > 0 and debugging:
        bullet_system.draw()

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

    for enemy in enemies:
        enemy.evaluate_health()
        enemy.clean_up()
        enemy.scan_for_friendlies(enemies)

    camera_follow.scan_for_player(player)

    pygame.display.flip()
    fpsClock.tick(FPS)

pygame.quit()