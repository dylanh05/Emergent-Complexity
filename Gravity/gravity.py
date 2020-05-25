import pygame
from pygame.locals import *
import math

# Pseudoconstants
dt = .01
G = 400000

class Body:
    def __init__(self, x, y, vx, vy, mass):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.ax = 0
        self.ay = 0
        self.mass = mass
        self.tail = []

    def gravity(self, bodies):
        self.ax = 0
        self.ay = 0
        for body in bodies:
            dist = distance(body.x, body.y, self.x, self.y)
            if dist == 0:
                continue
            theta = math.atan((body.y-self.y)/(body.x - self.x))
            if body.x-self.x < 0 and body.y-self.y > 0:
                theta = theta - math.pi
            if body.x-self.x < 0 and body.y-self.y < 0:
                theta = theta + math.pi

            g = G * body.mass/(dist**2)
            self.ax += g*math.cos(theta)
            self.ay += g*math.sin(theta)

    def update_pos(self):
        if self.x > screen_size[0]:
            self.x = 0
        if self.x < 0:
            self.x = screen_size[0]
        if self.y > screen_size[1]:
            self.y = 0
        if self.y < 0:
            self.y = screen_size[1]
        self.vx = self.vx + self.ax*dt
        self.vy = self.vy + self.ay*dt
        oldx = self.x
        oldy = self.y
        self.x = self.x + self.vx*dt
        self.y = self.y + self.vy*dt
        self.tail.append(([oldx, oldy], [self.x, self.y]))
        if len(self.tail) > 200:
            self.tail.pop(0)

    def draw_body(self):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 5)
        for line in self.tail:
            pygame.draw.line(screen, (255, 0, 0), line[0],line[1],2)


def distance(x1, y1, x2, y2):
    return math.sqrt((x2-x1)**2+(y2-y1)**2)

# Pygame initialization
screen_size = [1200, 650]
pygame.init()
screen = pygame.display.set_mode((screen_size[0], screen_size[1]))
running = 1
bodies = []

bodies.append(Body(500.4, 350, 0, 0, 5))
bodies.append(Body(800.3, 350, 0, 70, .000005))
bodies.append(Body(500.3, 250, -100, 100, .000005))
bodies.append(Body(500.2, 250, 150, 100, .000005))
bodies.append(Body(600.3, 350, 0, 120, .000005))
bodies.append(Body(601.3, 355, 100, 120, .0000000005))
bodies.append(Body(600.1, 450, -110, -10, .000005))
bodies.append(Body(100.1, 150, 30, 0, .000005))
bodies.append(Body(800.1, 550, -70, 0, .000005))
bodies.append(Body(200.1, 550, 50, 0, .000005))
bodies.append(Body(500.1, 370, -280, 0, .000005))

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = 0

    screen.fill((0, 0, 0))

    for body in bodies:
        body.gravity(bodies)
        body.update_pos()
        body.draw_body()

    pygame.display.flip()

pygame.quit()
