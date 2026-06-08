import ctypes
import math
from PIL import Image
from PIL import ImageDraw   
import numpy as np                                                              
from OpenGL.GL import *
from OpenGL.GLUT import *
import glm
import constants as c
from camera import Camera


class Background:


    def __init__(self):
        
        self.skybox_vertices = [
            # pos
            -1.0,  1.0, -1.0,
            -1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
             1.0,  1.0, -1.0,
            -1.0,  1.0, -1.0,

            -1.0, -1.0,  1.0,
            -1.0, -1.0, -1.0,
            -1.0,  1.0, -1.0,
            -1.0,  1.0, -1.0,
            -1.0,  1.0,  1.0,
            -1.0, -1.0,  1.0,

             1.0, -1.0, -1.0,
             1.0, -1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0, -1.0,
             1.0, -1.0, -1.0,

            -1.0, -1.0,  1.0,
            -1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
             1.0, -1.0,  1.0,
            -1.0, -1.0,  1.0,

            -1.0,  1.0, -1.0,
             1.0,  1.0, -1.0,
             1.0,  1.0,  1.0,
             1.0,  1.0,  1.0,
            -1.0,  1.0,  1.0,
            -1.0,  1.0, -1.0,

            -1.0, -1.0, -1.0,
            -1.0, -1.0,  1.0,
             1.0, -1.0, -1.0,
             1.0, -1.0, -1.0,
            -1.0, -1.0,  1.0,
             1.0, -1.0,  1.0
        ]

        self.qtd_vertices = len(self.skybox_vertices) // 3
        self.vertices = np.array(self.skybox_vertices, dtype=np.float32)              

        # Skybox
        #
        # Criar VAO
        # ---------
        self.s_VAO = glGenVertexArrays(1)
        glBindVertexArray(self.s_VAO)

        # Inicializa VBO
        # --------------
        self.s_VBO = glGenBuffers(1) 
        glBindBuffer(GL_ARRAY_BUFFER,self.s_VBO)                 
        glBufferData(GL_ARRAY_BUFFER,
                     self.vertices.nbytes,                   
                     self.vertices, GL_STATIC_DRAW)       

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,
                              3,
                              GL_FLOAT,
                              GL_FALSE,
                              3*4,
                              ctypes.c_void_p(0))
        
        self.assets_faces = [
            Image.open("assets/space_rt.png"),
            Image.open("assets/space_lf.png"),
            Image.open("assets/space_dn.png"),
            Image.open("assets/space_up.png"),
            Image.open("assets/space_bk.png"),
            Image.open("assets/space_ft.png"),
        ]
        
        self.cubemap_texture = self.load_cubemap(self.assets_faces)

        glBindBuffer(GL_ARRAY_BUFFER, 0)    
        glBindVertexArray(0)

    def load_cubemap(self, faces: list):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)

        for f in range(len(faces)):
            image = faces[f].transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
            data = image.tobytes()
            if data:
                glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + f, 
                             0, 
                             GL_RGB, 
                             image.width, 
                             image.height,
                             0,
                             GL_RGB,
                             GL_UNSIGNED_BYTE,
                             data)
                
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        return self.texture
    
    def render(self, shaderId):
        glBindVertexArray(self.s_VAO)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.cubemap_texture)
        glDrawArrays(GL_TRIANGLES, 0, self.qtd_vertices)
        glBindVertexArray(0)


class Object:
    
    def __init__(self,
                 name="Object",
                 glow = False,
                 mass = 1, # kg
                 density = 1, # g/cm³ 
                 r = 1, g = 0, b = 0,
                 init_position = glm.vec3(0.0, 0.0, 0.0), # km
                 init_velocity = glm.vec3(0.0, 0.0, 0.0), # km/h
                ):

        self.vertices = []
        self.orbits = []

        self.stacks = 80
        self.sectors = 80
        
        self.glow = glow
        self.position = init_position
        self.velocity = init_velocity
        self.radius = math.cbrt(3 * mass / (4 * math.pi * density)) / 30000 # Apenas para diminuir a escala da simulação
        self.mass = mass
        self.density = density
        self.name = name
        
        # 
        self.eccentricity = self.get_eccentricity_vector()
        self.main_attractor_pos = glm.vec3(0.0, 0.0, 0.0)
        for i in range(self.stacks):
            theta1 = (i / self.stacks) * glm.pi()
            theta2 = (i + 1) / self.stacks * glm.pi()

            for j in range(self.sectors):
                phi1 = j / self.sectors * 2 * glm.pi()
                phi2 = (j + 1) / self.sectors * 2 * glm.pi()
                
                v1 = self.spherical_to_cartesian(self.radius, theta1, phi1)
                v2 = self.spherical_to_cartesian(self.radius, theta1, phi2)
                v3 = self.spherical_to_cartesian(self.radius, theta2, phi1)
                v4 = self.spherical_to_cartesian(self.radius, theta2, phi2)

                n1 = glm.normalize(v1)
                n2 = glm.normalize(v2)
                n3 = glm.normalize(v3)
                n4 = glm.normalize(v4)

                # triangulo 1
                self.vertices.extend([
                    v1[0], v1[1], v1[2], r, g, b, n1.x, n1.y, n1.z
                    ])
                self.vertices.extend([
                    v2[0], v2[1], v2[2], r, g, b, n2.x, n2.y, n2.z
                    ])
                self.vertices.extend([
                    v3[0], v3[1], v3[2], r, g, b, n3.x, n3.y, n3.z
                    ])

                # triangulo 2
                self.vertices.extend([
                    v2[0], v2[1], v2[2], r, g, b, n2.x, n2.y, n2.z
                    ])
                self.vertices.extend([
                    v4[0], v4[1], v4[2], r, g, b, n4.x, n4.y, n4.z
                    ])
                self.vertices.extend([
                    v3[0], v3[1], v3[2], r, g, b, n3.x, n3.y, n3.z
                    ])
        
        self.qtd_vertices = len(self.vertices) // 9
        self.vertices = np.array(self.vertices,             # 32 bits
                                 dtype=np.float32)              
        
        # Criar VAO
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)

        # Inicializa VBO
        VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO)                 
        glBufferData(GL_ARRAY_BUFFER,
                     self.vertices.nbytes,                   
                     self.vertices, 
                     GL_DYNAMIC_DRAW)       
         
        # Setar os ponteiros dos atributos
        glVertexAttribPointer(0,                        # pos
                              3,                        # qtd de valores
                              GL_FLOAT,                 # tipo de dado
                              GL_FALSE,                 # não normalizar
                              9*4,                      # intervalo de bytes entre atributos
                              ctypes.c_void_p(0))       # ponteiro do primeiro attributo

        # CORES
        glVertexAttribPointer(1,                        # pos
                              3,                        # qtd de valores
                              GL_FLOAT,                 # tipo de dado
                              GL_FALSE,                 # não normalizar
                              9*4,                      # intervalo de bytes entre atributos
                              ctypes.c_void_p(3*4))     # ponteiro do segundo attributo

        # NORMAIS
        glVertexAttribPointer(2,                       # pos
                              3,                        # qtd de valores
                              GL_FLOAT,                 # tipo de dado
                              GL_FALSE,                 # não normalizar
                              9*4,                      # intervalo de bytes entre atributos
                              ctypes.c_void_p(6*4))     # ponteiro do segundo attributo
    
        glEnableVertexAttribArray(0)                    # habilitar pos
        glEnableVertexAttribArray(1)                    # habilitar cor
        glEnableVertexAttribArray(2)                    # habilita vetores normalizados

        glBindBuffer(GL_ARRAY_BUFFER, 0)    
        glBindVertexArray(0)

    def spherical_to_cartesian(self, r, theta, phi):
            x = r * math.sin(theta) * math.cos(phi)
            y = r * math.cos(theta)
            z = r * math.sin(theta) * math.sin(phi)
            return glm.vec3(x, y, z)

    def render(self, shaderId):
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLES, 0, self.qtd_vertices) 
        glBindVertexArray(0)

    def update_position(self, dt):
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt
        self.position[2] += self.velocity[2] * dt

    def get_position(self):
        return self.position
    
    def accelerate(self, x, y, z, dt):
        
        self.velocity[0] += x * dt
        self.velocity[1] += y * dt
        self.velocity[2] += z * dt
    
    def new_radius(self, mass):
        self.radius = math.cbrt(3 * mass / (4 * math.pi * self.density)) / 30000 # redução de escala

    def check_collision(self, other):
        dx = other.position[0] - self.position[0]
        dy = other.position[1] - self.position[1]
        dz = other.position[2] - self.position[2]

        distance = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2) + math.pow(dz, 2))

        if (other.radius + self.radius) > distance:
            return -0.2
        return 1
    
    def get_angular_momentum(self, r2, v2):
        r1 = self.position - r2
        v1 = self.velocity - v2 
        result = glm.cross(r1, v1)
        return result
    
    def get_gravitational_parameter(self, M):
        return (c.G * (M + self.mass)) / c.SCALE_KM2
           
    def get_velocity_vec(self, v2):
        return self.velocity - v2
        
    def get_normal_pos(self, r2):
        r1 = self.position - r2
        return glm.normalize(r1)

    def get_main_attractor_pos(self):
        if self.orbits:
            main_body = max(self.orbits, key=lambda orbit: orbit[2])
            return main_body[5]
    
    def get_eccentricity_vector(self):
        if self.orbits:  
            main_body = max(self.orbits, key=lambda orbit: orbit[2])
            
            main_mass = main_body[3]
            r2 = main_body[5]
            v2 = main_body[4]
            
            v_vector = self.get_velocity_vec(v2)
            h_momentum = self.get_angular_momentum(r2, v2)
            n_pos = self.get_normal_pos(r2)
            u_parameter = self.get_gravitational_parameter(main_mass)
            
            eccentricity_vector = glm.cross(v_vector, h_momentum) / u_parameter - n_pos
            
            print(f"\nVELOCIDADE RADIAL {glm.dot(v_vector, n_pos)} |\n POSIÇÃO {self.position} |\n e: {eccentricity_vector} ")
            return eccentricity_vector
        return

    def get_semi_major_axis(self):
        if len(self.orbits) > 0: 
            main_body = max(self.orbits, key=lambda orbit: orbit[2])
            
            main_mass = main_body[3]
            r = glm.length(self.position - main_body[5])
            v2 = glm.length(self.velocity)
            u_parameter = self.get_gravitational_parameter(main_mass)
            
            specific_energy = math.pow(v2, 2)/2 - u_parameter/r
            semi_axis = -u_parameter / (2 * specific_energy)
            
            return semi_axis
        return
            
## W.I.P
class Orbit:
    def __init__(self, obj, r = 1, g = 1, b = 1, nDiv = 200):

        self.vertices = [

        ]
        self.main_attractor_pos = obj.get_main_attractor_pos()
        self.get_obj_pos = obj.get_position()
        semi_major_axis = obj.get_semi_major_axis()
        epsilon = glm.length(obj.get_eccentricity_vector())
        deltaAngle = 2*math.pi/nDiv

        for i in range(nDiv):
            angle = i * deltaAngle
            radius = semi_major_axis * (1 - math.pow(epsilon, 2)) / (1 + epsilon * math.cos(angle))
            
            x = self.main_attractor_pos[0] + radius * math.cos(angle)
            y = self.main_attractor_pos[1] + radius * math.sin(angle)
            z = self.main_attractor_pos[2]
            self.vertices.append([x,y,z, r,g,b])
            
        self.qtd_vertices = len(self.vertices)
        self.vertices = np.array(self.vertices, dtype=np.float32)
        
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)
        
        self.VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,
                     self.VBO)
        glBufferData(GL_ARRAY_BUFFER,
                     self.vertices, GL_STATIC_DRAW)
        
        glVertexAttribPointer(0,
                              3,
                              GL_FLOAT,
                              GL_FALSE,
                              6*4,
                              ctypes.c_void_p(0))

        
        glVertexAttribPointer(1,
                              3,
                              GL_FLOAT,
                              GL_FALSE,
                              6*4,
                              ctypes.c_void_p(3*4))
        
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
    
    def get_rotation(self):
        vmat4 = glm.mat4(1.0)
        
        source = self.main_attractor_pos
        target = self.get_obj_pos
        
        vec_direction = source - target
        vec_angle = math.atan2(vec_direction.y, vec_direction.x)
        
        vec_rotation = glm.vec3(0.0, 1.0, 0.0)
        return glm.rotate(vmat4, vec_angle, vec_rotation)
    
    def render(self, shaderId):
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_LINE_LOOP, 0, self.qtd_vertices)
        glBindVertexArray(0)
            
        
