from OpenGL.GL import *
from OpenGL.GLU import *
from math import *

import pygame
from pygame.locals import *

import sys
import time

from Shaders import *
from Matrices import *


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

        # Movement / rotation
        self.angle = 0
        self.move_speed = 10
        self.rotation_speed = 150

        self.UP_key_down = False
        self.white_background = False

    def update(self):
        delta_time = self.clock.tick() / 1000.0
        self.my_clock += delta_time

        self.angle += pi * delta_time
        self.rot_step = self.rotation_speed * delta_time
        self.move_step = self.move_speed * delta_time

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

    def draw_scene(self, map=False):
        """Draw a static cube in the world. The camera moves freely around it."""
        self.model_matrix.push_matrix()
        self.shader.set_material_diffuse(1, 0, 0)
        self.model_matrix.add_translation(0, -1.2, 0)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.model_matrix.push_matrix()
        self.shader.set_material_diffuse(0.4, 0.4, 0.4)
        self.model_matrix.add_translation(0, -2, 0)
        self.model_matrix.add_scale(20, 0.5, 20)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.model_matrix.push_matrix()
        self.shader.set_material_diffuse(0.4, 0.4, 0.4)
        self.model_matrix.add_translation(0, 8, 0)
        self.model_matrix.add_scale(20, 0.5, 20)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.model_matrix.push_matrix()
        self.shader.set_material_diffuse(0.4, 0.4, 0.4)
        self.model_matrix.add_translation(10 - 0.5, 3, 0)
        self.model_matrix.add_scale(0.5, 10, 20)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.model_matrix.push_matrix()
        self.shader.set_material_diffuse(0.4, 0.4, 0.4)
        self.model_matrix.add_translation(-10 + 0.5, 3, 0)
        self.model_matrix.add_scale(0.5, 10, 20)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.model_matrix.push_matrix()
        self.shader.set_material_diffuse(0.4, 0.4, 0.4)
        self.model_matrix.add_translation(0, 3, 10)
        self.model_matrix.add_scale(20, 10, 0.5)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        self.model_matrix.push_matrix()
        self.shader.set_material_diffuse(0.4, 0.4, 0.4)
        self.model_matrix.add_translation(0, 3, -10)
        self.model_matrix.add_scale(20, 10, 0.5)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

    def program_loop(self):
        exiting = False
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

            self.update()
            self.display()

        pygame.quit()

    def start(self):
        self.program_loop()


if __name__ == "__main__":
    GraphicsProgram3D().start()
