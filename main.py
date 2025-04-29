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

class Player:
    def __init__(self,cx,cy):
        self.cx = cx
        self.cy = cy
        self.vy = 0
        self.vx = 0
    def draw(self):
        pygame.draw.circle(screen, (0,0,0), (self.cx, self.cx),25)
    def move(self,vx,vy):
        self.vx = vx
        self.vy = vy
        self.cx += self.vx
        self.cy += self.vy


island = Island((0, 255, 60,50),500,400,300)
camera_follow = BoundingBox()
player = Player(400,300)
while running:
    screen.fill((107, 191, 255))
    island.draw()
    if debugging:
        camera_follow.draw()
    player.draw()

    keys = pygame.key.get_pressed()
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False


    pygame.display.flip()
    fpsClock.tick(FPS)

pygame.quit()