# A* Pathfinding algorithm in python...

# --------------------------------------------------------external libraries----------------------------------------------------------#

import pygame
from pygame.display import flip
from pygame.draw import line, rect
from pygame.mouse import get_pos
from pygame.mouse import get_pressed as mouse_pressed
import math
from queue import PriorityQueue
import numpy
import sys

# ----------------------------------------------------------global variables----------------------------------------------------------#

width = 720
height = 440
rez = 40

display = pygame.display.set_mode((width, height))
pygame.display.set_caption('A* Pathfinding')

# -------------------------------------------------------------class Grid------------------------------------------------------------#


class Grid(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.board = []
        for i in range(self.x):
            self.board.append([])
            for j in range(self.y):
                self.board[i].append(Block(i, j))

    def draw(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                self.board[i][j].draw()
# -------------------------------------------------------------class Block------------------------------------------------------------#


class Block(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pos = self.x, self.y
        self.path = False
        self.block = False
        self.start = False
        self.end = False
        self.open = False
        self.close = False
        self.rows = height // rez
        self.cols = width // rez
        self.neighbors = []

    def draw(self):
        if self.open:
            rect(display, (90, 250, 90), (self.x * rez, self.y * rez, rez, rez))

        elif self.close:
            rect(display, (128, 90, 128), (self.x * rez, self.y * rez, rez, rez))

        elif self.path:
            rect(display, (169, 169, 169), (self.x * rez, self.y * rez, rez, rez))

        elif self.start:
            rect(display, (90, 90, 250), (self.x * rez, self.y * rez, rez, rez))

        elif self.end:
            rect(display, (250, 90, 90), (self.x * rez, self.y * rez, rez, rez))

        elif self.block:
            rect(display, (51, 51, 51), (self.x * rez, self.y * rez, rez, rez))

        else:
            rect(display, (220, 220, 220), (self.x * rez, self.y * rez, rez, rez))

    def make_block(self):
        # self.path = not self.path
        self.block = True
        self.path = False

    def make_start(self):
        self.start = True
        self.end = False
        self.path = False

    def make_end(self):
        self.end = True
        self.start = False
        self.path = False

    def make_path(self):
        self.path = True
        self.close = False

    def make_open(self):
        self.open = True

    def make_close(self):
        self.close = True
        self.open = False

    def update_neighbours(self, grid):
        # down block
        if self.x < self.cols - 1 and not grid.board[self.x + 1][self.y].block:
            self.neighbors.append(grid.board[self.x + 1][self.y])

        # up block
        if self.x > 0 and not grid.board[self.x - 1][self.y].block:
            self.neighbors.append(grid.board[self.x - 1][self.y])

        # right block
        if self.y < self.rows - 1 and not grid.board[self.x][self.y + 1].block:
            self.neighbors.append(grid.board[self.x][self.y + 1])

        # left block
        if self.y > 0 and not grid.board[self.x][self.y - 1].block:
            self.neighbors.append(grid.board[self.x][self.y - 1])

# ---------------------------------------------------------------function path----------------------------------------------------------#


def reconstruct_path(pathlist, current, draw):
    while current in pathlist:
        current = pathlist[current]
        current.make_path()
        draw()

# -------------------------------------------------------------function drawgrid--------------------------------------------------------#


def drawgrid():
    for i in range(rez, width, rez):
        for j in range(rez, height, rez):
            line(display, (0, 0, 0), (i, 0), (i, height))
            line(display, (0, 0, 0), (0, j), (width, j))

# ----------------------------------------------------------------heuristic------------------------------------------------------------#


def heuristic(start, end):
    x1, y1 = start.pos
    x2, y2 = end.pos
    return abs(x1 - x2) + abs(y1 - y2)

# --------------------------------------------------------------A* algorithm-----------------------------------------------------------#


def a_star(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {block: float("inf")
               for rows in grid.board for block in rows}
    g_score[start] = 0
    f_score = {block: float("inf")
               for rows in grid.board for block in rows}
    f_score[start] = heuristic(start, end)

    closed_set = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        closed_set.remove(current)

        if current.pos == end.pos:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            exit
            break

        for neighbor in current.neighbors:
            temp_g = g_score[current] + 1

            if temp_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g
                f_score[neighbor] = g_score[neighbor] + \
                    heuristic(neighbor, end)
                if neighbor not in closed_set:
                    count += 1
                    open_set.put(
                        (f_score[neighbor], count, neighbor))
                    closed_set.add(neighbor)
                    neighbor.make_open()

            draw()

        if current != start:
            current.make_close()

# --------------------------------------------------------------function draw-----------------------------------------------------------#


def draw(grid):
    display.fill((220, 220, 220))

    for rows in grid.board:
        for block in rows:
            block.draw()

    grid.draw()
    drawgrid()
    flip()

# --------------------------------------------------------------function main-----------------------------------------------------------#


def main():
    # global grid
    run = True
    grid = Grid(width // rez, height // rez)
    start_node = None
    end_node = None

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                # sys.exit()

            if mouse_pressed()[0]:
                x, y = get_pos()
                grid_pos = grid.board[x // rez][y // rez]
                if not start_node and not grid_pos.end:
                    grid_pos.make_start()
                    start_node = grid_pos
                elif not end_node and not grid_pos.start:
                    grid_pos.make_end()
                    end_node = grid_pos
                else:
                    grid_pos.make_block()

            elif mouse_pressed()[2]:
                x, y = get_pos()
                grid_pos = grid.board[x // rez][y // rez]

                if grid_pos.pos == start_node.pos:
                    start_node = None
                    grid_pos.make_path()
                elif grid_pos.pos == end_node.pos:
                    end_node = None
                    grid_pos.make_path()
                else:
                    grid_pos.make_path()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    for rows in grid.board:
                        for block in rows:
                            block.update_neighbours(grid)

                    a_star(lambda: draw(grid), grid, start_node, end_node)

        draw(grid)

# -------------------------------------------------------------------------------------------------------------------------#


if __name__ == "__main__":
    main()

# -------------------------------------------------------------------------------------------------------------------------#
