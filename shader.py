from OpenGL.GL import *
import OpenGL.GL.shaders as gls
import glm

class Shader: 
    def __init__(self, vertexShaderFileName, fragmentShaderFileName):
        with open(vertexShaderFileName, "r") as file:                   # OpenGL moderno requer escrever os Shaders.
            vsSource = file.read()
        with open(fragmentShaderFileName, "r") as file:
            fsSource = file.read()
    
        vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
        fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
        self.shaderId = gls.compileProgram(vsId, fsId)

    def bind(self):
        glUseProgram(self.shaderId)
    
    def unbind(self):
        glUseProgram(0)

    def setUniform(self, name, x, y=None, z=None, w=None):              ## facilta um pouco o encapsulamento da cpu pra gpu
        name_loc = glGetUniformLocation(self.shaderId, name)
        if y == None: glUniform1f(name_loc, x)
        elif z == None: glUniform2f(name_loc, x, y)
        elif w == None: glUniform3f(name_loc, x, y, z)
        else:         glUniform4f(name_loc, x, y, z, w)

    def setUniformv(self, name, value):                                 ## nesse caso é para listas
        name_loc = glGetUniformLocation(self.shaderId, name)
        if len(value) == 1: glUniform1fv(name_loc, 1, value)
        elif len(value) == 2: glUniform2fv(name_loc, 1, value)
        elif len(value) == 3: glUniform3fv(name_loc, 1, value)
        else: glUniform4fv(name_loc, 1, value)

    def setUniformMat4(self, name, mat):
        name_loc = glGetUniformLocation(self.shaderId, name)
        if name_loc == -1:
            return name_loc
        glUniformMatrix4fv(name_loc, 1, GL_FALSE, glm.value_ptr(mat))
        return name_loc
    
    def setUniformi(self, name, value):
        name_loc = glGetUniformLocation(self.shaderId, name)
        glUniform1i(name_loc, value)