import pygame
from time import sleep, time
import random

black = (0,0,0)
red = (255,0,0)
blue = (0,0,255)
grey = (100,100,100)
white = (255,255,255)

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.size = 8
    
    def draw(self, screen):
        pygame.draw.circle(screen, black,  (self.x, self.y), self.size)


class Line:
    def __init__(self, color, start, stop):
        self.color = color
        self.start = start
        self.stop = stop
        self.thickness = 5

    def draw(self, screen):
        pygame.draw.line(screen, self.color, self.start, self.stop, self.thickness)

GRID_DIST = 80

def main():
    pygame.init()

    screen_size = [1000,1000]
    quit = False
    clk_spd = 30

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(screen_size)
    screen.fill(white)

    grid = []
    for i in range(1,11):
        for j in range(1,11):
            dot = Dot(i*GRID_DIST, j*GRID_DIST)
            grid.append(dot)
            dot.draw(screen)
    l = Line(blue, grid[0].pos, grid[1].pos)
    l.draw(screen)
    pygame.display.update()

    while not quit:
        clock.tick(clk_spd)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
    pygame.quit()

main()
