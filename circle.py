import numpy    
import ctypes
import math
import numpy as np                                                              
import glm
from OpenGL.GL import *


class Circle:
    def __init__(self, nDiv=50, radius=0.5, posx=0, posy=0):
        self.vertices = [
            ##  pos      cor
            ## [0.0,0.0, 0,0,0]
            
        ]

        deltaAngle = 2*math.pi / nDiv
        for i in range(nDiv):
            angle = i*deltaAngle

            x = posx + math.cos(angle)
            y = posy + math.sin(angle)
            
            self.vertices.append([x * radius,
                                  y * radius, 
                                  1, 1, 1])

        self.qtdVertices = len(self.vertices) // 6
        self.vertices = np.array(self.vertices,             # 32 bits
                                 dtype=np.float32)              
        
        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)

        vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,                       # dados para vbo
                     vboId)                
        glBufferData(GL_ARRAY_BUFFER,                       # tipo de buffer 00                    self.vertices.nbytes,                  # tamanho do buffer 
                     self.vertices, GL_DYNAMIC_DRAW)        # para animar as orbitas
        
        # POSIÇÃO
        glVertexAttribPointer(0,                        # pos
                              2,                        # qtd de valores
                              GL_FLOAT,                 # tipo de dado
                              GL_FALSE,                 # não normalizar
                              5*4,                      # intervalo de bytes entre atributos
                              ctypes.c_void_p(0))       # ponteiro do primeiro attributo

        # CORES
        glVertexAttribPointer(1,                        # pos
                              3,                        # qtd de valores
                              GL_FLOAT,                 # tipo de dado
                              GL_FALSE,                 # não normalizar
                              5*4,                      # intervalo de bytes entre atributos
                              ctypes.c_void_p(2*4))     # ponteiro do segundo attributo

        glEnableVertexAttribArray(0)                   # habilitar pos
        glEnableVertexAttribArray(1)                   # habilitar cor
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def render(self, shaderId):
        glBindVertexArray(self.vaoId)
        glDrawArrays(GL_ARRAY_BUFFER, 0, self.qtdVertices) ## TROCAR
        glBindVertexArray(0)

class Sphere:
    def __init__(self, radius = 0.5, stacks = 20, sectors = 20, r=1,g=0,b=0):
        self.vertices = [
            ##  pos      cor    
            ## [0.0,0.0,0.0, 0,0,0]
        ]

        for i in range(stacks + 1):
            theta1 = (i / stacks) * glm.pi()
            theta2 = (i+1) / stacks * glm.pi()
            for j in range(sectors):
                phi1 = j / sectors * 2 * glm.pi()
                phi2 = (j+1) / sectors * 2 * glm.pi()
                
                v1 = self.sphericalToCartesian(radius, theta1, phi1)
                v2 = self.sphericalToCartesian(radius, theta1, phi2)
                v3 = self.sphericalToCartesian(radius, theta2, phi1)
                v4 = self.sphericalToCartesian(radius, theta2, phi2)

                # triangulo 1
                self.vertices.extend([v1[0], v1[1], v1[2], r,g,b])
                self.vertices.extend([v2[0], v2[1], v2[2], r,g,b])
                self.vertices.extend([v3[0], v3[1], v3[2], r,g,b])

                # triangulo 2
                self.vertices.extend([v2[0], v2[1], v2[2], r,g,b])
                self.vertices.extend([v4[0], v4[1], v4[2], r,g,b])
                self.vertices.extend([v3[0], v3[1], v3[2], r,g,b])
        
        self.qtdVertices = len(self.vertices) // 6
        self.vertices = np.array(self.vertices,             # 32 bits
                                 dtype=np.float32)              
        
        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)

        vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,                       # dados para vbo
                     vboId)                
        glBufferData(GL_ARRAY_BUFFER,                       # tipo de buffer 00                    self.vertices.nbytes,                  # tamanho do buffer 
                     self.vertices, GL_DYNAMIC_DRAW)        # para animar as orbitas
        
        # POSIÇÃO
        glVertexAttribPointer(0,                        # pos
                              3,                        # qtd de valores
                              GL_FLOAT,                 # tipo de dado
                              GL_FALSE,                 # não normalizar
                              6*4,                      # intervalo de bytes entre atributos
                              ctypes.c_void_p(0))       # ponteiro do primeiro attributo

        # CORES
        glVertexAttribPointer(1,                        # pos
                              3,                        # qtd de valores
                              GL_FLOAT,                 # tipo de dado
                              GL_FALSE,                 # não normalizar
                              6*4,                      # intervalo de bytes entre atributos
                              ctypes.c_void_p(3*4))     # ponteiro do segundo attributo

        glEnableVertexAttribArray(0)                   # habilitar pos
        glEnableVertexAttribArray(1)                   # habilitar cor
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def sphericalToCartesian(self, r, theta, phi):
            x = r * math.sin(theta) * math.cos(phi)
            y = r * math.cos(theta)
            z = r * math.sin(theta) * math.sin(phi)
            return glm.vec3(x, y, z)

    def render(self, shaderId):
        glBindVertexArray(self.vaoId)
        glDrawArrays(GL_TRIANGLES, 0, self.qtdVertices) ## TROCAR
        glBindVertexArray(0)

                
                