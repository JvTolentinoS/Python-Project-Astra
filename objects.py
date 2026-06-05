import numpy    
import ctypes
import math
import numpy as np                                                              
import glm
from OpenGL.GL import *
from PIL import Image

class Background: 
    def __init__(self, imgpath="background.jpg"):
        self.vertices = [
            ## pos, cor, uv

             -1.0,1.0,0.0,  1.0,1.0,1.0, 0.0,1.0,
             -1.0,-1.0,0.0, 1.0,1.0,1.0, 0.0,0.0,
              1.0,-1.0,0.0, 1.0,1.0,1.0, 1.0,0.0,

             -1.0,1.0,0.0,  1.0,1.0,1.0, 0.0,1.0,
              1.0,-1.0,0.0, 1.0,1.0,1.0, 1.0,0.0,
              1.0,1.0,0.0,  1.0,1.0,1.0, 1.0,1.0
        ]

        self.qtdVertices = len(self.vertices) // 8
        self.vertices = np.array(self.vertices, dtype=np.float32)              
        
        # Criar VAO
        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)

        # Inicializa VBO
        vboId = glGenBuffers(1) 
        glBindBuffer(GL_ARRAY_BUFFER,vboId)                 
        glBufferData(GL_ARRAY_BUFFER,
                     self.vertices.nbytes,                   
                     self.vertices, GL_STATIC_DRAW)       
        
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        image = Image.open(imgpath)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        img_data = image.convert("RGBA").tobytes()
        
        glTexImage2D(GL_TEXTURE_2D,
                     0,
                     GL_RGBA,
                     image.width,
                     image.height,
                     0,
                     GL_RGBA,
                     GL_UNSIGNED_BYTE,
                     img_data)

        # Setar os ponteiros dos atributos
        glVertexAttribPointer(0,                        # pos
                              3,                        # qtd de valores
                              GL_FLOAT,                 # tipo de dado
                              GL_FALSE,                 # não normalizar
                              8*4,                      # intervalo de bytes entre atributos
                              ctypes.c_void_p(0))       # ponteiro do primeiro attributo

        # cor
        glVertexAttribPointer(1,                        # pos
                              3,                        # qtd de valores
                              GL_FLOAT,                 # tipo de dado
                              GL_FALSE,                 # não normalizar
                              8*4,                      # intervalo de bytes entre atributos
                              ctypes.c_void_p(3*4))     # ponteiro do segundo attributo

        # textura        
        glVertexAttribPointer(2,                        # pos
                              2,                        # qtd de valores
                              GL_FLOAT,                 # tipo de dado
                              GL_FALSE,                 # não normalizar
                              8*4,                      # intervalo de bytes entre atributos
                              ctypes.c_void_p(6*4))     # ponteiro do segundo attributo

        glEnableVertexAttribArray(0)                    # habilitar pos
        glEnableVertexAttribArray(1)                    # habilitar cor
        glEnableVertexAttribArray(2)                    # habilitar habilita textura
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)    
        glBindVertexArray(0)

    def render(self, shaderId):
        glBindVertexArray(self.vaoId)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glDrawArrays(GL_TRIANGLES, 0, self.qtdVertices) ## TROCAR
        glBindVertexArray(0)



class Object:
    def __init__(self,
                 initPosition = glm.vec3(0.0, 0.0, 0.0),
                 initVelocity = glm.vec3(0.0, 0.0, 0.0),
                 mass = 1, # kg
                 density = 1, # kg/m³ 
                 r=1,g=0,b=0,
                 glow = False,
                 name="Object"
                ):

        self.vertices = [
            ##  pos      cor    
            ## [0.0,0.0,0.0, 0,0,0]
        ]

        self.orbits = [
            
        ]

        self.stacks = 20
        self.sectors = 20
        
        self.position = initPosition
        self.velocity = initVelocity
        self.radius = math.cbrt(3 * mass / (4 * math.pi * density)) / 30000 # Apenas para diminuir a escala da simulação
        self.mass = mass
        self.density = density
        self.glow = glow
        self.name = name
        self.distance = 0
        self.angularMomentum = self.getAngularMomentum()

        for i in range(self.stacks + 1):
            theta1 = (i / self.stacks) * glm.pi()
            theta2 = (i+1) / self.stacks * glm.pi()
            for j in range(self.sectors):
                phi1 = j / self.sectors * 2 * glm.pi()
                phi2 = (j+1) / self.sectors * 2 * glm.pi()
                
                v1 = self.sphericalToCartesian(self.radius, theta1, phi1)
                v2 = self.sphericalToCartesian(self.radius, theta1, phi2)
                v3 = self.sphericalToCartesian(self.radius, theta2, phi1)
                v4 = self.sphericalToCartesian(self.radius, theta2, phi2)

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

    def updatePosition(self, dt):
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        self.position[2] += self.velocity[2] * dt

    def getPosition(self):
        return self.position
    
    def accelerate(self, x, y, z, dt):
        self.velocity[0] += x * dt
        self.velocity[1] += y * dt
        self.velocity[2] += z * dt
    
    def recalculateRadius(self, mass):
        self.radius = math.cbrt(3 * mass / (4 * math.pi * self.density)) / 30000

    def checkCollision(self, other):
        dx = other.position[0] - self.position[0]
        dy = other.position[1] - self.position[1]
        dz = other.position[2] - self.position[2]
        distance = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2) + math.pow(dz, 2))
        if (other.radius + self.radius) > distance:
            return -0.2
        return 1

    def getAngularMomentum(self):
        am = self.mass * glm.cross(self.position, self.velocity)
        return am
    
class Orbit:
    def __init__(self, obj, r=1, g=1, b=1, nDiv = 100):
        self.vertices = [

        ]

        epsilon = 0
        deltaAngle = 2*math.pi/nDiv

        
        for i in range(nDiv):
            angle = i*deltaAngle
            x = r * math.cos(math.radians(angle)) / 1 + epsilon * math.cos(math.radians(angle))
            y = r * math.sin(math.radians(angle)) / 1 + epsilon * math.cos(math.radians(angle))
            z = 0.0
            self.vertices.append([x,y,z, r,g,b])
        self.qtdVertices = len(self.qtdVertices)



