import ctypes
import math
from PIL import Image
import numpy as np                                                              
from OpenGL.GL import *
from OpenGL.GLUT import *
import glm
import constants as c
from camera import Camera


class Skybox:
    """
    Renderiza 6 imagens em um cubemap para criar um Skybox.
    """
    def __init__(self):
        # Settings
        # --------
        self.skybox_verts = [
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

        self.qty_verts = len(self.skybox_verts) // 3
        self.verts = np.array(self.skybox_verts, dtype=np.float32)              

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
                     self.verts.nbytes,                   
                     self.verts, GL_STATIC_DRAW)       
        
        # Inicializa um array de atributos de a_pos na localização 0
        # -------------------------------------------------------------
        glVertexAttribPointer(0,
                              3,
                              GL_FLOAT,
                              GL_FALSE,
                              3*4,
                              ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        # Carregando as faces
        # -------------------
        self.assets_faces = [
            Image.open("assets/space_rt.png"),
            Image.open("assets/space_lf.png"),
            Image.open("assets/space_dn.png"),
            Image.open("assets/space_up.png"),
            Image.open("assets/space_bk.png"),
            Image.open("assets/space_ft.png"),
        ]
        
        # Especificando um array 2D de Imagens
        self.cubemap_txr = self.load_cubemap(self.assets_faces)

        glBindBuffer(GL_ARRAY_BUFFER, 0)    
        glBindVertexArray(0)

    def load_cubemap(self, faces: list):
        """
        Descreve em glTexImage2D como a imagem deve ser tratada
        e designa em qual face do cube map será carregada a textura.
        """
        self.txr = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.txr)

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
        return self.txr
    
    def render(self, shaderId):
        """
        Vincula o nome do Vertex Array Object gerado em glGenVertexArrays
        para encapsular o VBO, descrição dos vértices e estado de ativação dos 
        atributos, para assim sequenciar a construção dos primitivos em DrawArray.
        """
        glBindVertexArray(self.s_VAO)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.cubemap_txr)
        glDrawArrays(GL_TRIANGLES, 0, self.qty_verts)
        glBindVertexArray(0)

class Object:
    """
    Inicializa um objeto astrônomico com propriedades físicas e com formato esférico. 
    """
    def __init__(self,
                 name="Object",
                 glow = False,
                 mass = 1, # kg
                 density = 1, # g/cm³ 
                 r = 1, g = 0, b = 0,
                 init_position = glm.vec3(0.0, 0.0, 0.0), # km
                 init_velocity = glm.vec3(0.0, 0.0, 0.0), # km/h
                ):
        
        
        # Propriedades Vetoriais
        # Posição: km
        # Velocidade: km/tick
        # ----------------------
        self.position = init_position
        self.velocity = init_velocity
        self.scaled_position = self.position * c.SIMULATION_DISTANCE_SCALED
        # Descrição Físicas
        # Raio: metros / 30.000
        # Massa: kg
        # Densidade kg/m³
        # ---------------------
        self.glow = glow
        self.name = name
        self.mass = mass
        self.density = density
        self.radius = math.cbrt(3 * mass / (4 * math.pi * density)) / c.RADII_SCALE # Apenas para diminuir a escala da simulação
        
        # Elementos do Movimento Orbital
        # angular_L = Velocidade Angular em km²/tick
        # e = Excentricidade medida 
        # ------------------------------
        self.host_body = None
        self.grav_rel = []
        self.rel = []
        self.rel_pos = glm.vec3(0.0, 0.0, 0.0)
        self.focal_pos = glm.vec3(0.0,0.0,0.0)
        self.scaled_focal_pos = self.focal_pos * c.SIMULATION_DISTANCE_SCALED
        self.focal_vel = glm.vec3(0.0,0.0,0.0)
        self.focal_mass = None
        self.angular_L_vec3 = glm.vec3(0.0, 0.0, 0.0)
        self.e_vec3 = self.get_e_vec3() 
        self.has_bond = self.get_bond_status(self.e_vec3)
        
        # Propriedades dos Vértices
        # -------------------------
        self.verts = []
        self.stacks = 80
        self.sectors = 80
        
        
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
                self.verts.extend([
                    v1[0], v1[1], v1[2], r, g, b, n1.x, n1.y, n1.z
                    ])
                self.verts.extend([
                    v2[0], v2[1], v2[2], r, g, b, n2.x, n2.y, n2.z
                    ])
                self.verts.extend([
                    v3[0], v3[1], v3[2], r, g, b, n3.x, n3.y, n3.z
                    ])

                # triangulo 2
                self.verts.extend([
                    v2[0], v2[1], v2[2], r, g, b, n2.x, n2.y, n2.z
                    ])
                self.verts.extend([
                    v4[0], v4[1], v4[2], r, g, b, n4.x, n4.y, n4.z
                    ])
                self.verts.extend([
                    v3[0], v3[1], v3[2], r, g, b, n3.x, n3.y, n3.z
                    ])
        
        self.qty_verts = len(self.verts) // 9
        self.verts = np.array(self.verts,             # 32 bits
                                 dtype=np.float32)              
        
        # Criar VAO
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)

        # Inicializa VBO
        VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO)                 
        glBufferData(GL_ARRAY_BUFFER,
                     self.verts.nbytes,                   
                     self.verts, 
                     GL_DYNAMIC_DRAW)       
         
        # Setar os ponteiros dos atributos
        glVertexAttribPointer(0,                        # pos
                              3,                        # qty de valores
                              GL_FLOAT,                 # tipo de dado
                              GL_FALSE,                 # não normalizar
                              9*4,                      # intervalo de bytes entre atributos
                              ctypes.c_void_p(0))       # ponteiro do primeiro attributo

        # Cores
        glVertexAttribPointer(1,                        # pos
                              3,                        # qty de valores
                              GL_FLOAT,                 # tipo de dado
                              GL_FALSE,                 # não normalizar
                              9*4,                      # intervalo de bytes entre atributos
                              ctypes.c_void_p(3*4))     # ponteiro do segundo attributo

        # Normais
        glVertexAttribPointer(2,                        # pos
                              3,                        # qty de valores
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
        """
        Converte cordenadas polares para um vetor cartesiano
        utilizando y como eixo de altura, x como horizontal e
        z como profundidade.
        """
        x = r * math.sin(theta) * math.cos(phi)
        y = r * math.cos(theta)
        z = r * math.sin(theta) * math.sin(phi)
        return glm.vec3(x, y, z)

    def render(self, shaderId):
        """
        Vincula o nome do Vertex Array Object gerado em glGenVertexArrays
        para encapsular o VBO, descrição dos vértices e estado de ativação dos 
        atributos, para assim sequenciar a construção dos primitivos em DrawArray.
        """
        glBindVertexArray(self.VAO)
        glDrawArrays(GL_TRIANGLES, 0, self.qty_verts) 
        glBindVertexArray(0)

    def update_position(self, dt):
        """
        Incrementa o vetor de posição a partir da derivada do vetor de velocidade.
        """
        self.position[0] += (self.velocity[0] * dt) / c.SIMULATION_DISTANCE_SCALED
        self.position[1] += (self.velocity[1] * dt) / c.SIMULATION_DISTANCE_SCALED
        self.position[2] += (self.velocity[2] * dt) / c.SIMULATION_DISTANCE_SCALED

    def update_position_scaled(self):
        """
        Incrementa o vetor de posição a partir da derivada do vetor de velocidade.
        """
        self.scaled_position = self.position * c.SIMULATION_DISTANCE_SCALED
        
    def get_position(self):
        """
        Getter do vetor de posição.
        """
        return self.position
    
    # @property
    # def scaled_position(self):
    #     """
    #     Proprieridade do vetor de posição escalado
    #     """
    #     return self.scaled_position
    
    # @scaled_position.setter
    # def scaled_position(self):
    #     """
    #     Setter da posição do vetor escalado.
    #     """
    #     return self.get_position() * c.SIMULATION_DISTANCE_SCALED
    
    def accelerate(self, x, y, z, dt):
        """
        Incrementa o vetor de velocidade a partir do vetor de aceleração da gravidade.
        """
        self.velocity[0] += x * dt
        self.velocity[1] += y * dt
        self.velocity[2] += z * dt
    
    def new_radius(self, mass):
        """
        Redefine o raio.
        """
        self.radius = math.cbrt(3 * mass / (4 * math.pi * self.density)) / 30000 # redução de escala

    def check_collision(self, other):
        """
        Reduz a velocidade a partir da verificação da 
        posição relativa dos dois corpos em diferença a soma dos raios. 
        """
        dx = other.position[0] - self.position[0]
        dy = other.position[1] - self.position[1]
        dz = other.position[2] - self.position[2]

        distance = glm.sqrt(glm.pow(dx, 2) + glm.pow(dy, 2) + glm.pow(dz, 2))

        if (other.radius + self.radius) > distance:
            return -0.2
        return 1
    
    def get_angular_L_vec3(self, r2, v2):
        """
        Retorna L vetorial = r vetorial * v vetorial
        """
        r1 = (self.position - r2) * c.SIMULATION_DISTANCE_SCALED
        v1 = self.velocity - v2 
        result = glm.cross(r1, v1)
        self.angular_L_vec3 = result
        return result
    
    def get_gravitational_parameter(self, M):
        """
        Retorna (U) = Constante G * (Corpo Primário + Satélite) (m³/s) => Convertido para (km³/s)
        """
        return (c.G * (M + self.mass)) / c.SCALE_KM2
           
    def get_velocity_vec(self, v2):
        """
        Retorna a velocidade relativa (v) do vetor velocidade ao corpo primário
        """
        return self.velocity - v2
        
    def get_normal_pos(self, r2):
        """
        Retorna o versor da posição relativa n(pos) do vetor posição ao corpo primário
        """
        r1 = self.position - r2
        return glm.normalize(r1)

    def get_rel_pos(self):
        """
        Retorna o corpo primário com a maior Força Gravitacional
        """
        if self.host_body:
            return self.host_body.position
    
    def get_e_vec3(self):
        """
        Retorna excentricidade(e) = vetor (v) * vetor (L) / (U) - (n pos)
        """
        if self.host_body:  
            
            host_mass = self.focal_mass
            position_2 = self.focal_pos
            velocity_2 = self.focal_vel
            
            v_vector = self.get_velocity_vec(velocity_2)
            angular_L = self.get_angular_L_vec3(position_2, velocity_2)
            n_pos = self.get_normal_pos(position_2)
            u_parameter = self.get_gravitational_parameter(host_mass)
            
            e_vec3_vector = glm.cross(v_vector, angular_L) / u_parameter - n_pos
            return e_vec3_vector
        return

    def get_semi_major_axis(self):
        """
        Retorna o semi-eixo maior sendo (a) = -(U) / 2 * Energia Específica(ee) 
        """
        if self.host_body: 
            main_body = self.host_body
            
            main_mass = main_body.mass
            r = (glm.length(self.position - main_body.position)) * c.SIMULATION_DISTANCE_SCALED
            v2 = glm.length(self.velocity - main_body.velocity)
            u_parameter = self.get_gravitational_parameter(main_mass)
            
            specific_energy = glm.pow(v2, 2)/2 - u_parameter/r
            semi_axis = -u_parameter / (2 * specific_energy)
            
            return semi_axis
        return
    
    def get_bond_status(self, e):
        if e is not None and self.host_body is not None:
            e = glm.length(e) 
            return draw_kepler(e, self.get_semi_major_axis(), self.radius, self.host_body.radius)
        return False
    
    def chain_function(self, dt, orbits):
        self.host_body = define_primary_host(self)
        if not self.host_body:
            return
        
        self.grav_rel = get_orbital_objects(self)
        self.rel_pos = self.get_rel_pos()
        
        focal_point = get_focal_point(self.grav_rel)
        self.focal_pos = focal_point[0]
        self.focal_vel = focal_point[1]
        self.focal_mass = focal_point[2]
        
        self.e_vec3 = self.get_e_vec3()
        self.has_bond = self.get_bond_status(self.e_vec3)
        
        if self.has_bond and not orbits:
            orbital_object = Orbit(self)
            orbits.append(orbital_object)

        elif self.has_bond and orbits:
            is_registered = False

            for i in range(len(orbits)):
                if orbits[i].orbital_body_name == self.name:
                    orbits[i].update_orbit(self)
                    is_registered = True

            if not is_registered:
                orbital_object = Orbit(self)
                orbits.append(orbital_object)

# W.I.P

class Orbit:
    """
    Projeta uma elipse correspondente a órbita ligada de Kepler, a partir do corpo primário.
    """
    # Elemento Orbital Global
    # -----------------------
    reference_plane = glm.vec3(1.0, 0.0, 0.0)
    
    def __init__(self, obj = object, r = 1, g = 1, b = 1, nDiv = 1000):

        self.verts = [

        ]
        self.DrawArray = True
        # Parametros dos Corpos
        # ---------------------
        self.orbital_body_name = obj.name
        self.central_body_pos = obj.host_body.position
        self.angular_L = obj.angular_L_vec3
        self.n_angular_L = glm.normalize(self.angular_L)
        self.central_body_rad = obj.radius
        self.host_body_rad = obj.host_body.radius
        
        # Elementos Orbitais 
        # ------------------
        self.semi_major_axis = obj.get_semi_major_axis()
        self.epsilon = obj.get_e_vec3()
        if not self.epsilon:
            return
        self.l_epsilon = glm.length(self.epsilon)
        self.n_epsilon = glm.normalize(self.epsilon)
        self.transversal_vec = glm.cross(self.n_angular_L, 
                                         self.n_epsilon)
        
        # Decidir se a órbita deve ser desenhada
        # --------------------------------------
        if draw_kepler(self.l_epsilon, self.semi_major_axis, self.central_body_rad, self.host_body_rad):
            delta_theta = 2*math.pi/nDiv
            for i in range(nDiv):
                theta = i * delta_theta
                vec3d = self.get_rad_dist(theta) + self.central_body_pos
                
                x = vec3d.x / c.SIMULATION_DISTANCE_SCALED
                y = vec3d.y / c.SIMULATION_DISTANCE_SCALED
                z = vec3d.z / c.SIMULATION_DISTANCE_SCALED
                
                self.verts.append([x,y,z, r,g,b])
                
            self.qty_verts = len(self.verts)
            self.verts = np.array(self.verts, dtype=np.float32)
            
            self.VAO = glGenVertexArrays(1)
            glBindVertexArray(self.VAO)
            
            self.VBO = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER,
                        self.VBO)
            glBufferData(GL_ARRAY_BUFFER,
                        self.verts, GL_DYNAMIC_DRAW)
            
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
    
    def get_rad_dist(self, theta):
        """
        Retorna a distância radial (r) = a * (1 - e²) / (1 + e*cos(theta)) alinhada ao eixo transversal.
        """
        if self.semi_major_axis > 0 and self.l_epsilon >= 0:
            semi_major_axis = self.semi_major_axis
            transversal = self.transversal_vec
            e_epsilon = self.l_epsilon
            n_epsilon= self.n_epsilon 
        
            radial_distance = semi_major_axis * (1 - glm.pow(e_epsilon, 2)) / (1 + (e_epsilon * glm.cos(theta)))
            
            t_radial_distance = (radial_distance * glm.cos(theta) * n_epsilon
                                 + radial_distance * glm.sin(theta) * transversal)
            
            #print(e_epsilon)
            return t_radial_distance
        return glm.vec3(0.0, 0.0, 0.0)
    
    def update_orbit(self, obj, nDiv = 1000, r = 1, g = 1, b = 1):
        """
        Realiza uma atualização parcial dos atributos do Vertex no Buffer Object (VBO). 
        """
        # Parametros dos Corpos
        # ----------------------------------------------------------------
        self.central_body_pos = obj.focal_pos
        self.angular_L = obj.angular_L_vec3
        self.n_angular_L = glm.normalize(self.angular_L)
        self.central_body_rad = obj.radius
        self.host_body_rad = obj.host_body.radius
        
        # Elementos Orbitais 
        # ----------------------------------------------------------------
        self.semi_major_axis = obj.get_semi_major_axis()
        self.l_epsilon = glm.length(obj.get_e_vec3())
        self.n_epsilon = glm.normalize(obj.get_e_vec3())
        self.transversal_vec = glm.cross(self.n_angular_L, 
                                         self.n_epsilon) 
        
        if draw_kepler(self.l_epsilon, self.semi_major_axis, self.central_body_rad, self.host_body_rad):
            self.DrawArray = True
            verts = [
                
            ]
             
            delta_theta = 2*math.pi/nDiv
            for i in range(nDiv):
                theta = i * delta_theta
                
                x = (self.get_rad_dist(theta)[0] + self.central_body_pos[0]) / c.SIMULATION_DISTANCE_SCALED
                y = (self.get_rad_dist(theta)[1] + self.central_body_pos[1]) / c.SIMULATION_DISTANCE_SCALED
                z = (self.get_rad_dist(theta)[2] + self.central_body_pos[2]) / c.SIMULATION_DISTANCE_SCALED
                
                verts.append([x,y,z, r,g,b])
                
            verts = np.array(verts, dtype=np.float32)
            
            glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
            glBufferSubData(GL_ARRAY_BUFFER, 0, verts.nbytes, verts)
            glBindBuffer(GL_ARRAY_BUFFER, 0)
        else:
            self.DrawArray = False
            self.verts = []
            self.qty_verts = 0
            
    def render(self, shaderId):
        """
        Vincula o nome do Vertex Array Object gerado em glGenVertexArrays
        para encapsular o VBO, descrição dos vértices e estado de ativação dos 
        atributos, para assim sequenciar a construção dos primitivos em DrawArray.
        """
        if self.DrawArray and self.qty_verts > 0:
            glBindVertexArray(self.VAO)
            glDrawArrays(GL_LINE_LOOP, 0, self.qty_verts)
            glBindVertexArray(0)
        
def draw_kepler(epsilon, semi_major_axis, rad1, rad2):
    """
    Retorna se a orbita referenciada será ligada (Elípitica ou circular) ou desligada (Híperbole ou decaída)
    a partir da diferença do semi-eixo maior e o raio dos pares.
    """
    return False
    if epsilon >= 1 or epsilon < 0: 
        return False
    if semi_major_axis: 
        r_min = semi_major_axis * (1 - epsilon)
        if (r_min <= (rad1 + rad2)):
            return False
    return True

def define_rel(current_body, iterated_body):

    if iterated_body:
        iterated_body_info = [
            iterated_body.name,
            iterated_body.mass,
            glm.vec3(iterated_body.velocity),
            glm.vec3(iterated_body.position),
            iterated_body
        ]
        is_registered = False
        
        if not current_body.rel:
            current_body.rel.append(iterated_body_info)
            is_registered = True

        else: 
            for reg_rel in current_body.rel:
                if reg_rel[0] == iterated_body_info[0]:
                    reg_rel[1] = iterated_body_info[1]
                    reg_rel[2] = iterated_body_info[2] 
                    reg_rel[3] = iterated_body_info[3]
                    reg_rel[4] = iterated_body_info[4]
                    is_registered = True

        if not is_registered:
            current_body.rel.append(iterated_body_info)

def define_host(current_body):
    if current_body.rel:
        body_list = []
        body_mass = sorted(current_body.rel, 
                        key=lambda rel: rel[1],
                        reverse=True)
        for body in body_mass:
            distance = glm.length(body[4].scaled_position - current_body.scaled_position)
            if distance > 0:
                mass_r2 = body[1] / pow(distance, 2)
                body_list.append([mass_r2, body[4]])
        most_massive = max(body_list,
                           key=lambda mass_r2: mass_r2[0])
        
        return most_massive[1]

def define_primary_host(current_body):
    if current_body.rel:
        current_body_rel = sorted(current_body.rel,
                                          key=lambda rel: rel[1],
                                          reverse=True)
        
        for body in current_body_rel:
            parent_body = body[4]
            host_body = define_host(parent_body)
            
            if define_hill_zone(current_body, 
                                parent_body, 
                                host_body):
                return parent_body
        return current_body_rel[0][4]
    return None

def define_hill_zone(current_body, parent_body, host_body):
    if parent_body and host_body:
        current_body_dist = glm.length(current_body.position - parent_body.position) * c.SIMULATION_DISTANCE_SCALED
        parent_body_dist = glm.length(parent_body.position - host_body.position) * c.SIMULATION_DISTANCE_SCALED
        
        hill_zone = parent_body_dist * math.cbrt(parent_body.mass / (3 * host_body.mass))    
        
        if hill_zone > current_body_dist:
            return True
        return False

def get_focal_point(orbital_objects):
    if orbital_objects:
        orbital_objs_mass = sum(orb.mass for orb in orbital_objects)
        
        focal_point_pos = glm.vec3(0.0, 0.0, 0.0)
        focal_point_vel = glm.vec3(0.0, 0.0, 0.0)
        
        for orb in orbital_objects:
            focal_point_pos += orb.focal_pos * orb.mass
            focal_point_vel += orb.focal_vel * orb.mass
            
        result_pos = focal_point_pos / orbital_objs_mass
        result_vel = focal_point_vel / orbital_objs_mass
        
        return result_pos, result_vel, orbital_objs_mass

def verify_binary_pair(binary_1, binary_2):
    binary_system = [binary_1, binary_2]
    
    if binary_1.mass >= binary_2.mass:
        host = binary_1
        parent = binary_2
    else:
        host = binary_2
        parent = binary_1
    
    focal_pos = get_focal_point(binary_system)[1]
    
    focal_parent_dist = glm.length(focal_pos - parent.position)
        
    return 

def get_orbital_objects(current_body):
    
    if not current_body.host_body:
        return []
    
    host = current_body.host_body
    
    if host is current_body or verify_binary_pair(current_body, host):
        return [host, current_body]
    
    return [host]
