import pygame
from time import sleep, time
import random

black = (0,0,0)
red = (202,0,42)
lred = (241,179,179)
blue = (8,96,168)
lblue = (166,189,219)
grey = (100,100,100)
white = (255,255,255)

GRID_DIST = 80
NOS = 10
MARGIN = 2
SSIZE = [1000,1000]

class Dot:
    def __init__(self, x=0, y=0, pos=(-1,-1)):
        if pos == (-1,-1):
            self.x = x
            self.y = y
            self.pos = (x, y)
        else:
            self.pos = pos
            self.x = pos[0]
            self.y = pos[1]
        self.size = 10
    
    def draw(self, screen):
        pygame.draw.circle(screen, black,  (self.x, self.y), self.size)

    def one_right(self):
        return (self.x+GRID_DIST, self.y)

    def one_left(self):
        return (self.x-GRID_DIST, self.y)

    def one_up(self):
        return (self.x, self.y-GRID_DIST)

    def one_down(self):
        return (self.x, self.y+GRID_DIST)

    def __lt__(self, other):
        return(self.pos < other.pos)

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
        return self.start_stop == other.start_stop or self.start_stop == (other.start_stop[1], other.start_stop[0])

    def change_color(self, color):
        self.color = color

class Box:
    def __init__(self, color, coor):
        self.color = color
        self.x = coor[0]
        self.y = coor[1]
        self.offset = 15
        self.is_shielded = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color,  (self.x+self.offset, self.y+self.offset, GRID_DIST-self.offset*2, GRID_DIST-self.offset*2))

class Player:
    def __init__(self, color, lcolor):
        self.color = color
        self.lcolor = lcolor
        self.points = []
        self.lines = []
        self.bombs = 2
        self.shields = 1

    def get_points(self):
        return len(self.points)

    def in_lines(self, lines):
        return all(map(lambda l: l in self.lines, lines))
    
    def __eq__(self, other):
        return self.color == other.color


def main():
    pygame.init()

    quit = False
    clk_spd = 30

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(SSIZE)

    grid = []
    for i in range(MARGIN, MARGIN+NOS):
        for j in range(MARGIN, MARGIN+NOS):
            grid.append(Dot(i*GRID_DIST, j*GRID_DIST))

    lines = []
    points = []
    turn = True

    global player1
    global player2

    player1 = Player(red, lred)
    player2 = Player(blue, lblue)
    curr_player = player1

    while not quit:
        global change_player
        clock.tick(clk_spd)
        screen.fill(white)
        pygame.font.init() 
        myfont = pygame.font.SysFont('Comic Sans MS', 100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True

            if event.type == pygame.MOUSEBUTTONDOWN:
                if light_line not in player1.lines and light_line not in player2.lines: 
                    light_line.change_color(curr_player.color)
                    curr_player.lines.append(light_line)
                    last = Dot(pos=light_line.start)
                    second_last = Dot(pos=light_line.stop)
                    change_player = True
                    def check_point(all_lines):
                        global change_player
                        if all(map(lambda l: l in player1.lines or l in player2.lines, all_lines)):
                            curr_player.points.append(Box(curr_player.color, l1.start))
                            change_player = False

                    if last.y == second_last.y:
                        if second_last.x < last.x: last, second_last = second_last, last
                        l1 = Line(curr_player.color, last.one_up(), second_last.one_up())
                        l2 = Line(curr_player.color, second_last.one_up(), second_last.pos)
                        l3 = light_line
                        l4 = Line(curr_player.color, last.pos, last.one_up())
                        all_lines = [l1, l2, l3, l4]
                        check_point(all_lines)

                        l1 = Line(curr_player.color, last.pos, second_last.pos)
                        l2 = Line(curr_player.color, second_last.pos, second_last.one_down())
                        l4 = Line(curr_player.color, second_last.one_down(), last.one_down())
                        l3 = Line(curr_player.color, last.one_down(), last.pos)
                        all_lines = [l1, l2, l3, l4]
                        check_point(all_lines)

                    elif last.x == second_last.x:
                        if last.y < second_last.y: last, second_last = second_last, last
                        l1 = Line(curr_player.color, second_last.pos, second_last.one_right())
                        l2 = Line(curr_player.color, second_last.one_right(), last.one_right())
                        l3 = Line(curr_player.color, last.one_right(), last.pos)
                        l4 = light_line
                        all_lines = [l1, l2, l3, l4]
                        check_point(all_lines)

                        l1 = Line(curr_player.color, second_last.one_left(), second_last.pos)
                        l2 = light_line
                        l4 = Line(curr_player.color, last.pos, last.one_left())
                        l3 = Line(curr_player.color, last.one_left(), second_last.one_left())
                        all_lines = [l1, l2, l3, l4]
                        check_point(all_lines)
            
                    if change_player:
                        curr_player = player1 if curr_player == player2 else player2

            
        def get_dist(p1, p2):
            return abs(((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5)

        mouse_pos = pygame.mouse.get_pos()
        dist = list(map(lambda a: get_dist(a.pos, mouse_pos), grid))
        if dist:
            dist_point = list(zip(dist, grid))
            nearest = min(dist_point)[1]
            dist_point.remove(min(dist_point))
            second_nearest = min(dist_point)[1]
            while not((nearest.pos[0] == second_nearest.pos[0] or nearest.pos[1] == second_nearest.pos[1]) and get_dist(nearest.pos, second_nearest.pos) == GRID_DIST):
                dist_point.remove(min(dist_point))
                second_nearest = min(dist_point)[1]
        light_line = Line(curr_player.lcolor, nearest.pos, second_nearest.pos)
        light_line.draw(screen)
        nearest.draw(screen)
        second_nearest.draw(screen)

        textsurface = myfont.render(str(player1.get_points()), False, red)
        screen.blit(textsurface,(10,10))
        textsurface = myfont.render(str(player2.get_points()), False, blue)
        screen.blit(textsurface,(10,80))
        for point in player1.points: point.draw(screen)
        for point in player2.points: point.draw(screen)
        for line in player1.lines: line.draw(screen)
        for line in player2.lines: line.draw(screen)
        for dot in grid: dot.draw(screen)
        if player2.get_points() + player1.get_points() == 81:
            if player1.get_points() > player2.get_points:
                screen.fill(white)
                winfont = pygame.font.SysFont('Comic Sans MS', 500)
                textsurface = winfont.render("Red Wins!", False, red)
                screen.blit(textsurface, (200, 450))
            else:
                screen.fill(white)
                winfont = pygame.font.SysFont('Comic Sans MS', 500)
                textsurface = winfont.render("Blue Wins!", False, blue)
                screen.blit(textsurface, (200, 450))
            quit = True
        pygame.display.update()
            
    pygame.quit()

while True:
    main()
