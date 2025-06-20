import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))

running = True

debugging = True

FPS = 30
fpsClock = pygame.time.Clock()

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
        if self.lx < player.cx - 5 and player.cx + 5 < (self.lx + self.width) and self.ty < player.cy - 5 and (self.lx + self.height) > player.cy + 5:
            print("Player detected")
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
    def draw(self):
        pygame.draw.circle(screen, (0,0,0), (self.cx, self.cx),25)
    def move(self,vx,vy):
        self.vx = vx
        self.vy = vy
        self.cx += self.vx
        self.cy += self.vy
        pygame.draw.circle(screen, (0,0,0), (self.cx, self.cy),25)
        #print("Player drawn at",self.cx,self.cy)

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
                player.cy -= 3
                #print("Moving up",player.cx,player.cy)
                if keys[pygame.K_a]:
                    player.cx -= 3
                    #print("Moving up and left")
                if keys[pygame.K_d]:
                    player.cx += 3

        if keys[pygame.K_s]:
            if move_ticker == 0:
                move_ticker = 10
                player.cy += 3
                #print("Moving down")
                if keys[pygame.K_a]:
                    player.cx -= 3
                if keys[pygame.K_d]:
                    #print("Moving down and right")
                    player.cx += 3

        if keys[pygame.K_a]:
            if move_ticker == 0:
                move_ticker = 10
                player.cx -= 3
                #print("moving left")

        if keys[pygame.K_d]:
            if move_ticker == 0:
                move_ticker = 10
                player.cx += 3
                #print("moving right")

    else:
        if keys[pygame.K_w]:
            if move_ticker == 0:
                move_ticker = 10
                world.move_camera(["up"])
                if keys[pygame.K_a]:
                    world.move_camera(["up", "left"])
                if keys[pygame.K_d]:
                    world.move_camera(["up", "right"])
                if keys[pygame.K_s]:
                    player.cy = player.cy + 1

        if keys[pygame.K_s]:
            if move_ticker == 0:
                move_ticker = 10
                world.move_camera(["down"])
                if keys[pygame.K_a]:
                    world.move_camera(["down", "left"])
                if keys[pygame.K_d]:
                    world.move_camera(["down", "right"])
                if keys[pygame.K_w]:
                    player.cy = player.cy - 1

        if keys[pygame.K_a]:
            if move_ticker == 0:
                move_ticker = 10
                world.move_camera(["left"])
            if keys[pygame.K_d]:
                player.cx = player.cx + 1

        if keys[pygame.K_d]:
            if move_ticker == 0:
                move_ticker = 10
                world.move_camera(["right"])
            if keys[pygame.K_a]:
                player.cx = player.cx - 1



    if debugging:
        if keys[pygame.K_UP]:
            player.in_camera = False

    camera_follow.scan_for_player(player)
    pygame.display.flip()
    fpsClock.tick(FPS)