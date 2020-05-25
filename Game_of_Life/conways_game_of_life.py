# Dylan Herrera
# Simple Conway's game of life implementation

# Click on squares to activate, then use right arrow key to start simulation
# Either step through simulation interactively, or set starting configuration and run

import pygame
from pygame.locals import *

# --------------- Manipulate ---------------
step_through = True
screen_size = 600   # Square screen
n = 30     # Number of squares in row
# ------------------------------------------

square_size = screen_size / n
grid = []


class Square:
    def __init__(self, index, val):
        self.index = index
        self.val = val  # 0 dead, 1 alive

    def draw_square(self):
        if self.val:
            pygame.draw.rect(screen, (230, 230, 230), [self.index[0]*square_size, self.index[1]*square_size, square_size, square_size])
        pygame.draw.line(screen, (255, 255, 255), [self.index[0]*square_size, self.index[1]*square_size], [self.index[0]*square_size + square_size, self.index[1]*square_size], 1)
        pygame.draw.line(screen, (255, 255, 255), [self.index[0]*square_size, self.index[1]*square_size], [self.index[0]*square_size, self.index[1]*square_size+square_size], 1)
        pygame.draw.line(screen, (255, 255, 255), [self.index[0]*square_size+square_size, self.index[1]*square_size], [self.index[0]*square_size + square_size, self.index[1]*square_size + square_size], 1)
        pygame.draw.line(screen, (255, 255, 255), [self.index[0]*square_size, self.index[1]*square_size + square_size], [self.index[0]*square_size + square_size, self.index[1]*square_size + square_size], 1)


def init_grid():
    global grid
    for i in range(n):
        row = []
        for j in range(n):
            row.append(Square([i, j], 0))
        grid.append(row)


def draw_grid():
    global grid
    for row in grid:
        for square in row:
            square.draw_square()


def update_grid(grid):
    new_grid = []
    for i in range(n):
        row = []
        for j in range(n):
            count = 0
            # Compress
            if i != n-1:
                if grid[i+1][j].val:
                    count += 1
            if i != n-1 and j != n-1:
                if grid[i+1][j+1].val:
                    count += 1
            if i != n-1 and j != 0:
                if grid[i+1][j-1].val:
                    count += 1
            if i != 0:
                if grid[i-1][j].val:
                    count += 1
            if i != 0 and j != n-1:
                if grid[i-1][j+1].val:
                    count += 1
            if i != 0 and j != 0:
                if grid[i-1][j-1].val:
                    count += 1
            if j != 0:
                if grid[i][j-1].val:
                    count += 1
            if j != n-1:
                if grid[i][j+1].val:
                    count += 1

            if (grid[i][j].val == 1 and (count == 2 or count == 3)) or (grid[i][j].val == 0 and count == 3):
                val = 1
            else:
                val = 0
            row.append(Square([i, j], val))
        new_grid.append(row)
    return  new_grid

def add_squares(pos):
    for i in range(n):
        for j in range(n):
            if i*square_size + square_size > pos[0] > i*square_size and j * square_size + square_size > pos[1] > j * square_size:
                grid[i][j].val = 1


# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((screen_size + 1, screen_size + 1))
running = 1

init_grid()
count = 0
cont = False
while running:
    step = False
    for event in pygame.event.get():
        if event.type == QUIT:
            running = 0

        if event.type == pygame.MOUSEBUTTONDOWN and not cont:
            pos = pygame.mouse.get_pos()
            add_squares(pos)
        if event.type == pygame.MOUSEBUTTONDOWN and step_through:
            pos = pygame.mouse.get_pos()
            add_squares(pos)

        if event.type == pygame.KEYDOWN and not cont:
            if event.key == pygame.K_RIGHT:
                cont = True

        if step_through and cont:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    step = True

    if not step_through and cont:
        if count % 1 == 0:
            step = True

    screen.fill((47, 79, 79))

    if step:
        grid = update_grid(grid)

    draw_grid()
    pygame.display.flip()

    count += 1
    if count > 1000:
        count = 0

pygame.quit()
