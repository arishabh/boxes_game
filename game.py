import pygame
from time import sleep, time
import random

black = (0,0,0)
red = (202,0,42)
lred = (255,80,79)
blue = (8,96,168)
lblue = (166,189,219)
grey = (100,100,100)
white = (255,255,255)

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.size = 10
    
    def draw(self, screen):
        pygame.draw.circle(screen, black,  (self.x, self.y), self.size)


class Line:
    def __init__(self, color, start, stop):
        self.thickness = 19
        self.color = color
        self.start = start
        self.stop = stop
        self.start_stop = (start, stop)

    def draw(self, screen):
        pygame.draw.line(screen, self.color, self.start, self.stop, self.thickness)

    def __eq__(self, other):
        return self.start_stop == other.start_stop

    def change_color(self, color):
        self.color = color


GRID_DIST = 80
NOS = 10
MARGIN = 2

def main():
    pygame.init()

    screen_size = [1000,1000]
    quit = False
    clk_spd = 30

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(screen_size)

    grid = []
    for i in range(MARGIN, MARGIN+NOS):
        for j in range(MARGIN, MARGIN+NOS):
            grid.append(Dot(i*GRID_DIST, j*GRID_DIST))

    lines = []
    turn = True

    while not quit:
        clock.tick(clk_spd)
        screen.fill(white)

        if turn:
            curr_color = red
            curr_lcolor = lred
        else:
            curr_color = blue
            curr_lcolor = lblue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_Q:
                    quit = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                light_line.change_color(curr_color)
                lines.append(light_line)
                turn = not turn

            mouse_pos = pygame.mouse.get_pos()
            
        def get_dist(p1, p2):
            return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

        dist = list(map(lambda a: get_dist(a.pos, mouse_pos), grid))
        nearest = grid[dist.index(min(dist))]
        dist.remove(min(dist))
        second_nearest = grid[dist.index(min(dist))]
        while not((nearest.pos[0] == second_nearest.pos[0] or nearest.pos[1] == second_nearest.pos[1]) and get_dist(nearest.pos, second_nearest.pos) == GRID_DIST):
            dist.remove(min(dist))
            second_nearest = grid[dist.index(min(dist))]
        light_line = Line(curr_lcolor, nearest.pos, second_nearest.pos)
        light_line.draw(screen)
        nearest.draw(screen)
        second_nearest.draw(screen)

        for line in lines: line.draw(screen)
        for dot in grid: dot.draw(screen)
        pygame.display.update()
            
    pygame.quit()

main()
