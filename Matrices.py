from math import *  # trigonometry

from Base3DObjects import *


class ModelMatrix:
    def __init__(self):
        self.matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        self.stack = []
        self.stack_count = 0
        self.stack_capacity = 0

    def load_identity(self):
        self.matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]

    def copy_matrix(self):
        new_matrix = [0] * 16
        for i in range(16):
            new_matrix[i] = self.matrix[i]
        return new_matrix

    def add_transformation(self, matrix2):
        counter = 0
        new_matrix = [0] * 16
        for row in range(4):
            for col in range(4):
                for i in range(4):
                    new_matrix[counter] += (
                        self.matrix[row * 4 + i] * matrix2[col + 4 * i]
                    )
                counter += 1
        self.matrix = new_matrix

    def add_nothing(self):
        other_matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        self.add_transformation(other_matrix)

    def add_translation(self, x, y, z):
        other_matrix = [1, 0, 0, x, 0, 1, 0, y, 0, 0, 1, z, 0, 0, 0, 1]
        self.add_transformation(other_matrix)

    def add_scale(self, x, y, z):
        other_matrix = [x, 0, 0, 0, 0, y, 0, 0, 0, 0, z, 0, 0, 0, 0, 1]
        self.add_transformation(other_matrix)

    def add_rotation_y(self, angle):
        other_matrix = [
            cos(angle),
            0,
            sin(angle),
            0,
            0,
            1,
            0,
            0,
            -sin(angle),
            0,
            cos(angle),
            0,
            0,
            0,
            0,
            1,
        ]
        self.add_transformation(other_matrix)

    def add_rotation_x(self, angle):
        other_matrix = [
            1,
            0,
            0,
            0,
            0,
            cos(angle),
            -sin(angle),
            0,
            0,
            sin(angle),
            cos(angle),
            0,
            0,
            0,
            0,
            1,
        ]
        self.add_transformation(other_matrix)

    def print(self):
        print(self.matrix)

    ## MAKE OPERATIONS TO ADD TRANLATIONS, SCALES AND ROTATIONS ##
    # ---

    # YOU CAN TRY TO MAKE PUSH AND POP (AND COPY) LESS DEPENDANT ON GARBAGE COLLECTION
    # THAT CAN FIX SMOOTHNESS ISSUES ON SOME COMPUTERS
    def push_matrix(self):
        self.stack.append(self.copy_matrix())

    def pop_matrix(self):
        self.matrix = self.stack.pop()

    # This operation mainly for debugging
    def __str__(self):
        ret_str = ""
        counter = 0
        for _ in range(4):
            ret_str += "["
            for _ in range(4):
                ret_str += " " + str(self.matrix[counter]) + " "
                counter += 1
            ret_str += "]\n"
        return ret_str


# The ViewMatrix class holds the camera's coordinate frame and
# set's up a transformation concerning the camera's position
# and orientation


class ViewMatrix:
    def __init__(self):
        self.eye = Point(0, 0, 0)
        self.u = Vector(1, 0, 0)
        self.v = Vector(0, 1, 0)
        self.n = Vector(0, 0, -1)
        self.vertical_rot = 0

    ## MAKE OPERATIONS TO ADD LOOK, SLIDE, PITCH, YAW and ROLL ##
    # ---

    def look(self, center_look: Point, up: Vector = Vector(0, 1, 0)):
        self.n = self.eye - center_look
        self.n.normalize()
        self.u = up.cross(self.n)
        self.u.normalize()
        self.v = self.n.cross(self.u)
        self.v.normalize()

    def look_down(self):
        self.n = Vector(0, 1, 0)
        self.v = Vector(0, 0, -1)
        self.u = self.v.cross(self.n)
        self.u.normalize()

        self.v = self.n.cross(self.u)
        self.v.normalize()
        self.n.normalize()

    def slide(self, deltaU, deltaV, deltaN):
        self.eye.x += deltaU * self.u.x + deltaV * self.v.x + deltaN * self.n.x
        self.eye.y += deltaU * self.u.y + deltaV * self.v.y + deltaN * self.n.y
        self.eye.z += deltaU * self.u.z + deltaV * self.v.z + deltaN * self.n.z

    def walk(self, deltaU, deltaV, deltaN):
        n_copy = Vector(self.n.x, self.n.y, self.n.z)
        n_copy.y = 0
        n_copy.normalize()
        self.eye.x += deltaU * self.u.x + deltaV * self.v.x + deltaN * n_copy.x
        self.eye.z += deltaU * self.u.z + deltaV * self.v.z + deltaN * n_copy.z

    def roll(self, angle):
        angCos = cos(radians(angle))
        angSin = sin(radians(angle))

        temp_u = self.u
        temp_v = self.v

        self.u = Vector(
            angCos * temp_u.x - angSin * temp_v.x,
            angCos * temp_u.y - angSin * temp_v.y,
            angCos * temp_u.z - angSin * temp_v.z,
        )

        self.v = Vector(
            angSin * temp_u.x + angCos * temp_v.x,
            angSin * temp_u.y + angCos * temp_v.y,
            angSin * temp_u.z + angCos * temp_v.z,
        )

        self.u.normalize()
        self.v.normalize()
        self.n.normalize()

    def pitch(self, angle):

        if angle + self.vertical_rot > 90:
            return
        if angle + self.vertical_rot < -90:
            return

        self.vertical_rot += angle

        angCos = cos(radians(angle))
        angSin = sin(radians(angle))

        temp_v = self.v
        temp_n = self.n

        self.v = Vector(
            angCos * temp_v.x - angSin * temp_n.x,
            angCos * temp_v.y - angSin * temp_n.y,
            angCos * temp_v.z - angSin * temp_n.z,
        )

        self.n = Vector(
            angSin * temp_v.x + angCos * temp_n.x,
            angSin * temp_v.y + angCos * temp_n.y,
            angSin * temp_v.z + angCos * temp_n.z,
        )

        self.u.normalize()
        self.v.normalize()
        self.n.normalize()

    def yaw(self, angle):
        angCos = cos(radians(angle))
        angSin = sin(radians(angle))

        temp_u = self.u
        temp_n = self.n

        self.u = Vector(
            angCos * temp_u.x + angSin * temp_n.x,
            angCos * temp_u.y + angSin * temp_n.y,
            angCos * temp_u.z + angSin * temp_n.z,
        )

        self.n = Vector(
            -angSin * temp_u.x + angCos * temp_n.x,
            -angSin * temp_u.y + angCos * temp_n.y,
            -angSin * temp_u.z + angCos * temp_n.z,
        )

        self.u.normalize()
        self.v.normalize()
        self.n.normalize()

    def rotate_vector_around_y(self, vector, angle):
        c = cos(radians(angle))
        s = sin(radians(angle))

        tmp_x = vector.x * c + vector.z * s
        tmp_y = vector.y
        tmp_z = -vector.x * s + vector.z * c

        return Vector(tmp_x, tmp_y, tmp_z)

    def rotate_horizontal(self, angle):
        self.n = self.rotate_vector_around_y(self.n, angle)
        self.u = self.rotate_vector_around_y(self.u, angle)
        self.v = self.rotate_vector_around_y(self.v, angle)

    def get_matrix(self):
        minusEye = Vector(-self.eye.x, -self.eye.y, -self.eye.z)
        return [
            self.u.x,
            self.u.y,
            self.u.z,
            minusEye.dot(self.u),
            self.v.x,
            self.v.y,
            self.v.z,
            minusEye.dot(self.v),
            self.n.x,
            self.n.y,
            self.n.z,
            minusEye.dot(self.n),
            0,
            0,
            0,
            1,
        ]


# The ProjectionMatrix class builds transformations concerning
# the camera's "lens"


class ProjectionMatrix:
    def __init__(self):
        self.left = -1
        self.right = 1
        self.bottom = -1
        self.top = 1
        self.near = -1
        self.far = 1

        self.is_orthographic = True

    ## MAKE OPERATION TO SET PERSPECTIVE PROJECTION (don't forget to set is_orthographic to False) ##
    # ---
    def set_perspective(self, fovy, aspect, near, far):
        self.near = near
        self.far = far
        self.top = near * tan(radians(fovy) / 2)
        self.bottom = -self.top
        self.right = self.top * aspect
        self.left = -self.right
        self.is_orthographic = False

    def set_orthographic(self, left, right, bottom, top, near, far):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.near = near
        self.far = far
        self.is_orthographic = True

    def get_matrix(self):
        if self.is_orthographic:
            A = 2 / (self.right - self.left)
            B = -(self.right + self.left) / (self.right - self.left)
            C = 2 / (self.top - self.bottom)
            D = -(self.top + self.bottom) / (self.top - self.bottom)
            E = 2 / (self.near - self.far)
            F = (self.near + self.far) / (self.near - self.far)

            return [A, 0, 0, B, 0, C, 0, D, 0, 0, E, F, 0, 0, 0, 1]

        else:
            A = (2 * self.near) / (self.right - self.left)
            B = (self.right + self.left) / (self.right - self.left)
            C = (2 * self.near) / (self.top - self.bottom)
            D = (self.top + self.bottom) / (self.top - self.bottom)
            E = -(self.far + self.near) / (self.far - self.near)
            F = -(2 * self.far * self.near) / (self.far - self.near)

            return [A, 0, B, 0, 0, C, D, 0, 0, 0, E, F, 0, 0, -1, 0]


# The ProjectionViewMatrix returns a hardcoded matrix
# that is just used to get something to send to the
# shader before you properly implement the ViewMatrix
# and ProjectionMatrix classes.
# Feel free to throw it away afterwards!


class ProjectionViewMatrix:
    def __init__(self):
        pass

    def get_matrix(self):
        return [
            0.45052942369783683,
            0.0,
            -0.15017647456594563,
            0.0,
            -0.10435451285616304,
            0.5217725642808152,
            -0.3130635385684891,
            0.0,
            -0.2953940042189954,
            -0.5907880084379908,
            -0.8861820126569863,
            3.082884480118567,
            -0.2672612419124244,
            -0.5345224838248488,
            -0.8017837257372732,
            3.7416573867739413,
        ]


# IDEAS FOR OPERATIONS AND TESTING:
# if __name__ == "__main__":
#     matrix = ModelMatrix()
#     matrix.push_matrix()
#     print(matrix)
#     matrix.add_translation(3, 1, 2)
#     matrix.push_matrix()
#     print(matrix)
#     matrix.add_scale(2, 3, 4)
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)

#     matrix.add_translation(5, 5, 5)
#     matrix.push_matrix()
#     print(matrix)
#     matrix.add_scale(3, 2, 3)
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)

#     matrix.pop_matrix()
#     print(matrix)

#     matrix.push_matrix()
#     matrix.add_scale(2, 2, 2)
#     print(matrix)
#     matrix.push_matrix()
#     matrix.add_translation(3, 3, 3)
#     print(matrix)
#     matrix.push_matrix()
#     matrix.add_rotation_y(pi / 3)
#     print(matrix)
#     matrix.push_matrix()
#     matrix.add_translation(1, 1, 1)
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
#     matrix.pop_matrix()
#     print(matrix)
