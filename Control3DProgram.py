from OpenGL.GL import *
from OpenGL.GLU import *
from math import *

import pygame
from pygame.locals import *

import sys
import time

from Shaders import *
from Base3DObjects import Vector
from Matrices import *


class CubeObj:
    def __init__(
        self,
        RGB: Vector,
        position: Vector,
        shader,
        model_matrix,
        gravity=False,
        collisions=False,
        scale=Vector(1, 1, 1),
        floor=False,
    ):
        self.RGB = RGB
        self.scale = scale
        self.position = position
        self.gravity = gravity
        self.collisions = collisions
        self.cube = Cube()
        self.model_matrix = model_matrix
        self.shader = shader
        self.floor = floor

    def draw(self):
        self.model_matrix.push_matrix()
        self.shader.set_material_diffuse(self.RGB.x, self.RGB.y, self.RGB.z)
        self.model_matrix.add_translation(
            self.position.x, self.position.y, self.position.z
        )
        self.model_matrix.add_scale(self.scale.x, self.scale.y, self.scale.z)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

    def get_vertices(self):
        """Returns the 8 corner vertices of the cube in world space."""
        # Base cube corners (before scaling/translation)
        base_corners = [
            (-0.5, -0.5, -0.5),  # 0: back-bottom-left
            (0.5, -0.5, -0.5),  # 1: back-bottom-right
            (0.5, 0.5, -0.5),  # 2: back-top-right
            (-0.5, 0.5, -0.5),  # 3: back-top-left
            (-0.5, -0.5, 0.5),  # 4: front-bottom-left
            (0.5, -0.5, 0.5),  # 5: front-bottom-right
            (0.5, 0.5, 0.5),  # 6: front-top-right
            (-0.5, 0.5, 0.5),  # 7: front-top-left
        ]

        # Apply scale and translation
        vertices = []
        for x, y, z in base_corners:
            world_x = x * self.scale.x + self.position.x
            world_y = y * self.scale.y + self.position.y
            world_z = z * self.scale.z + self.position.z
            vertices.append((world_x, world_y, world_z))

        return vertices


class GraphicsProgram3D:
    def __init__(self):

        pygame.init()
        pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("Free Walk Around Cube")

        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

        # Setup shader and matrices
        self.shader = Shader3D()
        self.shader.use()

        self.model_matrix = ModelMatrix()
        self.projection_view_matrix = ProjectionViewMatrix()
        self.map_view_matrix = ViewMatrix()
        self.player_view_matrix = ViewMatrix()
        self.main_view_matrix = self.player_view_matrix
        self.projection_matrix = ProjectionMatrix()
        self.minimap_projection_matrix = ProjectionMatrix()

        self.controlling_player = True

        # Camera setup
        self.player_view_matrix.eye = Point(0, 0, 5)
        self.player_view_matrix.look(Point(0, 0, 0))

        # Apply initial camera + projection
        self.shader.set_view_matrix(self.main_view_matrix.get_matrix())
        self.projection_matrix.set_perspective(90, 800 / 600, 0.5, 50)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        # Create shapes
        self.sphere = Sphere(8, 16)
        self.cube = Cube()

        # Time control
        self.my_clock = 0
        self.clock = pygame.time.Clock()
        self.clock.tick()
        self.touching_floor = True

        # Movement / rotation
        self.angle = 0
        self.move_speed = 10
        self.rotation_speed = 150
        self.objects = []

        self.UP_key_down = False
        self.white_background = False

        self.create_obj()

        self.player = self.main_view_matrix.eye
        self.player.y = 5

    def update(self):
        delta_time = self.clock.tick() / 1000.0
        self.my_clock += delta_time

        self.angle += pi * delta_time
        self.rot_step = self.rotation_speed * delta_time
        self.move_step = self.move_speed * delta_time

        self.handle_physics()

    def display(self):
        glEnable(GL_DEPTH_TEST)
        (
            glClearColor(1.0, 1.0, 1.0, 1.0)
            if self.white_background
            else glClearColor(0, 0, 0, 1)
        )
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, 800, 600)

        # Update camera and light
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())
        self.shader.set_view_matrix(self.main_view_matrix.get_matrix())
        self.shader.set_eye_position(self.main_view_matrix.eye)
        self.shader.set_light_position(self.main_view_matrix.eye)

        # Basic light settings
        self.shader.set_light_diffuse(0.5, 0.5, 0.5)
        self.shader.set_light_specular(0.4, 0.4, 0.4)
        self.shader.set_light_ambient(0.3, 0.3, 0.3)

        self.model_matrix.load_identity()
        self.draw_scene()

        pygame.display.flip()

    def handle_physics(self):
        delta_time = self.clock.get_time() / 1000.0
        player_radius = 1
        gravity = -10
        found_floor = False
        for object in self.objects:
            min_y = inf
            min_x = inf
            min_z = inf

            max_y = -inf
            max_x = -inf
            max_z = -inf
            for vertice in object.get_vertices():
                min_x = min(min_x, vertice[0])
                min_y = min(min_y, vertice[1])
                min_z = min(min_z, vertice[2])

                max_x = max(max_x, vertice[0])
                max_y = max(max_y, vertice[1])
                max_z = max(max_z, vertice[2])

            if (
                min_x - player_radius <= self.player.x <= max_x + player_radius
                and min_y - player_radius <= self.player.y <= max_y + player_radius
                and min_z - player_radius <= self.player.z <= max_z + player_radius
            ):
                overlap_x = min(abs(self.player.x - min_x), abs(self.player.x - max_x))
                overlap_y = min(abs(self.player.y - min_y), abs(self.player.y - max_y))
                overlap_z = min(abs(self.player.z - min_z), abs(self.player.z - max_z))
                if overlap_x < overlap_y and overlap_x < overlap_z:
                    # Push along X axis
                    if self.player.x < (min_x + max_x) / 2:
                        self.player.x = min_x - player_radius
                    else:
                        self.player.x = max_x + player_radius

                elif overlap_y < overlap_x and overlap_y < overlap_z:
                    # Push along Y axis
                    if self.player.y < (min_y + max_y) / 2:
                        self.player.y = min_y - player_radius
                    else:
                        self.player.y = max_y + player_radius
                    if object.floor == True:
                        found_floor = True

                else:
                    # Push along Z axis
                    if self.player.z < (min_z + max_z) / 2:
                        self.player.z = min_z - player_radius
                    else:
                        self.player.z = max_z + player_radius
        if found_floor:
            self.touching_floor = True
        else:
            self.touching_floor = False
        if self.touching_floor == False:
            self.player.y += gravity * delta_time

    def draw_scene(self):
        for object in self.objects:
            object.draw()

    def create_obj(self, map=False):
        """Draw the scene using CubeObj for every cube instead of manual draw calls."""

        # Red cube
        new_cube = CubeObj(
            Vector(1, 0, 0),
            Vector(0, -1, 0),
            self.shader,
            self.model_matrix,
            scale=Vector(3, 2, 3),
            floor=True,
        )
        self.objects.append(new_cube)

        # Ground
        ground = CubeObj(
            Vector(0.4, 0.4, 0.4),
            Vector(0, -2, 0),
            self.shader,
            self.model_matrix,
            scale=Vector(20, 0.5, 20),
            floor=True,
        )
        self.objects.append(ground)

        # Ceiling
        ceiling = CubeObj(
            Vector(0.4, 0.4, 0.4),
            Vector(0, 8, 0),
            self.shader,
            self.model_matrix,
            scale=Vector(20, 0.5, 20),
        )
        self.objects.append(ceiling)

        # Right wall
        right_wall = CubeObj(
            Vector(0.4, 0.4, 0.4),
            Vector(10 - 0.5, 3, 0),
            self.shader,
            self.model_matrix,
            scale=Vector(0.5, 10, 20),
        )
        self.objects.append(right_wall)

        # Left wall
        left_wall = CubeObj(
            Vector(0.4, 0.4, 0.4),
            Vector(-10 + 0.5, 3, 0),
            self.shader,
            self.model_matrix,
            scale=Vector(0.5, 10, 20),
        )
        self.objects.append(left_wall)

        # Back wall
        back_wall = CubeObj(
            Vector(0.4, 0.4, 0.4),
            Vector(0, 3, 10),
            self.shader,
            self.model_matrix,
            scale=Vector(20, 10, 0.5),
        )
        self.objects.append(back_wall)

        # Front wall
        front_wall = CubeObj(
            Vector(0.4, 0.4, 0.4),
            Vector(0, 3, -10),
            self.shader,
            self.model_matrix,
            scale=Vector(20, 10, 0.5),
        )
        self.objects.append(front_wall)

    def program_loop(self):
        exiting = False
        delta_time = self.clock.get_time() / 1000.0
        while not exiting:
            keys = pygame.key.get_pressed()

            # CAMERA CONTROLS
            if keys[pygame.K_UP]:
                self.main_view_matrix.pitch(-self.rot_step)
            if keys[pygame.K_DOWN]:
                self.main_view_matrix.pitch(self.rot_step)
            if keys[pygame.K_LEFT]:
                self.main_view_matrix.rotate_horizontal(self.rot_step)
            if keys[pygame.K_RIGHT]:
                self.main_view_matrix.rotate_horizontal(-self.rot_step)

            if keys[pygame.K_w]:
                self.main_view_matrix.walk(0, 0, -self.move_step)
            if keys[pygame.K_s]:
                self.main_view_matrix.walk(0, 0, self.move_step)
            if keys[pygame.K_a]:
                self.main_view_matrix.walk(-self.move_step, 0, 0)
            if keys[pygame.K_d]:
                self.main_view_matrix.walk(self.move_step, 0, 0)

            # EVENT HANDLING
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting!")
                    exiting = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        print("Escaping!")
                        exiting = True
                    if event.key == K_v:
                        # Toggle between top-down map view and player view
                        if self.controlling_player:
                            self.main_view_matrix = self.map_view_matrix
                            self.controlling_player = False
                        else:
                            self.main_view_matrix = self.player_view_matrix
                            self.controlling_player = True
                        self.shader.set_view_matrix(self.main_view_matrix.get_matrix())
                    if event.key == K_SPACE and self.touching_floor:
                        self.player.y += 5

            self.update()
            self.display()

        pygame.quit()

    def start(self):
        self.program_loop()


if __name__ == "__main__":
    GraphicsProgram3D().start()
