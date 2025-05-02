import pygame
import math

pygame.init()

screen = pygame.display.set_mode((1500, 900))

running = True

debugging = True

FPS = 30
fpsClock = pygame.time.Clock()

def CalcDistance(pointA, pointB):
    return math.sqrt((pointA.cx - pointB.cx)**2 + (pointA.cy - pointB.cy)**2) - pointA.radius - pointB.radius

class Island:
    def __init__(self,colour, radius, cx, cy):
        self.colour = colour
        self.radius = radius
        self.cx = cx
        self.cy = cy

    def draw(self):
        pygame.draw.circle(screen, (self.colour), (self.cx, self.cy), self.radius)

class BoundingBox:
    def __init__(self,lx=100,ty=50,width=600,height=500,screen=screen):
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
        if self.lx < player.hcx - 5 and player.hcx + 5 < (self.lx + self.width) and self.ty < player.hcy - 5 and (self.lx + self.height - 45) > player.hcy:
            print("player detected")
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
    def draw(self):
        pygame.draw.circle(screen, (0,0,0), (self.cx, self.cy),self.radius)
        #print("Player drawn at",self.cx,self.cy)

class Enemy:
    def __init__(self,cx,cy):
        self.cx = cx
        self.cy = cy
        self.radius = 25

    def draw(self):
        pygame.draw.circle(screen, (0,0,0), (self.cx, self.cy),self.radius)

    def beeline(self,player):
        pass


class GameWorld:
    def __init__(self,player):
        self.objects = []
        self.keys = pygame.key.get_pressed()
        self.player = player

    def move_camera(self,direction):
        for item in self.objects:
            if "down" in direction:
                item.cy = item.cy - 3


            if "up" in direction:
                item.cy = item.cy + 3


            if "left" in direction:
                item.cx = item.cx + 3

            if "right" in direction:
                item.cx = item.cx - 3





island = Island((0, 255, 60,50),500,400,300)


camera_follow = BoundingBox()
player = Player(400,300)
world = GameWorld(player)
world.objects.append(island)
enemy = Enemy(750,450)
world.objects.append(enemy)
while running:
    screen.fill((107, 191, 255))
    island.draw()
    if debugging:
        camera_follow.draw()
    player.draw()

    keys = pygame.key.get_pressed()
    world.keys = pygame.key.get_pressed()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    move_ticker = 0

    if player.in_camera:
        if keys[pygame.K_w]:
            if move_ticker == 0:
                move_ticker = 10
                player.hcy -= 3
                player.cy = player.hcy
                #print("Moving up",player.cx,player.cy)
                if keys[pygame.K_a]:
                    player.hcx -= 3
                    player.cx = player.hcx
                    #print("Moving up and left")
                if keys[pygame.K_d]:
                    player.hcx += 3
                    player.cx = player.hcx

        if keys[pygame.K_s]:
            if move_ticker == 0:
                move_ticker = 10
                player.hcy += 3
                player.cy = player.hcy
                #print("Moving down")
                if keys[pygame.K_a]:
                    player.hcx -= 3
                    player.cx = player.hcx
                if keys[pygame.K_d]:
                    #print("Moving down and right")
                    player.hcx += 3
                    player.cx = player.hcx

        if keys[pygame.K_a]:
            if move_ticker == 0:
                move_ticker = 10
                player.hcx -= 3
                player.cx = player.hcx
                #print("moving left")

        if keys[pygame.K_d]:
            if move_ticker == 0:
                move_ticker = 10
                player.hcx += 3
                player.cx = player.hcx
                #print("moving right")

    else:
        moved = False
        if keys[pygame.K_w] and not moved:
            if move_ticker == 0:
                if not keys[pygame.K_a] and not keys[pygame.K_d]:
                    move_ticker = 10
                    world.move_camera(["up"])
                    player.hcy = player.cy - 3
                    moved = True
                if keys[pygame.K_a] and not moved:
                    world.move_camera(["up", "left"])
                    player.hcx = player.cx - 3
                    moved = True
                if keys[pygame.K_d] and not moved:
                    world.move_camera(["up", "right"])
                    player.hcx = player.cx + 3
                    moved = True

        if keys[pygame.K_s] and not moved:
            if move_ticker == 0:
                if not keys[pygame.K_a] and not keys[pygame.K_d]:
                    move_ticker = 10
                    world.move_camera(["down"])
                    player.hcy = player.cy + 3
                    moved = True
                if keys[pygame.K_a] and not moved:
                    world.move_camera(["down", "left"])
                    player.hcx = player.cx - 3
                    moved = True
                if keys[pygame.K_d] and not moved:
                    world.move_camera(["down", "right"])
                    player.hcx = player.cx + 3
                    moved = True

        if keys[pygame.K_a] and not moved:
            if move_ticker == 0:
                move_ticker = 10
                world.move_camera(["left"])
                player.hcx = player.cx - 3
                moved = True


        if keys[pygame.K_d] and not moved:
            if move_ticker == 0:
                move_ticker = 10
                world.move_camera(["right"])
                player.hcx = player.cx + 3
                moved = True



    if debugging:
        if keys[pygame.K_UP]:
            player.in_camera = False
        pygame.draw.circle(screen,(255,50,255),(player.hcx,player.hcy),10)

    camera_follow.scan_for_player(player)

    pygame.display.flip()
    fpsClock.tick(FPS)

pygame.quit()