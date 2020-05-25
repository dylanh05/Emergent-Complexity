import pygame
from pygame.locals import *
import random

global dt
dt = .00001
global points
points = []

class Point:
    def __init__(self, pos):
        self.pos = pos
        self.color = (random.random()*255, random.random()*255, random.random()*255)
        self.trail = []

    def draw_point(self):
        if self.pos[0] < 900 and self.pos[1] < 900 and self.pos[0] > -900 and self.pos[1] > -900:
            pygame.draw.circle(window, self.color, [int(self.pos[0]+480), int(self.pos[1]+270)], 1)
            for line in self.trail:
                pygame.draw.line(window, self.color, [line[0][0]+480, line[0][1]+270], [line[1][0]+480, line[1][1]+270], 1)

    def update_pos(self, t):
        oldx = self.pos[0]
        oldy = self.pos[1]
        if self.pos[0] < 900 and self.pos[1] < 900 and self.pos[0] > -900 and self.pos[1] > -900:
            dx = -self.pos[0]**2 + self.pos[1] - t*self.pos[0]
            dy = self.pos[0]**2 + self.pos[1]**2 - t**2 - self.pos[0]*self.pos[1] + self.pos[1]*t - self.pos[0] + self.pos[1]
            self.pos[0] = self.pos[0] + dx*dt
            self.pos[1] = self.pos[1] + dy*dt
            self.trail.append(([oldx, oldy], [self.pos[0],self.pos[1]]))
            if len(self.trail) > 100:
                self.trail.pop(0)


def init_anim(n):
    global points
    points = []
    for i in range(n):
        points.append(Point([random.random()*960-480, random.random()*540-270]))

def draw_points(points):
    for point in points:
        point.draw_point()

def move_points(points, t):
    for point in points:
        point.update_pos(t)

def delete_points(points):
    for i in range(0, len(points)):
        if points[i].pos[0] > 900 and points[i].pos[1] > 900 and points[i].pos[0] < -900 and points[i].pos[1] < -900:
            points.pop(i)
            break

# Pygame initialization
pygame.init()
window = pygame.display.set_mode((960, 540))

running = 1
init_anim(100)
t = -6
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = 0

    window.fill((0, 0, 0))
    draw_points(points)
    move_points(points, t)
    delete_points(points)

    t += 1
    pygame.display.flip()

pygame.quit()
