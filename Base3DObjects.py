import random
from random import *

from OpenGL.GL import *
from OpenGL.GLU import *

import numpy

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

    def copy(self):
        return Vector(self.x, self.y, self.z)

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"


class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b


class Material:
    def __init__(self, diffuse=None, specular=None, shininess=None):
        self.diffuse = Color(0.0, 0.0, 0.0) if diffuse == None else diffuse
        self.specular = Color(0.0, 0.0, 0.0) if specular == None else specular
        self.shininess = 1 if shininess == None else shininess


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

        self.uv_array = [
            0.0,
            0.0,
            0.0,
            1.0,
            1.0,
            1.0,
            1.0,
            0.0,
            1.0,
            0.0,
            1.0,
            1.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            1.0,
            1.0,
            1.0,
            0.0,
            1.0,
            1.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            1.0,
            1.0,
            0.0,
            1.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            1.0,
            1.0,
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
        shader.set_uv_attribute(self.uv_array)

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


class MeshModel:
    def __init__(self):
        self.vertex_arrays = dict()
        # self.index_arrays = dict()
        self.mesh_materials = dict()
        self.materials = dict()
        self.vertex_counts = dict()
        self.vertex_buffer_ids = dict()

    def add_vertex(self, mesh_id, position, normal, uv=None):
        if mesh_id not in self.vertex_arrays:
            self.vertex_arrays[mesh_id] = []
            self.vertex_counts[mesh_id] = 0
        self.vertex_arrays[mesh_id] += [
            position.x,
            position.y,
            position.z,
            normal.x,
            normal.y,
            normal.z,
        ]

        if uv is not None:
            self.vertex_arrays[mesh_id] += [uv[0], uv[1]]
        else:
            self.vertex_arrays[mesh_id] += [0.0, 0.0]

        self.vertex_counts[mesh_id] += 1

    def set_mesh_material(self, mesh_id, mat_id):
        self.mesh_materials[mesh_id] = mat_id

    def add_material(self, mat_id, mat):
        self.materials[mat_id] = mat

    def set_opengl_buffers(self):
        for mesh_id in self.mesh_materials.keys():
            self.vertex_buffer_ids[mesh_id] = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_ids[mesh_id])
            glBufferData(
                GL_ARRAY_BUFFER,
                numpy.array(self.vertex_arrays[mesh_id], dtype="float32"),
                GL_STATIC_DRAW,
            )
            glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, shader):
        shader.set_use_texture(False)
        for mesh_id, mesh_material in self.mesh_materials.items():
            material = self.materials[mesh_material]
            shader.set_material_diffuse(
                material.diffuse.r, material.diffuse.g, material.diffuse.b
            )
            shader.set_material_specular(
                material.specular.r, material.specular.g, material.specular.b
            )
            shader.set_material_shininess(material.shininess)
            shader.set_attribute_buffers(self.vertex_buffer_ids[mesh_id])
            glDrawArrays(GL_TRIANGLES, 0, self.vertex_counts[mesh_id])
            glBindBuffer(GL_ARRAY_BUFFER, 0)


class TriForce:
    def __init__(self, thickness=0.5):
        self.thickness = thickness
        front_z = thickness / 2
        back_z = -thickness / 2

        # Vertices for front triangle (z = +thickness/2)
        front_top = [0.0, 1.0, front_z]
        front_left = [-1.0, -1.0, front_z]
        front_right = [1.0, -1.0, front_z]

        # Vertices for back triangle (z = -thickness/2)
        back_top = [0.0, 1.0, back_z]
        back_left = [-1.0, -1.0, back_z]
        back_right = [1.0, -1.0, back_z]

        # For same-sized triangle:
        front_top2 = [1.0, -1.0, front_z]  # Bottom right corner of first triangle
        front_left2 = [0.0, -3.0, front_z]  # Go down 2 more units (not 1)
        front_right2 = [2.0, -3.0, front_z]  # Go down 2 more units

        back_top2 = [1.0, -1.0, back_z]
        back_left2 = [0.0, -3.0, back_z]
        back_right2 = [2.0, -3.0, back_z]

        front_top3 = [-1.0, -1.0, front_z]  # Bottom left corner of first triangle
        front_left3 = [-2.0, -3.0, front_z]  # Go left and down
        front_right3 = [0.0, -3.0, front_z]  # Meet the right triangle at center

        back_top3 = [-1.0, -1.0, back_z]
        back_left3 = [-2.0, -3.0, back_z]
        back_right3 = [0.0, -3.0, back_z]

        # Simple normals - just point out from each face
        front_normal = [0, 0, 1]  # Forward
        back_normal = [0, 0, -1]  # Backward
        right_normal = [1, 0, 0]  # Right
        left_normal = [-1, 0, 0]  # Left
        up_normal = [0, 1, 0]  # Up
        down_normal = [0, -1, 0]  # Down

        self.normal_array = [
            # First prism - front triangle (6 vertices)
            *front_normal,
            *front_normal,
            *front_normal,
            # First prism - back triangle (6 vertices)
            *back_normal,
            *back_normal,
            *back_normal,
            # First prism - side 1 (6 vertices)
            *left_normal,
            *left_normal,
            *left_normal,
            *left_normal,
            *left_normal,
            *left_normal,
            # First prism - side 2 (6 vertices)
            *down_normal,
            *down_normal,
            *down_normal,
            *down_normal,
            *down_normal,
            *down_normal,
            # First prism - side 3 (6 vertices)
            *right_normal,
            *right_normal,
            *right_normal,
            *right_normal,
            *right_normal,
            *right_normal,
            # Second prism - front triangle (6 vertices)
            *front_normal,
            *front_normal,
            *front_normal,
            # Second prism - back triangle (6 vertices)
            *back_normal,
            *back_normal,
            *back_normal,
            # Second prism - side 1 (6 vertices)
            *left_normal,
            *left_normal,
            *left_normal,
            *left_normal,
            *left_normal,
            *left_normal,
            # Second prism - side 2 (6 vertices)
            *down_normal,
            *down_normal,
            *down_normal,
            *down_normal,
            *down_normal,
            *down_normal,
            # Second prism - side 3 (6 vertices)
            *right_normal,
            *right_normal,
            *right_normal,
            *right_normal,
            *right_normal,
            *right_normal,
            # Third prism - front triangle (6 vertices)
            *front_normal,
            *front_normal,
            *front_normal,
            # Third prism - back triangle (6 vertices)
            *back_normal,
            *back_normal,
            *back_normal,
            # Third prism - side 1 (6 vertices)
            *left_normal,
            *left_normal,
            *left_normal,
            *left_normal,
            *left_normal,
            *left_normal,
            # Third prism - side 2 (6 vertices)
            *down_normal,
            *down_normal,
            *down_normal,
            *down_normal,
            *down_normal,
            *down_normal,
            # Third prism - side 3 (6 vertices)
            *right_normal,
            *right_normal,
            *right_normal,
            *right_normal,
            *right_normal,
            *right_normal,
        ]

        self.position_array = [
            # Front triangle
            *front_top,
            *front_left,
            *front_right,
            # Back triangle (reverse winding for correct face culling)
            *back_right,
            *back_left,
            *back_top,
            # Side 1: Top-Left edge (front_top - front_left to back_top - back_left)
            *front_top,
            *front_left,
            *back_left,
            *back_left,
            *back_top,
            *front_top,
            # Side 2: Left-Right edge (front_left - front_right to back_left - back_right)
            *front_left,
            *front_right,
            *back_right,
            *back_right,
            *back_left,
            *front_left,
            # Side 3: Right-Top edge (front_right - front_top to back_right - back_top)
            *front_right,
            *front_top,
            *back_top,
            *back_top,
            *back_right,
            *front_right,
            # Front triangle
            *front_top2,
            *front_left2,
            *front_right2,
            # Back triangle (reverse winding for correct face culling)
            *back_right2,
            *back_left2,
            *back_top2,
            # Side 1: Top-Left edge (front_top - front_left to back_top - back_left)
            *front_top2,
            *front_left2,
            *back_left2,
            *back_left2,
            *back_top2,
            *front_top2,
            # Side 2: Left-Right edge (front_left - front_right to back_left - back_right)
            *front_left2,
            *front_right2,
            *back_right2,
            *back_right2,
            *back_left2,
            *front_left2,
            # Side 3: Right-Top edge (front_right - front_top to back_right - back_top)
            *front_right2,
            *front_top2,
            *back_top2,
            *back_top2,
            *back_right2,
            *front_right2,
            *front_top3,
            *front_left3,
            *front_right3,
            # Back triangle (reverse winding for correct face culling)
            *back_right3,
            *back_left3,
            *back_top3,
            # Side 1: Top-Left edge (front_top - front_left to back_top - back_left)
            *front_top3,
            *front_left3,
            *back_left3,
            *back_left3,
            *back_top3,
            *front_top3,
            # Side 2: Left-Right edge (front_left - front_right to back_left - back_right)
            *front_left3,
            *front_right3,
            *back_right3,
            *back_right3,
            *back_left3,
            *front_left3,
            # Side 3: Right-Top edge (front_right - front_top to back_right - back_top)
            *front_right3,
            *front_top3,
            *back_top3,
            *back_top3,
            *back_right3,
            *front_right3,
        ]

    def set_vertices(self, shader):
        shader.set_position_attribute(self.position_array)
        shader.set_normal_attribute(self.normal_array)

    def draw(self, shader):
        glDrawArrays(GL_TRIANGLES, 0, len(self.position_array) // 3)
