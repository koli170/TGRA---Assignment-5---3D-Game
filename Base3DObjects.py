import random
from random import *

from OpenGL.GL import *
from OpenGL.GLU import *

import math
from math import *


class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)


class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def __len__(self):
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self):
        length = self.__len__()
        self.x /= length
        self.y /= length
        self.z /= length

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )


class Cube:
    def __init__(self):
        self.position_array = [
            -0.5,
            -0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            -0.5,
            0.5,
            -0.5,
            -0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            -0.5,
            0.5,
            -0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            -0.5,
            -0.5,
            -0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            -0.5,
        ]
        self.normal_array = [
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
        ]

    def scale(self, x, y, z):
        self.position_array = [
            -0.5,
            -0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            -0.5,
            0.5,
            -0.5,
            -0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            -0.5,
            0.5,
            -0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            -0.5,
            -0.5,
            -0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            -0.5,
            -0.5,
            0.5,
            -0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            0.5,
            -0.5,
        ]
        for i in range(0, len(self.position_array), 3):
            self.position_array[i] *= x
            self.position_array[i + 1] *= y
            self.position_array[i + 2] *= z

    def draw(self, shader):

        shader.set_position_attribute(self.position_array)
        shader.set_normal_attribute(self.normal_array)

        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 4, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 8, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 12, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 16, 4)
        glDrawArrays(GL_TRIANGLE_FAN, 20, 4)


class Sphere:
    def __init__(self, stacks=12, slices=24):
        self.vertex_array = []
        self.slices = slices
        stack_interval = pi / stacks
        slice_interval = 2 * pi / slices
        self.vertex_count = 0

        for stack_count in range(stacks):
            stack_angle = stack_count * stack_interval
            for slice_count in range(slices + 1):
                slice_angle = slice_count * slice_interval
                self.vertex_array.append(sin(stack_angle) * cos(slice_angle))
                self.vertex_array.append(cos(stack_angle))
                self.vertex_array.append(sin(stack_angle) * sin(slice_angle))

                self.vertex_array.append(
                    sin(stack_angle + stack_interval) * cos(slice_angle)
                )
                self.vertex_array.append(cos(stack_angle + stack_interval))
                self.vertex_array.append(
                    sin(stack_angle + stack_interval) * sin(slice_angle)
                )

                self.vertex_count += 2

    def set_vertices(self, shader):
        shader.set_position_attribute(self.vertex_array)
        shader.set_normal_attribute(self.vertex_array)

    def draw(self, shader):
        self.set_vertices(shader)
        verts_per_strip = (self.slices + 1) * 2
        for i in range(0, self.vertex_count, verts_per_strip):
            glDrawArrays(GL_TRIANGLE_STRIP, i, verts_per_strip)


from math import sin, cos, pi
from OpenGL.GL import *


from math import pi, sin, cos, sqrt
from OpenGL.GL import *


class Emerald:
    def __init__(self, stacks=4, slices=8, height=1.0, radius=0.5):
        self.vertex_array = []
        self.vertex_count = 0
        self.slices = slices

        for stack in range(stacks):
            y0 = height / 2 - (stack * height / stacks)
            y1 = height / 2 - ((stack + 1) * height / stacks)

            r0 = radius * (1 - abs(y0) / (height / 2))
            r1 = radius * (1 - abs(y1) / (height / 2))

            for slice in range(slices + 1):
                theta = slice * 2 * pi / slices
                x0 = r0 * cos(theta)
                z0 = r0 * sin(theta)
                x1 = r1 * cos(theta)
                z1 = r1 * sin(theta)

                if stack == 0:
                    y0 = height / stacks
                self.vertex_array.extend([x0, y0, z0])
                self.vertex_array.extend([x1, y1, z1])
                self.vertex_count += 2

    def set_vertices(self, shader):
        shader.set_position_attribute(self.vertex_array)
        shader.set_normal_attribute(self.vertex_array)

    def draw(self, shader):
        self.set_vertices(shader)
        verts_per_strip = (self.slices + 1) * 2
        for i in range(0, self.vertex_count, verts_per_strip):
            glDrawArrays(GL_TRIANGLE_STRIP, i, verts_per_strip)


class MazeCell:
    def __init__(self, north_wall: bool, east_wall: bool, scale=5.0):
        self.has_north_wall = north_wall
        self.has_east_wall = east_wall
        self.scale = scale

        self.north_wall = Cube()
        self.north_wall.scale(self.scale, self.scale, 0.4)

        self.east_wall = Cube()
        self.east_wall.scale(0.4, self.scale, self.scale)

        self.cover = Cube()
        self.cover.scale(self.scale, 0.1, self.scale)


class Maze:
    def __init__(self, rows=2, cols=2, scale=5):
        self.rows = rows
        self.cols = cols
        self.scale = scale

        self.floor = Cube()
        self.floor.scale(rows * scale, 0.2, cols * scale)

        self.marked_cells = [
            [False for _ in range(self.cols + 1)] for _ in range(self.rows + 1)
        ]

        self.generate()

    def mark_cell(self, x, y):
        if not self.marked_cells[x][y]:
            self.marked_cells[x][y] = True
            self.blueprint[x][y].north_wall.scale(5, 5.5, 0.4)
            self.blueprint[x][y].east_wall.scale(0.4, 5.5, 5)
            self.blueprint[x][y - 1].north_wall.scale(5, 5.5, 0.4)
            self.blueprint[x - 1][y].east_wall.scale(0.4, 5.5, 5)

    def valid_gen_steps(self, current, steps):
        row, col = current
        for step in steps:
            if step == 1:
                check_row, check_col = row + 1, col
            elif step == 2:
                check_row, check_col = row, col - 1
            elif step == 3:
                check_row, check_col = row - 1, col
            elif step == 4:
                check_row, check_col = row, col + 1
            if 1 <= check_row <= self.rows and 1 <= check_col <= self.cols:
                if not self.visited[check_row][check_col]:
                    return step
        return -1

    def reset_marked(self):
        self.marked_cells = [
            [False for _ in range(self.cols + 1)] for _ in range(self.rows + 1)
        ]
        for row in range(len(self.blueprint)):
            for col in range(len(self.blueprint[row])):
                if row == 0:
                    self.marked_cells[row][col] = True
                if col == 0:
                    self.marked_cells[row][col] = True

    def generate(self, rows=-1, cols=-1):
        if rows != -1:
            self.rows = rows
        if cols != -1:
            self.cols = cols

        self.marked_cells = [
            [False for _ in range(self.cols + 1)] for _ in range(self.rows + 1)
        ]

        self.blueprint = [
            [MazeCell(True, True) for _ in range(self.cols + 1)]
            for _ in range(self.rows + 1)
        ]

        self.start = [randint(1, self.rows), randint(1, self.cols)]
        self.end = [randint(1, self.rows), randint(1, self.cols)]
        while self.end == self.start:
            self.end = [randint(1, self.rows), randint(1, self.cols)]

        self.visited = [
            [False for _ in range(self.cols + 1)] for _ in range(self.rows + 1)
        ]
        tile_stack = [list(self.start)]
        self.visited[self.start[0]][self.start[1]] = True

        # REMOVE OUTSIDE EXTRA WALLS
        for row in range(len(self.blueprint)):
            for col in range(len(self.blueprint[row])):
                if row == 0:
                    self.marked_cells[row][col] = True
                    self.blueprint[row][col].has_north_wall = False
                    self.blueprint[row][col].east_wall.scale(0.4, 5.5, 5)
                if col == 0:
                    self.marked_cells[row][col] = True
                    self.blueprint[row][col].has_east_wall = False
                    self.blueprint[row][col].north_wall.scale(5, 5.5, 0.4)

        while tile_stack:
            current = tile_stack[-1]
            steps = [1, 2, 3, 4]
            shuffle(steps)
            step = self.valid_gen_steps(current, steps)

            if step == -1 or current == list(self.end):
                tile_stack.pop()
                continue

            row, col = current
            if step == 1:
                self.blueprint[row][col].has_east_wall = False
                next_cell = [row + 1, col]
            elif step == 2:
                self.blueprint[row][col - 1].has_north_wall = False
                next_cell = [row, col - 1]
            elif step == 3:
                self.blueprint[row - 1][col].has_east_wall = False
                next_cell = [row - 1, col]
            elif step == 4:
                self.blueprint[row][col].has_north_wall = False
                next_cell = [row, col + 1]

            tile_stack.append(next_cell)
            self.visited[next_cell[0]][next_cell[1]] = True
