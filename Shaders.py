from OpenGL.GL import *
from math import *
import sys
from Base3DObjects import *


class Shader3D:
    def __init__(self):
        vert_shader = glCreateShader(GL_VERTEX_SHADER)
        shader_file = open(sys.path[0] + "/simple3D.vert")
        glShaderSource(vert_shader, shader_file.read())
        shader_file.close()
        glCompileShader(vert_shader)
        result = glGetShaderiv(vert_shader, GL_COMPILE_STATUS)
        if result != 1:
            print(
                "Couldn't compile vertex shader\nShader compilation Log:\n"
                + str(glGetShaderInfoLog(vert_shader))
            )

        frag_shader = glCreateShader(GL_FRAGMENT_SHADER)
        shader_file = open(sys.path[0] + "/simple3D.frag")
        glShaderSource(frag_shader, shader_file.read())
        shader_file.close()
        glCompileShader(frag_shader)
        result = glGetShaderiv(frag_shader, GL_COMPILE_STATUS)
        if result != 1:
            print(
                "Couldn't compile fragment shader\nShader compilation Log:\n"
                + str(glGetShaderInfoLog(frag_shader))
            )

        self.renderingProgramID = glCreateProgram()
        glAttachShader(self.renderingProgramID, vert_shader)
        glAttachShader(self.renderingProgramID, frag_shader)
        glLinkProgram(self.renderingProgramID)
        result = glGetProgramiv(self.renderingProgramID, GL_LINK_STATUS)
        if result != 1:
            print(
                "Couldn't link shader program\nLink compilation Log:\n"
                + str(glGetProgramInfoLog(self.renderingProgramID))
            )

        self.positionLoc = glGetAttribLocation(self.renderingProgramID, "a_position")
        glEnableVertexAttribArray(self.positionLoc)

        self.normalLoc = glGetAttribLocation(self.renderingProgramID, "a_normal")
        glEnableVertexAttribArray(self.normalLoc)

        self.uvLoc = glGetAttribLocation(self.renderingProgramID, "a_uv")
        glEnableVertexAttribArray(self.uvLoc)

        self.useTextureLoc = glGetUniformLocation(
            self.renderingProgramID, "u_use_texture"
        )

        self.modelMatrixLoc = glGetUniformLocation(
            self.renderingProgramID, "u_model_matrix"
        )
        self.viewMatrixLoc = glGetUniformLocation(
            self.renderingProgramID, "u_view_matrix"
        )
        self.projectionMatrixLoc = glGetUniformLocation(
            self.renderingProgramID, "u_projection_matrix"
        )

        self.eyePositionLoc = glGetUniformLocation(
            self.renderingProgramID, "u_eye_position"
        )
        self.numLightsLoc = glGetUniformLocation(
            self.renderingProgramID, "u_num_lights"
        )

        self.lightPositionsLoc = []
        self.lightDiffuseLoc = []
        self.lightSpecularLoc = []
        self.lightAmbientLoc = []

        for i in range(10):
            self.lightPositionsLoc.append(
                glGetUniformLocation(self.renderingProgramID, f"u_light_positions[{i}]")
            )
            self.lightDiffuseLoc.append(
                glGetUniformLocation(self.renderingProgramID, f"u_light_diffuse[{i}]")
            )
            self.lightSpecularLoc.append(
                glGetUniformLocation(self.renderingProgramID, f"u_light_specular[{i}]")
            )
            self.lightAmbientLoc.append(
                glGetUniformLocation(self.renderingProgramID, f"u_light_ambient[{i}]")
            )

        self.matDiffuseLoc = glGetUniformLocation(
            self.renderingProgramID, "u_mat_diffuse"
        )
        self.matSpecularLoc = glGetUniformLocation(
            self.renderingProgramID, "u_mat_specular"
        )
        self.matAmbientLoc = glGetUniformLocation(
            self.renderingProgramID, "u_mat_ambient"
        )
        self.matShininessLoc = glGetUniformLocation(
            self.renderingProgramID, "u_mat_shininess"
        )
        self.attenCheckLoc = glGetUniformLocation(
            self.renderingProgramID, "u_atten_check"
        )
        self.diffuseTextureLoc = glGetUniformLocation(
            self.renderingProgramID, "u_tex01"
        )
        # glUniform1f(self.diffuseTextureLoc, GL_TEXTURE1)
        self.specularTextureLoc = glGetUniformLocation(
            self.renderingProgramID, "u_tex02"
        )

    def use(self):
        try:
            glUseProgram(self.renderingProgramID)
        except OpenGL.error.GLError:
            print(glGetProgramInfoLog(self.renderingProgramID))
            raise

    def set_model_matrix(self, matrix_array):
        glUniformMatrix4fv(self.modelMatrixLoc, 1, True, matrix_array)

    def set_view_matrix(self, matrix_array):
        glUniformMatrix4fv(self.viewMatrixLoc, 1, True, matrix_array)

    def set_projection_matrix(self, matrix_array):
        glUniformMatrix4fv(self.projectionMatrixLoc, 1, True, matrix_array)

    def set_eye_position(self, pos):
        glUniform4f(self.eyePositionLoc, pos.x, pos.y, pos.z, 1.0)

    def set_light_position(self, index, pos):
        if index < 10:
            glUniform4f(self.lightPositionsLoc[index], pos.x, pos.y, pos.z, 1.0)

    def set_light_diffuse(self, index, r, g, b):
        if index < 10:
            glUniform4f(self.lightDiffuseLoc[index], r, g, b, 1.0)

    def set_light_specular(self, index, r, g, b):
        if index < 10:
            glUniform4f(self.lightSpecularLoc[index], r, g, b, 1.0)

    def set_light_ambient(self, index, r, g, b):
        if index < 10:
            glUniform4f(self.lightAmbientLoc[index], r, g, b, 1.0)

    def set_num_lights(self, num):
        glUniform1i(self.numLightsLoc, num)

    def set_material_diffuse(self, r, g, b):
        glUniform4f(self.matDiffuseLoc, r, g, b, 1.0)

    def set_material_specular(self, r, g, b):
        glUniform4f(self.matSpecularLoc, r, g, b, 1.0)

    def set_material_ambient(self, r, g, b):
        glUniform4f(self.matAmbientLoc, r, g, b, 1.0)

    def set_material_shininess(self, shininess):
        glUniform1f(self.matShininessLoc, shininess)

    def set_diffuse_texture(self, number):
        glUniform1i(self.diffuseTextureLoc, number)

    def set_specular_texture(self, number):
        glUniform1i(self.specularTextureLoc, number)

    def set_attenuation_check(self, enabled):
        glUniform1i(self.attenCheckLoc, 1 if enabled else 0)

    def set_use_texture(self, use_it):
        glUniform1i(self.useTextureLoc, 1 if use_it else 0)

    def set_position_attribute(self, vertex_array):
        glVertexAttribPointer(self.positionLoc, 3, GL_FLOAT, False, 0, vertex_array)

    def set_normal_attribute(self, vertex_array):
        glVertexAttribPointer(self.normalLoc, 3, GL_FLOAT, False, 0, vertex_array)

    def set_uv_attribute(self, vertex_array):
        glVertexAttribPointer(self.uvLoc, 2, GL_FLOAT, False, 0, vertex_array)

    def set_attribute_buffers(self, vertex_buffer_id):
        glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_id)
        glVertexAttribPointer(
            self.positionLoc,
            3,
            GL_FLOAT,
            False,
            6 * sizeof(GLfloat),
            OpenGL.GLU.ctypes.c_void_p(0),
        )
        glVertexAttribPointer(
            self.normalLoc,
            3,
            GL_FLOAT,
            False,
            6 * sizeof(GLfloat),
            OpenGL.GLU.ctypes.c_void_p(3 * sizeof(GLfloat)),
        )
