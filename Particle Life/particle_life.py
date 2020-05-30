# Change attractions from characteristic of a color to characteristic of a pair of colors

from pygame.locals import *
import math
import random
from QuadTree import *

radius = 50
attractions = []
colors = []
particles = []
screen_size = [400, 400]
dt = .1

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
orange = (255, 165, 0)
yellow = (255, 255, 0)
purple = (102, 0, 204)

class Particle:
    def __init__(self, pos, vel, col):
        self.pos = pos
        self.vel = vel
        self.color = col
        self.x = pos[0]
        self.y = pos[1]
        self.attract = gen_attraction(self.color, attractions, colors)

    def update_neighbors(self, obj, quad):
        self.neighbors = []
        quadcount = quad.find_quad(obj, quad.treelocs)
        for particle in quad.quads[quadcount]:
            distance = math.sqrt((self.x-particle.pos[0])**2+(self.y-particle.pos[1])**2)
            if radius > distance > .01:
                self.neighbors.append(particle)

    def draw_particle(self):
        pygame.draw.circle(screen, self.color, [int(self.x), int(self.y)], 4)

    def update_vel(self):
        ax = 0
        ay = 0
        for particle in self.neighbors:
            dy = particle.y-self.y
            dx = particle.x-self.x
            if dx < 0.001:
                dx = .001
            theta = math.atan(dy/dx)
            if (dx < 0 and dy > 0) or (dx < 0 and dy < 0):
                theta += math.pi
            distance = math.sqrt((self.x-particle.pos[0])**2+(self.y-particle.pos[1])**2)
            attraction = particle.attract
            mid = (attraction[0]+attraction[1])/2
            if distance <= attraction[0]:
                a = (distance - attraction[0])**4
            elif attraction[0] < distance <= mid:
                a = (attraction[2]*distance) - (attraction[2]*attraction[0])
            elif mid < distance <= attraction[1]:
                a = (-1*attraction[2]*distance) + (attraction[2]*attraction[1])
            else:
                a = 0
            ax += a*math.cos(theta)
            ay += a*math.sin(theta)

        self.vel[0] = self.vel[0] - ax*dt
        self.vel[1] = self.vel[1] - ay*dt

        # Friction
        self.vel[0] = self.vel[0] - (self.vel[0]/500) # MAY NEED TO BE ADJUSTED
        self.vel[1] = self.vel[1] - (self.vel[1]/500) # MAY NEED TO BE ADJUSTED

        # Noise
        self.vel[0] += .05*(random.random()-.5)
        self.vel[1] += .05*(random.random()-.5)

    def update_pos(self):
        self.x = self.x + self.vel[0]*dt
        self.y = self.y + self.vel[1]*dt
        if self.x > screen_size[0] or self.x < 0:
            self.vel[0] = -self.vel[0]
        if self.y > screen_size[1] or self.y < 0:
            self.vel[1] = -self.vel[1]


def init_particles(n):
    global particles
    for i in range(n):
        color = random.randint(0, 5)
        if color == 0:
            color = blue
        if color == 1:
            color = green
        if color == 2:
            color = red
        if color == 3:
            color = yellow
        if color == 4:
            color = purple
        if color == 5:
            color = orange
        particles.append(Particle([random.random()*screen_size[0], random.random()*screen_size[1]], [random.random()-.5, random.random()-.5], color))


def gen_attraction(color, attractions, colors):
    for i in range(len(colors)):
        if colors[i] == color:
            return attractions[i]
    colors.append(color)
    min = 1 + random.random()*2
    max = 3+random.random()*10
    slope = random.random()*2-1
    if random.random() > .5:
        sign = 1
    else:
        sign = -1
    slope = slope*sign
    attract_function = [min, max, slope]
    attractions.append(attract_function)
    return attract_function




# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((screen_size[0], screen_size[1]))
running = 1

# Quad tree initialization
npartitions = 2     # Default 2 must be nonzero
quad = QuadTree(npartitions, screen_size[0], screen)
init_particles(200)

while running:
    step = False
    for event in pygame.event.get():
        if event.type == QUIT:
            running = 0

    screen.fill((0, 0, 0))

    for particle in particles:
        particle.draw_particle()
        particle.update_neighbors(particle, quad)
        particle.update_pos()
        particle.update_vel()

    quad.get_objs(particles)


    pygame.display.flip()


pygame.quit()
