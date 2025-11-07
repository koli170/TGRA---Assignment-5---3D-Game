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

from ojb_3D_loading import *


class Object:
    def __init__(
        self,
        RGB: Vector,
        position: Vector,
        shader,
        model_matrix,
        gravity=False,
        collisions=False,
        scale=Vector(1, 1, 1),
        pushable=False,
        texture=None,
        texture_spec=None,
        shape=None,
        offset=None,
        stairs=False,
        rotation=False,
        bound_one=False,
        bound_two=False,
        bound_three=False,
        ambient=Vector(0, 0, 0),
        skip_light=False,
        lava=False,
    ):
        self.RGB = RGB
        self.scale = scale
        self.position = position
        self.gravity = gravity
        self.collisions = collisions
        self.model_matrix = model_matrix
        self.shader = shader
        self.floor = floor
        self.pushable = pushable
        self.touching_floor = False
        self.velocity = Vector(0, 0, 0)
        self.texture = texture
        self.cube = Cube() if shape is None else shape
        self.texture_spec = texture_spec
        self.offset = offset
        self.stairs = stairs
        self.rotation = rotation
        self.bound_one = bound_one
        self.bound_two = bound_two
        self.bound_three = bound_three
        self.ambient = ambient
        self.skip_light = skip_light
        self.lava = lava

    def draw(self):
        self.model_matrix.push_matrix()
        if self.skip_light:
            self.shader.set_use_lighting(1)
        else:
            self.shader.set_use_lighting(0)
        if self.texture != None:
            self.shader.set_use_texture(True)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            self.shader.set_diffuse_texture(0)
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            self.shader.set_specular_texture(1)
        else:
            self.shader.set_use_texture(False)
        self.shader.set_material_diffuse(self.RGB.x, self.RGB.y, self.RGB.z)
        self.shader.set_material_ambient(self.ambient.x, self.ambient.y, self.ambient.z)
        if self.offset:
            self.model_matrix.add_translation(
                self.position.x + self.offset[0],
                self.position.y + self.offset[1],
                self.position.z + self.offset[2],
            )
        else:
            self.model_matrix.add_translation(
                self.position.x, self.position.y, self.position.z
            )
        if self.rotation != False:
            self.model_matrix.add_rotation_z(self.rotation)
        self.model_matrix.add_scale(self.scale.x, self.scale.y, self.scale.z)
        self.shader.set_model_matrix(self.model_matrix.matrix)
        self.cube.draw(self.shader)
        self.model_matrix.pop_matrix()


class CubeObj(Object):
    def __init__(
        self,
        RGB: Vector,
        position: Vector,
        shader,
        model_matrix,
        gravity=False,
        collisions=False,
        scale=Vector(1, 1, 1),
        pushable=False,
        texture=None,
        texture_spec=None,
        pressure_plate=False,
        pressed_on=False,
        shape=None,
        offset=None,
        stairs=False,
        rotation=False,
        bound_one=False,
        bound_two=False,
        bound_three=False,
        ambient=Vector(0, 0, 0),
        friction=1,
        wall=False,
        skip_light=False,
        lava=False,
    ):
        super().__init__(
            RGB,
            position,
            shader,
            model_matrix,
            gravity,
            collisions,
            scale,
            pushable,
            texture,
            texture_spec,
            shape=shape,
            offset=offset,
            stairs=stairs,
            rotation=rotation,
            bound_one=bound_one,
            bound_two=bound_two,
            bound_three=bound_three,
            ambient=ambient,
            skip_light=skip_light,
            lava=lava,
        )
        self.pressure_plate = pressure_plate
        self.pressed_on = pressed_on
        self.friction = friction
        self.wall = wall

    def pressed(self):
        if self.pressed_on:
            self.RGB = Vector(0, 1, 0)
        else:
            self.RGB = Vector(1, 0, 0)

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

        self.width = 1280
        self.height = 720

        pygame.init()
        pygame.display.set_mode(
            (self.width, self.height), pygame.OPENGL | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("Awesome Puzzle")

        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

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
        self.projection_matrix.set_perspective(90, self.width / self.height, 0.5, 100)
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())

        # Create shapes
        self.objects = []
        self.colliding_objects = []
        self.sphere = Sphere(8, 16)
        self.cube = Cube()
        self.tryggvi_cube = load_obj_file("MeshModelAddon/models", "NEWTRYGGVICUBE.obj")
        self.tryggvi_cube.set_opengl_buffers()

        # Time control
        self.my_clock = 0
        self.clock = pygame.time.Clock()
        self.clock.tick()
        self.touching_floor = True
        self.floor_player_touching = None
        # Movement / rotation
        self.angle = 0
        self.move_speed = 10
        self.rotation_speed = 150
        self.jumping = False
        self.player_velocity = 0
        self.jump_speed = 20
        self.jump_duration = 0.2
        self.time_jumped = 0
        self.push_force = 40
        self.relative_mouse_movement = (0, 0, 0)
        self.mouse_movement = Vector(0, 0, 0)
        self.mouse_sens = 0.1

        self.gravity = -40

        self.pressure_plate_one_pressed = False
        self.pressure_plate_one = None

        self.pressure_plate_two_pressed = False
        self.pressure_plate_two = None

        self.pressure_plate_three_pressed = False
        self.pressure_plate_three = None

        self.touching_lava = False

        self.original_player_position = None
        self.original_cubeone_position = None
        self.original_cubetwo_position = None

        self.death_timer = 0

        self.cube_one = None
        self.cube_two = None

        self.UP_key_down = False
        self.white_background = False

        self.texture_id_01 = self.load_texture("Textures/companioncube_uv.png")
        self.texture_id_02 = self.load_texture("Textures/FNM_KingForADay.jpg")
        self.texture_id_03 = self.load_texture("Textures/returnofthespacecowboy.jpg")
        self.texture_wall = self.load_texture("Textures/TGRAF-WALL.png")
        self.texture_floor = self.load_texture("Textures/TGRAF-GOLF.png")
        self.texture_bridge = self.load_texture("Textures/TGRAF-BRIDGE.png")
        self.texture_lava = self.load_texture("Textures/TGRAF-LAVA.png")
        self.texture_lava_large = self.load_texture("Textures/TGRAF-LAVA_LARGE.png")

        self.create_obj()

        self.player = self.main_view_matrix.eye
        self.player.x = -18
        self.player.z = -2
        self.original_player_position = Vector(-17, 3, -2)
        self.main_view_matrix.look(Vector(0, 0, 0))

    def load_texture(self, path_string):
        surface = pygame.image.load(path_string)
        tex_string = pygame.image.tostring(surface, "RGBA", 1)
        width = surface.get_width()
        height = surface.get_height()
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            width,
            height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            tex_string,
        )
        return tex_id

    def update(self):
        delta_time = self.clock.tick() / 1000.0
        if delta_time > 0.1:
            return
        self.my_clock += delta_time
        if self.death_timer > 2:
            self.reset()
        if self.touching_lava:
            self.death_timer += delta_time

        if self.pressure_plate_one != None:
            self.pressure_plate_one_pressed = self.pressure_plate_one.pressed_on
        if self.pressure_plate_two != None:
            self.pressure_plate_two_pressed = self.pressure_plate_two.pressed_on
        if self.pressure_plate_three != None:
            self.pressure_plate_three_pressed = self.pressure_plate_three.pressed_on

        self.angle += pi * delta_time
        self.rot_step = self.rotation_speed * delta_time
        self.move_step = self.move_speed * delta_time

        if self.jumping:
            self.time_jumped += delta_time
            self.player.y += self.jump_speed * delta_time
        if self.time_jumped >= self.jump_duration and self.jumping:
            self.jumping = False

        self.handle_physics()

    def display(self):
        glEnable(GL_DEPTH_TEST)
        (
            glClearColor(1.0, 1.0, 1.0, 1.0)
            if self.white_background
            else glClearColor(0, 0, 1, 1)
        )
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self.width, self.height)

        # Update camera and light
        self.shader.set_projection_matrix(self.projection_matrix.get_matrix())
        self.shader.set_view_matrix(self.main_view_matrix.get_matrix())
        self.shader.set_eye_position(self.main_view_matrix.eye)

        # Basic light settings
        self.shader.set_num_lights(1)
        self.shader.set_light_diffuse(0, 0.7, 0.7, 0.7)
        self.shader.set_light_position(0, Vector(0, 5, 0))
        self.shader.set_light_specular(0, 0.4, 0.4, 0.4)
        self.shader.set_light_ambient(0, 0.3, 0.3, 0.3)

        self.model_matrix.load_identity()
        self.draw_scene()

        pygame.display.flip()

    def handle_physics(self):
        delta_time = self.clock.get_time() / 1000.0
        if delta_time > 0.1:
            return

        player_half_size = 1.0
        player_half_height = 3.0
        for colliding_object in self.colliding_objects:
            if colliding_object.gravity:
                colliding_object.velocity.y = (
                    colliding_object.velocity.y + self.gravity * delta_time
                )
                colliding_object.position.y += colliding_object.velocity.y * delta_time
            if (
                abs(colliding_object.velocity.x) > 0.001
                or abs(colliding_object.velocity.z) > 0.001
            ):
                colliding_object.position.x += colliding_object.velocity.x * delta_time
                colliding_object.position.z += colliding_object.velocity.z * delta_time
                colliding_object.velocity.x *= (
                    1 - colliding_object.friction * delta_time
                )
                colliding_object.velocity.z *= (
                    1 - colliding_object.friction * delta_time
                )
                if abs(colliding_object.velocity.x) < 0.01:
                    colliding_object.velocity.x = 0
                if abs(colliding_object.velocity.z) < 0.01:
                    colliding_object.velocity.z = 0

        if not self.jumping:
            self.player_velocity = self.player_velocity + self.gravity * delta_time
            self.player.y += self.player_velocity * delta_time

        found_floor = False

        for object in self.objects:
            if object.pressure_plate:
                object.pressed_on = False
                object.pressed()
            if (
                (object.bound_one and self.pressure_plate_one_pressed == False)
                or (object.bound_two and self.pressure_plate_two_pressed == False)
                or (object.bound_three and self.pressure_plate_three_pressed == False)
            ):
                continue
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

            player_min_x = self.player.x - player_half_size
            player_max_x = self.player.x + player_half_size
            player_min_y = self.player.y - player_half_height
            player_max_y = self.player.y + player_half_height
            player_min_z = self.player.z - player_half_size
            player_max_z = self.player.z + player_half_size

            if (
                player_min_x < max_x
                and player_max_x > min_x
                and player_min_y < max_y
                and player_max_y > min_y
                and player_min_z < max_z
                and player_max_z > min_z
            ):

                overlap_x = min(player_max_x - min_x, max_x - player_min_x)
                overlap_y = min(player_max_y - min_y, max_y - player_min_y)
                overlap_z = min(player_max_z - min_z, max_z - player_min_z)

                if (
                    overlap_x < overlap_y
                    and overlap_x < overlap_z
                    and (object.pressure_plate == False and object.stairs == False)
                ):
                    # Push along X axis
                    if self.player.x < (min_x + max_x) / 2:
                        self.player.x = min_x - player_half_size
                        if object.pushable and self.floor_player_touching != object:
                            object.velocity.x += self.push_force * delta_time
                    else:
                        if object.pushable and self.floor_player_touching != object:
                            object.velocity.x -= self.push_force * delta_time
                        self.player.x = max_x + player_half_size

                if overlap_y < overlap_x and overlap_y < overlap_z:
                    # Push along Y axis
                    if self.player.y < (min_y + max_y) / 2:
                        self.player.y = min_y - player_half_height
                        if self.jumping:
                            self.jumping = False
                            self.time_jumped = 0
                    else:
                        if object.lava:
                            self.gravity = -1
                            if self.touching_lava == False:
                                self.player_velocity = 0
                                self.touching_lava = True
                        else:
                            if object.pressure_plate:
                                object.pressed_on = True
                                object.pressed()
                            self.player.y = max_y + player_half_height
                            found_floor = True
                            self.floor_player_touching = object
                            self.player_velocity = 0

                if (
                    overlap_z < overlap_x
                    and overlap_z < overlap_y
                    and (object.pressure_plate == False and object.stairs == False)
                ):
                    # Push along Z axis
                    if self.player.z < (min_z + max_z) / 2:
                        if object.pushable and self.floor_player_touching != object:
                            object.velocity.z += self.push_force * delta_time
                        self.player.z = min_z - player_half_size
                    else:
                        if object.pushable and self.floor_player_touching != object:
                            object.velocity.z -= self.push_force * delta_time
                        self.player.z = max_z + player_half_size

        self.touching_floor = found_floor

        for colliding_object in self.colliding_objects:
            found_floor_object = False
            colliding_object.friction = 10
            for object in self.objects:
                if object == colliding_object:
                    continue

                min_y = inf
                min_x = inf
                min_z = inf
                max_y = -inf
                max_x = -inf
                max_z = -inf
                colliding_min_y = inf
                colliding_min_x = inf
                colliding_min_z = inf
                colliding_max_y = -inf
                colliding_max_x = -inf
                colliding_max_z = -inf

                for vertice in object.get_vertices():
                    min_x = min(min_x, vertice[0])
                    min_y = min(min_y, vertice[1])
                    min_z = min(min_z, vertice[2])
                    max_x = max(max_x, vertice[0])
                    max_y = max(max_y, vertice[1])
                    max_z = max(max_z, vertice[2])

                for vertice in colliding_object.get_vertices():
                    colliding_min_x = min(colliding_min_x, vertice[0])
                    colliding_min_y = min(colliding_min_y, vertice[1])
                    colliding_min_z = min(colliding_min_z, vertice[2])
                    colliding_max_x = max(colliding_max_x, vertice[0])
                    colliding_max_y = max(colliding_max_y, vertice[1])
                    colliding_max_z = max(colliding_max_z, vertice[2])

                if (
                    colliding_min_x < max_x
                    and colliding_max_x > min_x
                    and colliding_min_y < max_y
                    and colliding_max_y > min_y
                    and colliding_min_z < max_z
                    and colliding_max_z > min_z
                ):

                    overlap_x = min(colliding_max_x - min_x, max_x - colliding_min_x)
                    overlap_y = min(colliding_max_y - min_y, max_y - colliding_min_y)
                    overlap_z = min(colliding_max_z - min_z, max_z - colliding_min_z)

                    if (
                        overlap_x < overlap_y
                        and overlap_x < overlap_z
                        and (object.pressure_plate == False and object.stairs == False)
                    ):
                        if colliding_object.position.x < (min_x + max_x) / 2:
                            colliding_object.position.x = (
                                min_x - (colliding_max_x - colliding_min_x) / 2
                            )
                            if object.wall:
                                colliding_object.velocity.x -= 11000 * delta_time
                                colliding_object.friction = 0.5
                        else:
                            colliding_object.position.x = (
                                max_x + (colliding_max_x - colliding_min_x) / 2
                            )
                            if object.wall:
                                colliding_object.velocity.x += 11000 * delta_time
                                colliding_object.friction = 0.5

                    if overlap_y < overlap_x and overlap_y < overlap_z:
                        if colliding_object.position.y < (min_y + max_y) / 2:
                            colliding_object.position.y = (
                                min_y - (colliding_max_y - colliding_min_y) / 2
                            )
                        else:
                            colliding_object.position.y = (
                                max_y + (colliding_max_y - colliding_min_y) / 2
                            )
                            if object.pressure_plate:
                                object.pressed_on = True
                                object.pressed()
                            if object.lava:
                                if colliding_object == self.cube_one:
                                    colliding_object.position = (
                                        self.original_cubeone_position
                                    )
                                elif colliding_object == self.cube_two:
                                    colliding_object.position = (
                                        self.original_cubetwo_position
                                    )
                            found_floor_object = True
                            colliding_object.velocity.y = 0
                            if object.stairs:
                                colliding_object.velocity.x += -40 * delta_time
                                colliding_object.friction = 1

                    if (
                        overlap_z < overlap_x
                        and overlap_z < overlap_y
                        and (object.pressure_plate == False and object.stairs == False)
                    ):
                        if colliding_object.position.z < (min_z + max_z) / 2:
                            colliding_object.position.z = (
                                min_z - (colliding_max_z - colliding_min_z) / 2
                            )
                            if object.wall:
                                colliding_object.velocity.z -= 11000 * delta_time
                                colliding_object.friction = 0.5
                        else:
                            colliding_object.position.z = (
                                max_z + (colliding_max_z - colliding_min_z) / 2
                            )
                            if object.wall:
                                colliding_object.velocity.z += 11000 * delta_time
                                colliding_object.friction = 0.5
            colliding_object.touching_floor = found_floor_object

    def draw_scene(self):
        for object in self.objects:
            if (
                (self.pressure_plate_one_pressed == False and object.bound_one)
                or (self.pressure_plate_two_pressed == False and object.bound_two)
                or (self.pressure_plate_three_pressed == False and object.bound_three)
            ):
                continue
            object.draw()

    def create_stairs(
        self, start_position, num_steps, step_width, step_depth, step_height
    ):
        for i in range(num_steps):
            x_pos = start_position.x + (i * step_width / 2)

            # Height scale grows cumulatively
            height_scale = step_height * (i + 1)

            # Y position needs to be offset by half the height since cube position is at center
            y_pos = start_position.y + (height_scale / 2)

            z_pos = start_position.z

            stair = CubeObj(
                Vector(1, 1, 1),
                Vector(x_pos, y_pos, z_pos),
                self.shader,
                self.model_matrix,
                scale=Vector(step_width, height_scale, step_depth),
                stairs=True,
                bound_one=True,
            )
            self.objects.append(stair)

    def create_obj(self, map=False):
        tryggvi_cube_one = CubeObj(
            Vector(1, 1, 1),
            Vector(-4, 5, -4),
            self.shader,
            self.model_matrix,
            scale=Vector(1.2, 1.2, 1.2),
            pushable=True,
            collisions=True,
            gravity=True,
            shape=self.tryggvi_cube,
            offset=(0, -2.35, 0),
        )
        self.objects.append(tryggvi_cube_one)
        self.original_cubeone_position = tryggvi_cube_one.position.copy()
        self.cube_one = tryggvi_cube_one

        pressure_plate = CubeObj(
            Vector(1, 0, 0),
            Vector(-15, -1.5, -10),
            self.shader,
            self.model_matrix,
            scale=Vector(4, 0.3, 4),
            pressure_plate=True,
        )
        self.objects.append(pressure_plate)
        self.pressure_plate_one = pressure_plate

        pressure_plate_two = CubeObj(
            Vector(1, 0, 0),
            Vector(-16, -1.5, 10),
            self.shader,
            self.model_matrix,
            scale=Vector(4, 0.3, 4),
            pressure_plate=True,
        )
        self.objects.append(pressure_plate_two)
        self.pressure_plate_two = pressure_plate_two

        pressure_plate_three = CubeObj(
            Vector(1, 0, 0),
            Vector(-6, -1.5, 10),
            self.shader,
            self.model_matrix,
            scale=Vector(4, 0.3, 4),
            pressure_plate=True,
        )
        self.objects.append(pressure_plate_three)
        self.pressure_plate_three = pressure_plate_three

        # Ground
        ground = CubeObj(
            Vector(1, 1, 1),
            Vector(-10, -2, 0),
            self.shader,
            self.model_matrix,
            scale=Vector(20, 0.5, 40),
            texture=self.texture_floor,
            texture_spec=self.texture_floor,
            ambient=Vector(1, 1, 1),
        )
        self.objects.append(ground)

        ground = CubeObj(
            Vector(1, 1, 1),
            Vector(50, -2, 0),
            self.shader,
            self.model_matrix,
            scale=Vector(20, 0.5, 40),
            texture=self.texture_floor,
            texture_spec=self.texture_floor,
        )
        self.objects.append(ground)

        # Ceiling
        ceiling = CubeObj(
            Vector(0.4, 0.4, 0.4),
            Vector(20, 15, 0),
            self.shader,
            self.model_matrix,
            scale=Vector(80, 0.5, 40),
        )
        self.objects.append(ceiling)

        # Front wall
        right_wall = CubeObj(
            Vector(1, 1, 1),
            Vector(60 - 0.5, 6, 0),
            self.shader,
            self.model_matrix,
            scale=Vector(0.5, 16, 40),
            texture=self.texture_wall,
            texture_spec=self.texture_wall,
            wall=True,
        )
        self.objects.append(right_wall)

        # back wall
        left_wall = CubeObj(
            Vector(1, 1, 1),
            Vector(-20 + 0.5, 6, 0),
            self.shader,
            self.model_matrix,
            scale=Vector(0.5, 16, 40),
            texture=self.texture_wall,
            texture_spec=self.texture_wall,
            wall=True,
        )
        self.objects.append(left_wall)

        # Right wall
        back_wall = CubeObj(
            Vector(1, 1, 1),
            Vector(20, 6, 20),
            self.shader,
            self.model_matrix,
            scale=Vector(80, 16, 0.5),
            texture=self.texture_wall,
            texture_spec=self.texture_wall,
            wall=True,
        )
        self.objects.append(back_wall)

        # Left wall
        front_wall = CubeObj(
            Vector(1, 1, 1),
            Vector(20, 6, -20),
            self.shader,
            self.model_matrix,
            scale=Vector(80, 16, 0.5),
            texture=self.texture_wall,
            texture_spec=self.texture_wall,
            wall=True,
        )
        self.objects.append(front_wall)

        # Stairs
        self.create_stairs(Vector(0, -1.7, 18), 10, 2, 8, 1)

        # walkway from stairs
        walk_way = CubeObj(
            Vector(1, 1, 1),
            Vector(16, 8.05, 18),
            self.shader,
            self.model_matrix,
            scale=Vector(12, 0.5, 8),
            bound_one=True,
        )
        self.objects.append(walk_way)

        # lava
        lava = CubeObj(
            Vector(1, 1, 1),
            Vector(20, -2.5, 0),
            self.shader,
            self.model_matrix,
            scale=Vector(40, 0.5, 40),
            texture=self.texture_lava_large,
            texture_spec=self.texture_lava_large,
            skip_light=True,
            lava=True,
        )
        self.objects.append(lava)

        tryggvi_cube_two = CubeObj(
            Vector(1, 1, 1),
            Vector(17, 13, 17),
            self.shader,
            self.model_matrix,
            scale=Vector(1.2, 1.2, 1.2),
            pushable=True,
            collisions=True,
            gravity=True,
            shape=self.tryggvi_cube,
            offset=(0, -2.35, 0),
        )
        self.objects.append(tryggvi_cube_two)
        self.original_cubetwo_position = tryggvi_cube_two.position.copy()
        self.cube_two = tryggvi_cube_two

        walk_way_escape = CubeObj(
            Vector(1, 1, 1),
            Vector(10, -2, 0),
            self.shader,
            self.model_matrix,
            scale=Vector(20, 0.5, 8),
            bound_two=True,
            texture=self.texture_bridge,
            texture_spec=self.texture_bridge,
        )
        self.objects.append(walk_way_escape)
        walk_way_escape_two = CubeObj(
            Vector(1, 1, 1),
            Vector(30, -2, 0),
            self.shader,
            self.model_matrix,
            scale=Vector(20, 0.5, 8),
            bound_three=True,
            texture=self.texture_bridge,
            texture_spec=self.texture_bridge,
        )
        self.objects.append(walk_way_escape_two)
        for object in self.objects:
            if object.collisions:
                self.colliding_objects.append(object)

    def reset(self):
        # Reset player position and state
        self.main_view_matrix.eye.x = self.original_player_position.x
        self.main_view_matrix.eye.y = self.original_player_position.y
        self.main_view_matrix.eye.z = self.original_player_position.z
        self.player_velocity = 0
        self.jumping = False
        self.time_jumped = 0
        self.touching_floor = False
        self.floor_player_touching = None

        # Reset cube positions and velocities
        self.cube_one.position.x = self.original_cubeone_position.x
        self.cube_one.position.y = self.original_cubeone_position.y
        self.cube_one.position.z = self.original_cubeone_position.z
        self.cube_one.velocity = Vector(0, 0, 0)

        self.cube_two.position.x = self.original_cubetwo_position.x
        self.cube_two.position.y = self.original_cubetwo_position.y
        self.cube_two.position.z = self.original_cubetwo_position.z
        self.cube_two.velocity = Vector(0, 0, 0)

        # Reset lava state
        self.touching_lava = False
        self.gravity = -40
        self.death_timer = 0

        # Reset camera
        self.main_view_matrix.look(Vector(0, 0, 0))

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

            if self.relative_mouse_movement != (0, 0, 0):
                self.main_view_matrix.rotate_horizontal(
                    -self.relative_mouse_movement[0] * self.mouse_sens
                )

                self.main_view_matrix.pitch(
                    self.relative_mouse_movement[1] * self.mouse_sens
                )

                self.relative_mouse_movement = (0, 0, 0)

            if keys[pygame.K_w] and self.touching_lava == False:
                self.main_view_matrix.walk(0, 0, -self.move_step)
            if keys[pygame.K_s] and self.touching_lava == False:
                self.main_view_matrix.walk(0, 0, self.move_step)
            if keys[pygame.K_a] and self.touching_lava == False:
                self.main_view_matrix.walk(-self.move_step, 0, 0)
            if keys[pygame.K_d] and self.touching_lava == False:
                self.main_view_matrix.walk(self.move_step, 0, 0)

            # EVENT HANDLING
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quitting!")
                    exiting = True
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_movement = event.pos
                    self.relative_mouse_movement = event.rel
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
                        self.jumping = True
                        self.time_jumped = 0

            self.update()
            self.display()

        pygame.quit()

    def start(self):
        self.program_loop()


if __name__ == "__main__":
    GraphicsProgram3D().start()
