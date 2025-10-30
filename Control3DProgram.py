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

        self.shader.set_view_matrix(self.main_view_matrix.get_matrix())
        self.projection_matrix.set_perspective(90, 800 / 600, 0.5, 50)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        self.sphere = Sphere(8, 16)
        self.cube = Cube()
        self.emerald = Emerald(height=2, radius=1)
        self.emerald_rotation = 0
        self.emerald_height = 2
        self.emerald_exists = True
        self.emerald_clock = -1
        self.emerald_counter = 0
        self.my_clock = 0

        self.MAZE_SCALE = 5.0
        self.maze = Maze(8, 8, self.MAZE_SCALE)

        size = self.MAZE_SCALE * max(self.maze.rows, self.maze.cols) / 1.5
        self.minimap_projection_matrix.set_orthographic(
            -size, size, -size, size, 0.5, 70
        )

        self.player_view_matrix.eye = Point(
            self.maze.start[0] * self.MAZE_SCALE - self.MAZE_SCALE / 2,
            3,
            self.maze.start[1] * self.MAZE_SCALE - self.MAZE_SCALE / 2,
        )
        self.old_location = self.player_view_matrix.eye
        self.map_view_matrix.eye = Point(
            self.MAZE_SCALE * self.maze.rows / 2,
            28,
            self.MAZE_SCALE * self.maze.cols / 2,
        )
        self.map_view_matrix.look_down()

        self.clock = pygame.time.Clock()
        self.clock.tick()

        self.angle = 0
        self.move_speed = 10
        self.rotation_speed = 150
        self.fade_out_value = 1
        self.fading = False

        self.UP_key_down = (
            False  ## --- ADD CONTROLS FOR OTHER KEYS TO CONTROL THE CAMERA --- ##
        )

        self.white_background = False

    def update(self):
        delta_time = self.clock.tick() / 1000.0
        self.my_clock += delta_time

        self.angle += pi * delta_time
        self.rot_step = self.rotation_speed * delta_time
        self.move_step = self.move_speed * delta_time

        old_player_location_grid = [
            int(self.old_location.x / self.MAZE_SCALE) + 1,
            int(self.old_location.z / self.MAZE_SCALE) + 1,
        ]

        end_x = self.maze.end[0] * self.MAZE_SCALE - self.MAZE_SCALE / 2
        end_z = self.maze.end[1] * self.MAZE_SCALE - self.MAZE_SCALE / 2

        # EMERALD COLLISION
        if (
            self.emerald_exists
            and (end_x - 1.5 < self.player_view_matrix.eye.x < end_x + 1.5)
            and (end_z - 1.5 < self.player_view_matrix.eye.z < end_z + 1.5)
        ):
            self.player_view_matrix.eye.x = self.old_location.x
            self.player_view_matrix.eye.z = self.old_location.z
            if self.emerald_clock < 0:
                self.emerald_clock = 0

        if self.emerald_clock >= 0:
            self.emerald_clock += delta_time
            if self.emerald_clock > 0.1:
                self.emerald_exists = False
                self.fading = True

        if self.fading:
            self.fade_out_value = max(0, self.fade_out_value - delta_time)

        if not self.fading and self.fade_out_value < 1:
            self.fade_out_value = min(1, self.fade_out_value + delta_time)

        if self.fade_out_value is 0:
            self.maze.generate()
            self.player_view_matrix.eye.x = (
                self.maze.start[0] * self.MAZE_SCALE - self.MAZE_SCALE / 2
            )
            self.player_view_matrix.eye.z = (
                self.maze.start[1] * self.MAZE_SCALE - self.MAZE_SCALE / 2
            )
            old_player_location_grid = [
                int(self.player_view_matrix.eye.x / self.MAZE_SCALE) + 1,
                int(self.player_view_matrix.eye.z / self.MAZE_SCALE) + 1,
            ]
            self.maze.reset_marked()
            self.emerald_clock = -1
            self.emerald_exists = True
            self.emerald_counter += 1
            print("YOU HAVE " + str(self.emerald_counter) + " EMERALD/S")
            self.fading = False

        self.emerald_rotation = (self.emerald_rotation + 1 * delta_time) % 360
        self.emerald_height = cos(self.my_clock) / 2 + 2
        self.emerald_color = [
            0.5 + 0.5 * math.sin(self.my_clock),
            0.5 + 0.5 * math.sin(self.my_clock + 2 * math.pi / 3),
            0.5 + 0.5 * math.sin(self.my_clock + 4 * math.pi / 3),
        ]

        self.maze.mark_cell(old_player_location_grid[0], old_player_location_grid[1])
        self.grand_ol_collision()

    def display(self):
        glEnable(
            GL_DEPTH_TEST
        )  ### --- NEED THIS FOR NORMAL 3D BUT MANY EFFECTS BETTER WITH glDisable(GL_DEPTH_TEST) ... try it! --- ###
        # glDisable(GL_CULL_FACE)
        # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        if self.white_background:
            glClearColor(1.0, 1.0, 1.0, 1.0)
        else:
            glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(
            GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT
        )  ### --- YOU CAN ALSO CLEAR ONLY THE COLOR OR ONLY THE DEPTH --- ###

        glViewport(0, 0, 800, 600)

        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())
        self.shader.set_view_matrix(self.main_view_matrix.get_matrix())

        self.projection_matrix.set_perspective(90, 800 / 600, 0.5, 20)
        self.shader.set_eye_position(self.main_view_matrix.eye)

        self.shader.set_light_position(self.main_view_matrix.eye)
        flicker = 0.85 + 0.35 * sin(self.my_clock * 1.5)
        flicker *= self.fade_out_value
        self.shader.set_light_diffuse(1.0 * flicker, 0.7 * flicker, 0.3 * flicker)
        self.shader.set_light_specular(1.0 * flicker, 0.7 * flicker, 0.3 * flicker)
        self.shader.set_light_ambient(1.0 * flicker, 0.7 * flicker, 0.3 * flicker)

        self.shader.set_light_position_2(self.main_view_matrix.eye)
        self.shader.set_light_ambient_2(
            self.emerald_color[0] * self.fade_out_value * 0.01,
            self.emerald_color[1] * self.fade_out_value * 0.01,
            self.emerald_color[2] * self.fade_out_value * 0.01,
        )
        self.shader.set_light_specular_2(
            self.emerald_color[0] * self.fade_out_value,
            self.emerald_color[1] * self.fade_out_value,
            self.emerald_color[2] * self.fade_out_value,
        )
        self.shader.set_light_diffuse_2(
            self.emerald_color[0] * self.fade_out_value,
            self.emerald_color[1] * self.fade_out_value,
            self.emerald_color[2] * self.fade_out_value,
        )
        self.shader.set_material_specular(0.2, 0.2, 0.2)
        self.shader.set_material_diffuse(0.2, 0.2, 0.2)
        self.shader.set_material_shininess(50)
        self.shader.set_light_ambient(0.1, 0.1, 0.1)
        self.shader.set_material_ambient(0.02, 0.02, 0.02)
        self.shader.set_atten_check(1)

        self.model_matrix.load_identity()

        self.draw_scene()

        # MINIMAP
        glViewport(600, 450, 200, 150)
        glScissor(600, 450, 200, 150)
        glEnable(GL_SCISSOR_TEST)
        glClear(GL_DEPTH_BUFFER_BIT)
        self.shader.set_light_position(self.map_view_matrix.eye)
        self.shader.set_light_diffuse(1, 1, 1)
        self.shader.set_light_specular(0, 0, 0)
        self.shader.set_light_ambient(1.0, 1.0, 1.0)
        self.shader.set_light_ambient_2(0.01, 0.01, 0.01)
        self.shader.set_atten_check(0)

        self.shader.set_projection_matrix(self.minimap_projection_matrix.get_matrix())
        self.shader.set_view_matrix(self.map_view_matrix.get_matrix())

        self.draw_scene(True)

        glDisable(GL_SCISSOR_TEST)

        pygame.display.flip()

    def draw_scene(self, map=False):

        # PLAYER BALL
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(
            self.player_view_matrix.eye.x,
            6,
            self.player_view_matrix.eye.z,
        )
        self.model_matrix.add_scale(1, 0.5, 1)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.shader.set_material_diffuse(0.1, 0.1, 0.1)
        self.shader.set_material_specular(0.9, 0.9, 0.9)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()

        # FLOOR
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(
            (self.maze.rows * self.MAZE_SCALE / 2),
            0,
            (self.maze.cols * self.MAZE_SCALE / 2),
        )
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.shader.set_material_diffuse(0.1, 0.1, 0.1)
        self.maze.floor.draw(self.shader)
        self.model_matrix.pop_matrix()

        # CEILING
        self.model_matrix.push_matrix()
        self.model_matrix.add_translation(
            (self.maze.rows * self.MAZE_SCALE / 2),
            5,
            (self.maze.cols * self.MAZE_SCALE / 2),
        )
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.shader.set_material_diffuse(0.1, 0.1, 0.1)
        if map:
            self.shader.set_material_diffuse(0.9, 0.9, 0.9)
        self.maze.floor.draw(self.shader)
        self.model_matrix.pop_matrix()

        # DRAW MAZE
        for row in range(len(self.maze.blueprint)):
            for col in range(len(self.maze.blueprint[row])):

                if self.maze.blueprint[row][col].has_north_wall:
                    self.model_matrix.push_matrix()
                    self.model_matrix.add_translation(
                        row * self.MAZE_SCALE - self.MAZE_SCALE / 2,
                        self.MAZE_SCALE / 2,
                        col * self.MAZE_SCALE,
                    )
                    self.shader.set_model_matrix(self.model_matrix.matrix)
                    self.shader.set_material_diffuse(0.2, 0.2, 0.2)
                    if map:
                        self.shader.set_material_diffuse(0.1, 0.1, 0.1)
                        self.shader.set_material_specular(0.9, 0.9, 0.9)
                        self.shader.set_material_shininess(80)
                    self.maze.blueprint[row][col].north_wall.draw(self.shader)
                    self.model_matrix.pop_matrix()

                if self.maze.blueprint[row][col].has_east_wall:
                    self.model_matrix.push_matrix()
                    self.model_matrix.add_translation(
                        row * self.MAZE_SCALE,
                        self.MAZE_SCALE / 2,
                        col * self.MAZE_SCALE - self.MAZE_SCALE / 2,
                    )
                    self.shader.set_model_matrix(self.model_matrix.matrix)
                    self.shader.set_material_diffuse(0.2, 0.2, 0.2)
                    if map:
                        self.shader.set_material_diffuse(0.1, 0.1, 0.1)
                        self.shader.set_material_specular(0.9, 0.9, 0.9)
                        self.shader.set_material_shininess(80)
                    self.maze.blueprint[row][col].east_wall.draw(self.shader)
                    self.model_matrix.pop_matrix()

                # FOG OF WAR
                if not self.maze.marked_cells[row][col]:
                    self.model_matrix.push_matrix()
                    self.model_matrix.add_translation(
                        row * self.MAZE_SCALE - self.MAZE_SCALE / 2,
                        6,
                        col * self.MAZE_SCALE - self.MAZE_SCALE / 2,
                    )
                    self.shader.set_model_matrix(self.model_matrix.matrix)
                    self.shader.set_material_diffuse(0.1, 0.1, 0.1)
                    self.maze.blueprint[row][col].cover.draw(self.shader)
                    self.model_matrix.pop_matrix()

        # DRAW EMERALD
        if self.emerald_exists:
            self.model_matrix.push_matrix()
            emerald_x, emerald_y = self.maze.end
            self.model_matrix.add_translation(
                emerald_x * self.MAZE_SCALE - self.MAZE_SCALE / 2,
                self.emerald_height,
                emerald_y * self.MAZE_SCALE - self.MAZE_SCALE / 2,
            )
            self.model_matrix.add_rotation_y(self.emerald_rotation)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_material_diffuse(
                self.emerald_color[0], self.emerald_color[1], self.emerald_color[2]
            )
            self.emerald.draw(self.shader)
            self.model_matrix.pop_matrix()

            self.model_matrix.push_matrix()
            emerald_x, emerald_y = self.maze.end
            self.model_matrix.add_translation(
                emerald_x * self.MAZE_SCALE - self.MAZE_SCALE / 2,
                5.5,
                emerald_y * self.MAZE_SCALE - self.MAZE_SCALE / 2,
            )
            self.model_matrix.add_scale(1, 0.3, 1)
            self.shader.set_model_matrix(self.model_matrix.matrix)
            self.shader.set_material_diffuse(0.8, 0.3, 0.3)
            self.sphere.draw(self.shader)
            self.model_matrix.pop_matrix()

    def program_loop(self):
        exiting = False
        while not exiting:

            keys = pygame.key.get_pressed()
            self.old_location = Point(
                self.player_view_matrix.eye.x,
                self.player_view_matrix.eye.y,
                self.player_view_matrix.eye.z,
            )
            # CAMERA
            if keys[pygame.K_UP]:
                self.main_view_matrix.pitch(-self.rot_step)
            if keys[pygame.K_DOWN]:
                self.main_view_matrix.pitch(self.rot_step)
            if keys[pygame.K_LEFT]:
                self.main_view_matrix.rotate_horizontal(-self.rot_step)
            if keys[pygame.K_RIGHT]:
                self.main_view_matrix.rotate_horizontal(self.rot_step)
            if keys[pygame.K_w]:
                if self.controlling_player:
                    self.main_view_matrix.walk(0, 0, -self.move_step)

            if keys[pygame.K_s]:
                if self.controlling_player:
                    self.main_view_matrix.walk(0, 0, self.move_step)

            if keys[pygame.K_a]:
                if self.controlling_player:
                    self.main_view_matrix.walk(-self.move_step, 0, 0)

            if keys[pygame.K_d]:
                if self.controlling_player:
                    self.main_view_matrix.walk(self.move_step, 0, 0)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting!")
                    exiting = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_ESCAPE:
                        print("Escaping!")
                        exiting = True

                    if event.key == K_UP:
                        self.UP_key_down = True

                    if event.key == K_v:
                        if self.controlling_player:
                            self.main_view_matrix = self.map_view_matrix
                            self.controlling_player = False

                        else:
                            self.main_view_matrix = self.player_view_matrix
                            self.controlling_player = True

                        self.shader.set_view_matrix(self.main_view_matrix.get_matrix())

                elif event.type == pygame.KEYUP:
                    if event.key == K_UP:
                        self.UP_key_down = False

            self.update()
            self.display()

        # OUT OF GAME LOOP
        pygame.quit()

    def start(self):
        self.program_loop()

    def grand_ol_collision(self):
        coll_box = 1.15
        old_player_location_grid = [
            int(self.old_location.x / self.MAZE_SCALE) + 1,
            int(self.old_location.z / self.MAZE_SCALE) + 1,
        ]
        delta_movement = self.player_view_matrix.eye - self.old_location

        if delta_movement.z > 0:
            if self.maze.blueprint[old_player_location_grid[0]][
                old_player_location_grid[1]
            ].has_north_wall:
                if (
                    self.player_view_matrix.eye.z % self.MAZE_SCALE
                    > self.MAZE_SCALE - coll_box
                ):
                    self.player_view_matrix.eye.z = self.old_location.z
            elif (
                (old_player_location_grid[1] < len(self.maze.blueprint[0]))
                and not (
                    self.player_view_matrix.eye.x % self.MAZE_SCALE > 2.5
                    and self.maze.blueprint[old_player_location_grid[0]][
                        old_player_location_grid[1]
                    ].has_east_wall
                )
                and not (
                    self.player_view_matrix.eye.x % self.MAZE_SCALE <= 2.5
                    and self.maze.blueprint[old_player_location_grid[0] - 1][
                        old_player_location_grid[1]
                    ].has_east_wall
                )
            ):
                if (
                    self.maze.blueprint[old_player_location_grid[0]][
                        old_player_location_grid[1] + 1
                    ].has_east_wall
                    or self.maze.blueprint[old_player_location_grid[0] + 1][
                        old_player_location_grid[1]
                    ].has_north_wall
                ):
                    if (
                        self.player_view_matrix.eye.x % self.MAZE_SCALE
                        > self.MAZE_SCALE - coll_box
                        and self.player_view_matrix.eye.z % self.MAZE_SCALE
                        > self.MAZE_SCALE - coll_box
                    ):
                        self.player_view_matrix.eye.z = self.old_location.z
                if (
                    self.maze.blueprint[old_player_location_grid[0] - 1][
                        old_player_location_grid[1] + 1
                    ].has_east_wall
                    or self.maze.blueprint[old_player_location_grid[0] - 1][
                        old_player_location_grid[1]
                    ].has_north_wall
                ):
                    if (
                        self.player_view_matrix.eye.x % self.MAZE_SCALE < coll_box
                        and self.player_view_matrix.eye.z % self.MAZE_SCALE
                        > self.MAZE_SCALE - coll_box
                    ):
                        self.player_view_matrix.eye.z = self.old_location.z

        if delta_movement.z < 0:
            if self.maze.blueprint[old_player_location_grid[0]][
                old_player_location_grid[1] - 1
            ].has_north_wall:
                if self.player_view_matrix.eye.z % self.MAZE_SCALE < coll_box:
                    self.player_view_matrix.eye.z = self.old_location.z
            elif (
                (old_player_location_grid[1] < len(self.maze.blueprint[0]))
                and not (
                    self.player_view_matrix.eye.x % self.MAZE_SCALE > 2.5
                    and self.maze.blueprint[old_player_location_grid[0]][
                        old_player_location_grid[1]
                    ].has_east_wall
                )
                and not (
                    self.player_view_matrix.eye.x % self.MAZE_SCALE <= 2.5
                    and self.maze.blueprint[old_player_location_grid[0] - 1][
                        old_player_location_grid[1]
                    ].has_east_wall
                )
            ):
                if (
                    self.maze.blueprint[old_player_location_grid[0]][
                        old_player_location_grid[1] - 1
                    ].has_east_wall
                    or self.maze.blueprint[old_player_location_grid[0] + 1][
                        old_player_location_grid[1] - 1
                    ].has_north_wall
                ):
                    if (
                        self.player_view_matrix.eye.x % self.MAZE_SCALE
                        > self.MAZE_SCALE - coll_box
                        and self.player_view_matrix.eye.z % self.MAZE_SCALE < coll_box
                    ):
                        self.player_view_matrix.eye.z = self.old_location.z
                if (
                    self.maze.blueprint[old_player_location_grid[0] - 1][
                        old_player_location_grid[1] - 1
                    ].has_east_wall
                    or self.maze.blueprint[old_player_location_grid[0] - 1][
                        old_player_location_grid[1]
                    ].has_north_wall
                ):
                    if (
                        self.player_view_matrix.eye.x % self.MAZE_SCALE < coll_box
                        and self.player_view_matrix.eye.z % self.MAZE_SCALE < coll_box
                    ):
                        self.player_view_matrix.eye.z = self.old_location.z

        if delta_movement.x > 0:
            if self.maze.blueprint[old_player_location_grid[0]][
                old_player_location_grid[1]
            ].has_east_wall:
                if (
                    self.player_view_matrix.eye.x % self.MAZE_SCALE
                    > self.MAZE_SCALE - coll_box
                ):
                    self.player_view_matrix.eye.x = self.old_location.x
            elif (
                (old_player_location_grid[1] < len(self.maze.blueprint[0]))
                and not (
                    self.player_view_matrix.eye.z % self.MAZE_SCALE > 2.5
                    and self.maze.blueprint[old_player_location_grid[0]][
                        old_player_location_grid[1]
                    ].has_north_wall
                )
                and not (
                    self.player_view_matrix.eye.z % self.MAZE_SCALE <= 2.5
                    and self.maze.blueprint[old_player_location_grid[0]][
                        old_player_location_grid[1] - 1
                    ].has_north_wall
                )
            ):
                if old_player_location_grid[1] != len(self.maze.blueprint[0]) - 1:
                    if (
                        self.maze.blueprint[old_player_location_grid[0]][
                            old_player_location_grid[1] + 1
                        ].has_east_wall
                        or self.maze.blueprint[old_player_location_grid[0] + 1][
                            old_player_location_grid[1]
                        ].has_north_wall
                    ):
                        if (
                            self.player_view_matrix.eye.x % self.MAZE_SCALE
                            > self.MAZE_SCALE - coll_box
                            and self.player_view_matrix.eye.z % self.MAZE_SCALE
                            > self.MAZE_SCALE - coll_box
                        ):
                            self.player_view_matrix.eye.x = self.old_location.x

                if (
                    self.maze.blueprint[old_player_location_grid[0]][
                        old_player_location_grid[1] - 1
                    ].has_east_wall
                    or self.maze.blueprint[old_player_location_grid[0] + 1][
                        old_player_location_grid[1] - 1
                    ].has_north_wall
                ):
                    if (
                        self.player_view_matrix.eye.x % self.MAZE_SCALE
                        > self.MAZE_SCALE - coll_box
                        and self.player_view_matrix.eye.z % self.MAZE_SCALE < coll_box
                    ):
                        self.player_view_matrix.eye.x = self.old_location.x

        if delta_movement.x < 0:
            if self.maze.blueprint[old_player_location_grid[0] - 1][
                old_player_location_grid[1]
            ].has_east_wall:
                if self.player_view_matrix.eye.x % self.MAZE_SCALE < coll_box:
                    self.player_view_matrix.eye.x = self.old_location.x
            elif (
                (old_player_location_grid[1] < len(self.maze.blueprint[0]))
                and not (
                    self.player_view_matrix.eye.z % self.MAZE_SCALE > 2.5
                    and self.maze.blueprint[old_player_location_grid[0]][
                        old_player_location_grid[1]
                    ].has_north_wall
                )
                and not (
                    self.player_view_matrix.eye.z % self.MAZE_SCALE <= 2.5
                    and self.maze.blueprint[old_player_location_grid[0]][
                        old_player_location_grid[1] - 1
                    ].has_north_wall
                )
            ):
                if old_player_location_grid[1] != len(self.maze.blueprint[0]) - 1:
                    if (
                        self.maze.blueprint[old_player_location_grid[0] - 1][
                            old_player_location_grid[1] + 1
                        ].has_east_wall
                        or self.maze.blueprint[old_player_location_grid[0] - 1][
                            old_player_location_grid[1]
                        ].has_north_wall
                    ):
                        if (
                            self.player_view_matrix.eye.x % self.MAZE_SCALE < coll_box
                            and self.player_view_matrix.eye.z % self.MAZE_SCALE
                            > self.MAZE_SCALE - coll_box
                        ):
                            self.player_view_matrix.eye.x = self.old_location.x

                if (
                    self.maze.blueprint[old_player_location_grid[0] - 1][
                        old_player_location_grid[1] - 1
                    ].has_east_wall
                    or self.maze.blueprint[old_player_location_grid[0] - 1][
                        old_player_location_grid[1] - 1
                    ].has_north_wall
                ):
                    if (
                        self.player_view_matrix.eye.x % self.MAZE_SCALE < coll_box
                        and self.player_view_matrix.eye.z % self.MAZE_SCALE < coll_box
                    ):
                        self.player_view_matrix.eye.x = self.old_location.x


if __name__ == "__main__":
    GraphicsProgram3D().start()
