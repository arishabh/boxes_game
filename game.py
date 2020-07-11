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
yellow = (255, 230, 0)

GRID_DIST = 80
NOS = 10
MARGIN = 2
SSIZE = [1000,1000]

pygame.font.init() 

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
        self.imgx = self.x+self.offset
        self.imgy = self.y+self.offset
        self.imgxy = (self.imgx, self.imgy)
        self.is_shielded = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color,  (self.imgx, self.imgy, GRID_DIST-self.offset*2, GRID_DIST-self.offset*2))
        if self.is_shielded:
            x = (self.imgx+(GRID_DIST-self.offset*2)/2)
            y = (self.imgy+(GRID_DIST-self.offset*2)/2)
            pygame.draw.circle(screen, black, (x, y, 10))

class Player:
    def __init__(self, ind, color, lcolor):
        self.index = ind
        self.color = color
        self.lcolor = lcolor
        self.points = []
        self.lines = []
        self.bombs = 2
        self.bomb = Bomb()
        self.bomb_selected = False
        self.shield = Shield()
        self.shields = 2
        self.shield_selected = False

    def get_points(self):
        return len(self.points)

    def in_lines(self, lines):
        return all(map(lambda l: l in self.lines, lines))
    
    def __eq__(self, other):
        return self.color == other.color

    def draw(self, screen, mpos):
        for p in self.points: p.draw(screen)
        for l in self.lines: l.draw(screen)
        self.bomb.draw(screen, mpos, self.bombs)
        self.shield.draw(screen, mpos)
        myfont = pygame.font.SysFont('Comic Sans MS', 100)
        textsurface = myfont.render(str(self.get_points()), False, self.color)
        screen.blit(textsurface,(10, (self.index*70)+10))

    def select_bomb(self):
        self.bomb_selected = True
        self.bomb.select()

    def use_bomb(self):
        self.bomb_selected = False
        self.bomb = Bomb()
        self.bombs -= 1

    def select_shield(self):
        self.shield_selected = True
        self.shield.select()

    def got_bombed(self, pos, effect_area):
        end = (pos[0]+effect_area[0], pos[1]+effect_area[1])
        # self.points = [p for p in self.points if p.imgxy>pos and p.imgxy<end]
        self.points = list(filter(lambda p: p<pos or p>end, self.points))
        print(self.points)
        self.lines = [l for l in self.lines if (l.start>pos and l.start<end) or (l.stop>pos and l.stop<end)]
        print(self.lines)

    def got_shielded(self, pos, effect_area):
        end = (pos[0]+effect_area[0], pos[1]+effect_area[1])
        for p in self.points:
            if p.imgxy>pos and p.imgxy<end:
                p.is_shielded = True
    
    def deselect_bomb(self):
        self.bomb_selected = False
        self.bomb.selected = False

    def deselect_shield(self):
        self.shield_selected = False
        self.shield.selected = False

    def reset(self):
        self.points = []
        self.lines = []
        self.bombs = 2
        self.bomb = Bomb()
        self.bomb_selected = False
        self.shield = Shield()
        self.shields = 2
        self.shield_selected = False

class Bomb:
    def __init__(self):
        self.pos = (70, 400)
        self.rad = 50
        self.big_rad = 55
        self.small_rad = 20
        self.selected = False
        boxes_effect = 4
        self.effect_width = boxes_effect*GRID_DIST
        self.effect_height = boxes_effect*GRID_DIST
        self.effect_area = (self.effect_width, self.effect_height)
        self.top_point = (0,0)
        self.near_pos = (0,0)

    def draw(self, screen, mpos, nos):
        if self.overlaps(mpos):
            pygame.draw.circle(screen, black, self.pos, self.big_rad)
        else:
            pygame.draw.circle(screen, black, self.pos, self.rad)
        winfont = pygame.font.SysFont('Comic Sans MS', 70)
        textsurface = winfont.render(str(nos), False, yellow)
        screen.blit(textsurface, (self.pos[0]+self.rad*0.4, self.pos[1]+self.rad*0.4))
        if self.selected:
            self.near_pos = (GRID_DIST*round(mpos[0]/GRID_DIST), GRID_DIST*round(mpos[1]/GRID_DIST))
            pygame.draw.circle(screen, black, self.near_pos, self.small_rad)
            bomb_ani = pygame.Surface(self.effect_area)
            bomb_ani.set_alpha(50)
            self.top_point = (self.near_pos[0]-round(self.effect_width/2), self.near_pos[1]-round(self.effect_height/2))
            # pygame.draw.rect(bomb_ani, grey, (top_point_x, top_point_y, self.effect_width, self.effect_height))
            screen.blit(bomb_ani, self.top_point)

    def overlaps(self, pos):
        x_axis = pos[0] > self.pos[0]-self.rad and pos[0] < self.pos[0]+self.rad
        y_axis = pos[1] > self.pos[1]-self.rad and pos[1] < self.pos[1]+self.rad
        return x_axis and y_axis
    
    def select(self):
        self.selected = True

class Shield:
    def __init__(self):
        self.pos = (70, 600)
        self.rad = 50
        self.big_rad = 55

    def draw(self, screen, mpos):
        if self.overlaps(mpos):
            pygame.draw.circle(screen, black, self.pos, self.big_rad)
        else:
            pygame.draw.circle(screen, black, self.pos, self.rad)

    def overlaps(self, pos):
        x_axis = pos[0] > self.pos[0]-self.rad and pos[0] < self.pos[0]+self.rad
        y_axis = pos[1] > self.pos[1]-self.rad and pos[1] < self.pos[1]+self.rad
        return x_axis and y_axis

def check_win(screen, player1, player2):
    global grid
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
        player1.reset()
        player2.reset()

def main():
    global player1
    global player2
    global grid

    pygame.init()

    quit = False
    clk_spd = 30

    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(SSIZE)

    grid = []
    for i in range(MARGIN, MARGIN+NOS):
        for j in range(MARGIN, MARGIN+NOS):
            grid.append(Dot(i*GRID_DIST, j*GRID_DIST))


    player1 = Player(0, red, lred)
    player2 = Player(1, blue, lblue)
    curr_player = player1

    while not quit:
        global change_player
        clock.tick(clk_spd)
        screen.fill(white)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    quit = True
                if event.key == pygame.K_ESCAPE:
                    if curr_player.bomb_selected: curr_player.deselect_bomb()
                    if curr_player.shield_selected: curr_player.deselect_shield()

            if event.type == pygame.MOUSEBUTTONDOWN:
                global change_player
                change_player = True
                if curr_player.bomb.overlaps(mouse_pos) and curr_player.bomb_selected:
                    curr_player.deselect_bomb()
                    change_player = False
                elif curr_player.shield.overlaps(mouse_pos) and curr_player.shield_selected:
                    curr_player.deselect_shield()
                    change_player = False
                elif curr_player.bomb_selected:
                    curr_player.use_bomb()
                    player1.got_bombed(curr_player.bomb.top_point, curr_player.bomb.effect_area)
                    player2.got_bombed(curr_player.bomb.top_point, curr_player.bomb.effect_area)
                elif curr_player.shield_selected:
                    curr_player.use_shield()
                elif curr_player.bomb.overlaps(mouse_pos) and curr_player.bombs and not curr_player.bomb_selected:
                    curr_player.select_bomb()
                    change_player = False
                elif curr_player.shield.overlaps(mouse_pos) and curr_player.shields:
                    curr_player.select_shield()
                    change_player = False
                elif light_line not in player1.lines and light_line not in player2.lines:
                    light_line.change_color(curr_player.color)
                    curr_player.lines.append(light_line)
                    last = Dot(pos=light_line.start)
                    second_last = Dot(pos=light_line.stop)
                    def check_point(all_lines):
                        global change_player
                        if all(map(lambda l: l in player1.lines or l in player2.lines, all_lines)):
                            curr_player.points.append(Box(curr_player.color, l1.start))
                            change_player = False
                            print("changed to false")

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
        player1.draw(screen, mouse_pos)
        player2.draw(screen, mouse_pos)

        check_win(screen, player1, player2)
        pygame.display.update()
            
    pygame.quit()

main()
