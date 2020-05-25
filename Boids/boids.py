# Boids flocking simulation with quadtree implemented for speed optimization
# Dylan Herrera

from pygame.locals import *
import math
import random
from QuadTree import *

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (200, 200, 200)
TRANS = (1, 1, 1)
blues = []
for i in range(0, 32):
    blues.append((0, 255 - 8 * i, 255))
    blues.append((0, 255 - 8 * i, 255))
greens = []
for i in range(0, 32):
    greens.append((255 - 8 * i, 255, 0))
    greens.append((255 - 8 * i, 255, 0))
reds = []
for i in range(0, 32):
    reds.append((255, 255 - 8 * i, 0))
    reds.append((255, 255 - 8 * i, 0))

# THESE FIVE VALUES ARE THE ONLY PARAMETERS THAT CAN BE CHANGED
show_neighbors = False
show_one_neighbors = False
# Enabling quad trees enhances performance drastically, but decreases accuracy of neighbor detection
# Increasing npartitions enhances performance drastically, but decreases possible perception radius
# Note the partitions should be used such that the perception radius is smaller than each quad
use_quads = True
npartitions = 2
colorscheme = blues

# Do not change
screen_size = (650,650)
perception = 40
scale_align = 0.2
scale_cohesion = 0.05
scale_separation = 0.8
scale_noise = .1
speed = 20
nboids = 250

params = [scale_align, scale_cohesion, scale_separation, scale_noise, speed, perception]


class Slider():
    def __init__(self, name, val, maxi, mini, pos):
        self.name = name
        self.val = val  # start value
        self.maxi = maxi  # maximum at slider position right
        self.mini = mini  # minimum at slider position left
        self.xpos = pos  # x-location on screen
        self.ypos = screen_size[1] - 60
        self.surf = pygame.surface.Surface((100, 50))
        self.hit = False  # the hit attribute indicates slider movement due to mouse interaction
        self.txt_surf = font.render(name, 1, BLACK)
        self.txt_rect = self.txt_surf.get_rect(center=(50, 15))
        # Static graphics - slider background #
        self.surf.fill((100, 100, 100))
        pygame.draw.rect(self.surf, GREY, [0, 0, 100, 50], 3)
        pygame.draw.rect(self.surf, WHITE, [10, 10, 80, 10], 0)
        pygame.draw.rect(self.surf, WHITE, [10, 30, 80, 5], 0)
        self.surf.blit(self.txt_surf, self.txt_rect)
        # dynamic graphics - button surface #
        self.button_surf = pygame.surface.Surface((20, 20))
        self.button_surf.fill(TRANS)
        self.button_surf.set_colorkey(TRANS)
        pygame.draw.circle(self.button_surf, BLACK, (10, 10), 6, 0)
        pygame.draw.circle(self.button_surf, WHITE, (10, 10), 4, 0)

    def draw(self):
        # static
        surf = self.surf.copy()
        # dynamic
        pos = (10+int((self.val-self.mini)/(self.maxi-self.mini)*80), 33)
        self.button_rect = self.button_surf.get_rect(center=pos)
        surf.blit(self.button_surf, self.button_rect)
        self.button_rect.move_ip(self.xpos, self.ypos)  # move of button box to correct screen position
        # screen
        screen.blit(surf, (self.xpos, self.ypos))

    def move(self):
        self.val = (pygame.mouse.get_pos()[0] - self.xpos - 10) / 80 * (self.maxi - self.mini) + self.mini
        if self.val < self.mini:
            self.val = self.mini
        if self.val > self.maxi:
            self.val = self.maxi


class Avoid():
    def __init__(self,x,y):
        self.x = x
        self.y = y


class Boid:
    global params

    def __init__(self, location, velocity):
        self.x = location[0]
        self.y = location[1]
        self.vx = velocity[0]
        self.vy = velocity[1]
        self.neighbors = []
        self.neighborsobjs = []
        self.dvx = 0
        self.dvy = 0
        self.dvx3 = 0
        self.dvy3 = 0

    def functions(self, this_boid, neighbors, scalealign, scalecohesion, scaleseparation, objs):
        length = len(neighbors)
        if length == 1:
            # Align
            self.dvx = 0
            self.dvy = 0
            # Cohesion
            self.dvx1 = 0
            self.dvy1 = 0
            # Separation
            self.dvx2 = 0
            self.dvy2 = 0
            return

        cvx = 0
        cvy = 0
        cx = 0
        cy = 0
        sx = 0
        sy = 0
        for boid in neighbors:
            # Align
            cvx += boid.vx
            cvy += boid.vy
            # Cohesion
            cx += boid.x
            cy += boid.y
            # Separation
            if distance((this_boid.x,this_boid.y),(boid.x,boid.y)) > 0.01:
                sx += (params[5]/(boid.x - this_boid.x))
                sy += (params[5]/(boid.y - this_boid.y))
        # Object avoidance
        for obj in objs:
            if distance((this_boid.x,this_boid.y),(obj.x,obj.y)) > 0.01:
                sx += (20*params[5]/(obj.x - this_boid.x))
                sy += (20*params[5]/(obj.y - this_boid.y))

        cvx = cvx/length
        cvy = cvy/length
        cx = cx/length
        cy = cy/length
        svx = sx/(length + len(objs))
        svy = sy/(length + len(objs))
        dx = (cx - self.x)
        dy = (cy - self.y)
        self.dvx = (cvx-self.vx)*scalealign
        self.dvy = (cvy-self.vy)*scalealign
        self.dvx1 = dx*scalecohesion
        self.dvy1 = dy*scalecohesion
        self.dvx2 = -svx*scaleseparation
        self.dvy2 = -svy*scaleseparation

    def apply_noise(self, count, scale_noise):
        # Change noise direction every 20 frames
        if count % 20 == 0:
            self.dvx3 = (random.random()*params[4]*scale_noise) - (params[4]*scale_noise/2)
            self.dvy3 = (random.random()*params[4]*scale_noise) - (params[4]*scale_noise/2)


def rotate(origin, points, angle):
    rotated = []
    for point in points:
        rotated.append((origin[0] + math.cos(angle) * (point[0] - origin[0]) - math.sin(angle) * (point[1] - origin[1]),origin[1] + math.sin(angle) * (point[0] - origin[0]) + math.cos(angle) * (point[1] - origin[1])))
    return rotated


def draw_boids(boids, colors, objs):
    count3 = 0
    for boid in boids:
        if boid.x > screen_size[0]:
            boid.x = 0
        if boid.x < 0:
            boid.x = screen_size[0]
        if boid.y > screen_size[1]-80:
            boid.y = 0
        if boid.y < 0:
            boid.y = screen_size[1]-80

        theta = math.atan(boid.vy/boid.vx)
        if boid.vx < 0 and boid.vy > 0:
            theta = 3.14 + theta
        if boid.vx < 0 and boid.vy < 0:
            theta = 3.14 + theta
        points = [(boid.x+10, boid.y), (boid.x-10, boid.y+5), (boid.x-10, boid.y-5)]
        pygame.draw.polygon(screen, colors[count3], rotate((boid.x, boid.y), points, theta))
        count3 += 1
        if count3 > 32:
            count3 = 0

        for obj in objs:
            pygame.draw.circle(screen, (255, 0, 0), (obj.x, obj.y), 10)

    if show_one_neighbors:
        for boid in boids[0].neighbors:
            pygame.draw.line(screen, [255, 0, 0], (boids[0].x, boids[0].y), (boid.x, boid.y))
        for obj in boids[0].neighborsobjs:
            pygame.draw.line(screen, [255, 0, 0], (boids[0].x, boids[0].y), (obj.x, obj.y))
        surface = pygame.Surface((screen_size[0], screen_size[1]), pygame.SRCALPHA)
        pygame.draw.circle(surface, [125,125,125,100], (int(boids[0].x), int(boids[0].y)), int(params[5]))
        screen.blit(surface, (0,0))

def move_boids(boids):
    for boid in boids:
        boid.x = boid.x + boid.vx*dt
        boid.y = boid.y + boid.vy*dt


def distance(point1, point2):
    return math.sqrt((point1[1]-point2[1])**2+(point1[0]-point2[0])**2)


# Only loops over boids in the quad
def quadneighbor(this_boid, quad, objs):
    global params
    global show_neighbors
    this_boid.neighbors = []
    for boid in quad:
        if distance((this_boid.x, this_boid.y), (boid.x, boid.y)) < params[5]:
            this_boid.neighbors.append(boid)
            if show_neighbors:
                pygame.draw.line(screen, [255, 0, 0], (this_boid.x, this_boid.y), (boid.x, boid.y))
    this_boid.neighborsobjs = []
    for obj in objs:
        if distance((this_boid.x, this_boid.y), (obj.x, obj.y)) < params[5]:
            this_boid.neighborsobjs.append(obj)
            if show_neighbors:
                pygame.draw.line(screen, [255, 0, 0], (this_boid.x, this_boid.y), (obj.x, obj.y))


# Loops over every boid object
def neighbor(this_boid, boids, objs):
    global params
    global show_neighbors
    this_boid.neighbors = []
    for boid in boids:
        if distance((this_boid.x, this_boid.y), (boid.x, boid.y)) < params[5]:
            this_boid.neighbors.append(boid)
            if show_neighbors:
                pygame.draw.line(screen, [255, 0, 0], (this_boid.x, this_boid.y), (boid.x, boid.y))
    this_boid.neighborsobjs = []
    for obj in objs:
        if distance((this_boid.x, this_boid.y), (obj.x, obj.y)) < params[5]:
            this_boid.neighborsobjs.append(obj)
            if show_neighbors:
                pygame.draw.line(screen, [255, 0, 0], (this_boid.x, this_boid.y), (obj.x, obj.y))

def init_boids(n):
    global params
    boids = []
    for i in range(0, n):
        x = random.randint(20, screen_size[0]-20)
        y = random.randint(20, screen_size[1]-100)
        theta = random.random()*6.28
        boid = Boid([x,y],[params[4]*math.cos(theta), params[4] * math.sin(theta)])
        boids.append(boid)
    return boids

pygame.init()
font = pygame.font.SysFont("Arial", 12)
screen = pygame.display.set_mode((screen_size[0], screen_size[1]))
dt = .1
running = 1
count = 0
boids = init_boids(nboids)
objs = []

# Sliders for parameter values
scale_align_slider = Slider("Align",scale_align,.4,0,10)
scale_cohesion_slider = Slider("Cohesion",scale_cohesion,.2,0,115)
scale_separation_slider = Slider("Separation",scale_separation,1.6,0,220)
scale_noise_slider = Slider("Noise",scale_noise,.2,0,325)
scale_speed_slider = Slider("Speed",speed,40,1,430)
scale_perception_slider = Slider("Perception",perception,200,0.1,535)
slides = [scale_align_slider, scale_cohesion_slider, scale_separation_slider, scale_noise_slider, scale_speed_slider, scale_perception_slider]


# Quad tree speed optimization
quad = QuadTree(npartitions, screen_size[0], screen)

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = 0
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for s in slides:
                if s.button_rect.collidepoint(pos):
                    s.hit = True
            if  (screen_size[0] - 10 > pos[0] > 10) and (screen_size[1] - 90 > pos[1] > 10):
                objs.append(Avoid(pos[0],pos[1]))

        elif event.type == pygame.MOUSEBUTTONUP:
            for s in slides:
                s.hit = False

    count2 = 0
    for s in slides:
        if s.hit:
            s.move()
        params[count2] = s.val
        count2 += 1

    screen.fill((0, 0, 0))

    if use_quads:
        # Quad tree group all boids into quadrants
        quad.get_objs(boids)

        draw_boids(boids, colorscheme, objs)
        text = font.render("Boids: Dylan Herrera", True, (0, 255, 255))
        screen.blit(text, [screen_size[0]-110, screen_size[1]-80])
        move_boids(boids)

        for quadrant in quad.quads:
            for boid in quadrant:
                boid.neighbors = []
                quadneighbor(boid, quadrant, objs)

                # Apply properties
                boid.functions(boid,boid.neighbors, params[0], params[1], params[2], boid.neighborsobjs)
                # Update align
                boid.vx = boid.vx + boid.dvx
                boid.vy = boid.vy + boid.dvy
                # Normalize
                boid.vx = (boid.vx/math.sqrt(boid.vx**2+boid.vy**2))*params[4]
                boid.vy = (boid.vy/math.sqrt(boid.vx**2+boid.vy**2))*params[4]
                # Update cohesion
                boid.vx = boid.vx + boid.dvx1
                boid.vy = boid.vy + boid.dvy1
                # Normalize
                boid.vx = (boid.vx/math.sqrt(boid.vx**2+boid.vy**2))*params[4]
                boid.vy = (boid.vy/math.sqrt(boid.vx**2+boid.vy**2))*params[4]
                # Update separation
                boid.vx = boid.vx + boid.dvx2
                boid.vy = boid.vy + boid.dvy2
                # Normalize
                boid.vx = (boid.vx/math.sqrt(boid.vx**2+boid.vy**2))*params[4]
                boid.vy = (boid.vy/math.sqrt(boid.vx**2+boid.vy**2))*params[4]

                if params[3] != 0:
                    boid.apply_noise(count, params[3])
                    # Update noise
                    boid.vx = boid.vx + boid.dvx3
                    boid.vy = boid.vy + boid.dvy3
                    # Normalize
                    boid.vx = (boid.vx/math.sqrt(boid.vx**2+boid.vy**2))*params[4]
                    boid.vy = (boid.vy/math.sqrt(boid.vx**2+boid.vy**2))*params[4]

    if not use_quads:
        draw_boids(boids, colorscheme, objs)
        text = font.render("Boids: Dylan Herrera", True, (0, 255, 255))
        screen.blit(text, [screen_size[0]-110, screen_size[1]-80])
        move_boids(boids)

        for boid in boids:
            boid.neighbors = []
            neighbor(boid, boids, objs)

            # Apply properties
            boid.functions(boid,boid.neighbors,params[0], params[1], params[2], boid.neighborsobjs)
            # Update align
            boid.vx = boid.vx + boid.dvx
            boid.vy = boid.vy + boid.dvy
            # Normalize
            boid.vx = (boid.vx/math.sqrt(boid.vx**2+boid.vy**2))*params[4]
            boid.vy = (boid.vy/math.sqrt(boid.vx**2+boid.vy**2))*params[4]
            # Update cohesion
            boid.vx = boid.vx + boid.dvx1
            boid.vy = boid.vy + boid.dvy1
            # Normalize
            boid.vx = (boid.vx/math.sqrt(boid.vx**2+boid.vy**2))*params[4]
            boid.vy = (boid.vy/math.sqrt(boid.vx**2+boid.vy**2))*params[4]
            # Update separation
            boid.vx = boid.vx + boid.dvx2
            boid.vy = boid.vy + boid.dvy2
            # Normalize
            boid.vx = (boid.vx/math.sqrt(boid.vx**2+boid.vy**2))*params[4]
            boid.vy = (boid.vy/math.sqrt(boid.vx**2+boid.vy**2))*params[4]

            if params[3] != 0:
                boid.apply_noise(count, params[3])
                # Update noise
                boid.vx = boid.vx + boid.dvx3
                boid.vy = boid.vy + boid.dvy3
                # Normalize
                boid.vx = (boid.vx/math.sqrt(boid.vx**2+boid.vy**2))*params[4]
                boid.vy = (boid.vy/math.sqrt(boid.vx**2+boid.vy**2))*params[4]

    count += 1
    if count > 20:
        count = 0

    for s in slides:
        s.draw()

    pygame.display.flip()

pygame.quit()
