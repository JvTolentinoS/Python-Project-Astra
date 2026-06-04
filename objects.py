import numpy    
import ctypes
import math
import numpy as np                                                              
import glm
from OpenGL.GL import *

class Object:
    def __init__(self,
                 initPosition = glm.vec3(0.0, 0.0, 0.0),
                 initVelocity = glm.vec3(0.0, 0.0, 0.0),
                 mass = 0.0,
                 radius = 0.5, 
                 r=1,g=0,b=0,
                 glow = False,
                ):
                
        self.vertices = [
            ##  pos      cor    
            ## [0.0,0.0,0.0, 0,0,0]
        ]

        self.stacks = 20
        self.sectors = 20
        
        self.position = initPosition
        self.velocity = initVelocity
        self.radius = radius
        self.mass = mass
        self.glow = glow

        for i in range(self.stacks + 1):
            theta1 = (i / self.stacks) * glm.pi()
            theta2 = (i+1) / self.stacks * glm.pi()
            for j in range(self.sectors):
                phi1 = j / self.sectors * 2 * glm.pi()
                phi2 = (j+1) / self.sectors * 2 * glm.pi()
                
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
        
        # Criar VAO
        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)

        # Inicializa VBO
        vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,vboId)                 
        glBufferData(GL_ARRAY_BUFFER,
                     self.vertices.nbytes,                   
                     self.vertices, GL_DYNAMIC_DRAW)       
         
        # Setar os ponteiros dos atributos
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

        glEnableVertexAttribArray(0)                    # habilitar pos
        glEnableVertexAttribArray(1)                    # habilitar cor
        
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

    def updatePosition(self):
        self.position[0] += self.velocity[0] / 96
        self.position[1] += self.velocity[1] / 96
        self.position[2] += self.velocity[2] / 96

    def getPosition(self):
        return self.position
    
    def accelerate(self, x, y, z):
        self.velocity[0] += x / 100
        self.velocity[1] += y / 100
        self.velocity[2] += z / 100

    