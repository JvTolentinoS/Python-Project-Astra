from OpenGL.GL import *
import OpenGL.GL.shaders as gls
import glm

class Shader: 
    """
    OpenGL requisita utilizar os programas de Vertex Shader e Fragment Shaders para
    gerar os fragmentos e vértices através da linguagem GLSL (OpenGL Shading Language),
    a biblioteca gls permite compilar a referência desses shaders e os validar posteriormente.
    """
    
    def __init__(self, vertexShaderFileName, fragmentShaderFileName):
        with open(vertexShaderFileName, "r") as file:                   
            vsSource = file.read()
        with open(fragmentShaderFileName, "r") as file:
            fsSource = file.read()
    
        vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
        fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
        self.shaderId = gls.compileProgram(vsId, fsId)

    def bind(self):
        """
        Instala o programa de Shader definido na Instância para o estado de renderização.
        """
        glUseProgram(self.shaderId)
    
    def unbind(self):
        """
        Esvazia o programa de Shader definidos na Instância no estado de renderização.
        """
        glUseProgram(0)

    def setUniform(self, name, x, y=None, z=None, w=None):              
        """
        Encapsula os uniformes, com exceção dos uniformes. Não encapsula mat e vecs.
        """
        name_loc = glGetUniformLocation(self.shaderId, name)
        if y == None: glUniform1f(name_loc, x)
        elif z == None: glUniform2f(name_loc, x, y)
        elif w == None: glUniform3f(name_loc, x, y, z)
        else:         glUniform4f(name_loc, x, y, z, w)

    def setUniformv(self, name, value):
        """
        Encapsula os uniformes de vec2, vec3 e vec4.
        """
        name_loc = glGetUniformLocation(self.shaderId, name)
        if len(value) == 1: glUniform1fv(name_loc, 1, value)
        elif len(value) == 2: glUniform2fv(name_loc, 1, value)
        elif len(value) == 3: glUniform3fv(name_loc, 1, value)
        else: glUniform4fv(name_loc, 1, value)

    def setUniformMat4(self, name, mat):
        """
        Encapsula os uniformes de mat4x4
        """
        name_loc = glGetUniformLocation(self.shaderId, name)
        if name_loc == -1:
            return name_loc
        glUniformMatrix4fv(name_loc, 1, GL_FALSE, glm.value_ptr(mat))
        return name_loc
    
    def setUniformi(self, name, value):
        """
        Encapsula os uniformes booleanos
        """
        name_loc = glGetUniformLocation(self.shaderId, name)
        return glUniform1i(name_loc, value)

    def setUniformGlm(self, name, value):
        """
        Encapsula os uniformes booleanos não númericos.
        """
        name_loc = glGetUniformLocation(self.shaderId, name)
        return glUniform3fv(name_loc, 1, glm.value_ptr(value))