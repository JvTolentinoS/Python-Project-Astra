import ctypes
import math
import functools
import json
from dataclasses import dataclass, field, asdict
import glm
from PIL import Image
import numpy as np
from typing import ClassVar
from OpenGL.GL import *
from OpenGL.GLUT import *
from camera import Camera
import constants as c
import random as r

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
        # ----------------------------------------------------------
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
        #
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


@dataclass
class Object:
    """
    Inicializa um objeto astrônomico com propriedades físicas e com formato esférico.
    """
    stacks: ClassVar[int] = 80
    sectors: ClassVar[int] = 80
    delta_time: ClassVar[float] = 0
    
    name: str
    _color: tuple
    _init_position: glm.vec3
    _init_velocity: glm.vec3
    _glow: bool = False

    # Descrição Físicas
    # Raio: metros / 
    # Massa: kg
    # Densidade kg/m³
    # ---------------------
    _mass: float = 1
    _density: float = 1
    _radius: float = field(init=False, default=0.0)
     
    # Propriedades Vetoriais
    # Posição: km
    # Velocidade: km/tick
    # ----------------------
    _position: glm.vec3 = field(init=False, default_factory=glm.vec3)
    _velocity: glm.vec3 = field(init=False, default_factory=glm.vec3)
    _scaled_position: glm.vec3 = field(init=False, default_factory=glm.vec3)
    _scaled_velocity: glm.vec3 = field(init=False, default_factory=glm.vec3)
    _focal_mass: float = field(init=False, default=0.0)
    _focal_pos: glm.vec3 = field(init=False, default_factory=glm.vec3)
    _focal_vel: glm.vec3 = field(init=False, default_factory=glm.vec3)
    
    # Elementos do Movimento Orbital
    # angular_L = Velocidade Angular em km²/tick
    # e = Excentricidade medida
    # ------------------------------------------    
    _host_body: Object = field(init=False, default=None)
    _grav_rel: list = field(init=False, default_factory=list)
    _rel: list = field(init=False, default_factory=list)
    _angular_momentum: glm.vec3 = field(init=False, default_factory=glm.vec3)
    e_vec3: glm.vec3 = field(init=False, default_factory=glm.vec3)
    has_bond: bool = field(init=False, default=False)
    
    # Sphere
    # ------
    sphere_values: int = field(init=False, default=0)
    qty_verts: int = field(init=False, default=0)
    VAO: int = field(init=False, default=0)
    
    def __post_init__(self):
        
        self._position = self._init_position
        self._velocity = self._init_velocity
        self._scaled_position = self._position * c.SIMULATION_DISTANCE_SCALED
        self._scaled_velocity = self._velocity / c.SIMULATION_DISTANCE_SCALED
        
        self._host_body = None
        self._angular_momentum = glm.vec3(0.0, 0.0, 0.0)
        self.e_vec3 = self.calc_e_vec3()
        self.has_bond = self.get_bond_status(self.e_vec3)

        # Esfera
        # ------
        self.sphere_values = self.sphere()
        self.VAO = self.sphere_values[0]
        self.qty_verts = self.sphere_values[1]
    
    def __hash__ (self):
        return hash(self.name)
    
    def convert_tuple_vec(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            return glm.vec3(*result)
        return wrapper
    
    @property
    @convert_tuple_vec
    def init_position(self):
        return self._init_position 
    
    @property
    @convert_tuple_vec
    def init_velocity(self):
        return self._init_velocity 
    
    @property
    @convert_tuple_vec
    def position(self):
        return self._position 
    
    @property
    @convert_tuple_vec
    def velocity(self):
        return self._velocity 
    
    @property
    @convert_tuple_vec
    def scaled_position(self):
        return self._scaled_position 
    
    @property
    @convert_tuple_vec
    def scaled_velocity(self):
        return self._scaled_velocity
    
    @property
    @convert_tuple_vec
    def color(self):
        return self._color
    
    @property
    def mass(self):
        return self._mass
    
    @property
    def density(self):
        return self._density
    
    @property
    def rel(self):
        return self._rel
    
    @property
    def radius(self):
        self._radius = math.cbrt(3 * self.mass / (4 * math.pi * self.density)) / c.RADII_SCALE
        return self._radius

    @property
    def glow(self):
        return self._glow
    
    @property   
    def angular_momentum(self):
        return self._angular_momentum
    
    @property
    def grav_rel(self):
        return self._grav_rel
    
    @property
    def host_body(self):
        return self._host_body
    
    @property
    def focal_pos(self):
        return self._focal_pos
    
    @property
    def focal_vel(self):
        return self._focal_vel
    
    @property
    def focal_mass(self):
        return self._focal_mass
    
    @focal_pos.setter
    def focal_pos(self, value):
        self._focal_pos = value
        
    @focal_vel.setter
    def focal_vel(self, value):
        self._focal_vel = value
    
    @focal_mass.setter
    def focal_mass(self, value):
        self._focal_mass = value
    
    @position.setter
    def position(self, value):
        self._position = value
        
    @scaled_position.setter
    def scaled_position(self, value):
        self._scaled_position = value
    
    @velocity.setter
    def velocity(self, value):
        self._velocity = value

    @scaled_velocity.setter
    def scaled_velocity(self, value):
        self._scaled_velocity = value
        
    @host_body.setter
    def host_body(self, value):
        self._host_body = value
    
    @grav_rel.setter
    def grav_rel(self, value):
        self._grav_rel = value
    
    @angular_momentum.setter
    def angular_momentum(self, value):
        self._angular_momentum = value
    
    def read_asdict(self):
        print(asdict(self))
    
    def sphere(self):
        verts = []
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
                verts.extend([
                    v1.x, v1.y, v1.z, self.color.x, self.color.y, self.color.z, n1.x, n1.y, n1.z
                    ])
                verts.extend([
                    v2.x, v2.y, v2.z, self.color.x, self.color.y, self.color.z, n2.x, n2.y, n2.z
                    ])
                verts.extend([
                    v3.x, v3.y, v3.z, self.color.x, self.color.y, self.color.z, n3.x, n3.y, n3.z
                    ])

                # triangulo 2
                verts.extend([
                    v2.x, v2.y, v2.z, self.color.x, self.color.y, self.color.z, n2.x, n2.y, n2.z
                    ])
                verts.extend([
                    v4.x, v4.y, v4.z, self.color.x, self.color.y, self.color.z, n4.x, n4.y, n4.z
                    ])
                verts.extend([
                    v3.x, v3.y, v3.z, self.color.x, self.color.y, self.color.z, n3.x, n3.y, n3.z
                    ])

        qty_verts = len(verts) // 9
        verts = np.array(verts,             # 32 bits
                                 dtype=np.float32)
        # Criar VAO
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)

        # Inicializa VBO
        VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, VBO)
        glBufferData(GL_ARRAY_BUFFER,
                     verts.nbytes,
                     verts,
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
        
        return VAO, qty_verts

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
        self.position += (self.velocity * dt) / c.SIMULATION_DISTANCE_SCALED

    def update_position_scaled(self):
        """
        Incrementa o vetor de posição a partir da derivada do vetor de velocidade.
        """
        self.scaled_position = self.position * c.SIMULATION_DISTANCE_SCALED

    def update_velocity_scaled(self):
        """
        Escala o vetor de velocidade 
        """
        self.scaled_velocity = self.velocity / c.SIMULATION_DISTANCE_SCALED
    
    def accelerate(self, acc, dt):
        """
        Incrementa o vetor de velocidade a partir do vetor de aceleração da gravidade.
        """
        self.velocity += (acc * dt)

    def check_collision(self, other):
        """
        Reduz a velocidade a partir da verificação da
        posição relativa dos dois corpos em diferença a soma dos raios.
        """
        
        distance = glm.distance(other.position, self.position)
        
        if (other.radius + self._radius) > distance:
            return -0.2
        return 1

    def calc_angular_L_vec3(self, position_other, velocity_other):
        """
        Retorna L vetorial = r vetorial * v vetorial
        """
        distance = (self.position - position_other) * c.SIMULATION_DISTANCE_SCALED
        velocity = self.velocity - velocity_other
        result = glm.cross(distance, velocity)
        self.angular_momentum = result
        return result
    
    def calc_gravitational_parameter(self, M):
        """
        Retorna (U) = Constante G * (Corpo Primário + Satélite) (m³/s) => Convertido para (km³/s)
        """
        return (c.G * (M + self.mass)) / c.SCALE_KM2

    def calc_velocity_vec(self, v2):
        """
        Retorna a velocidade relativa (v) do vetor velocidade ao corpo primário
        """
        return self.velocity - v2
    
    def calc_normal_pos(self, position_other):
        """
        Retorna o versor da posição relativa n(pos) do vetor posição ao corpo primário
        """
        result = self.position - position_other
        return glm.normalize(result)

    def calc_rel_pos(self):
        """
        Retorna o corpo primário com a maior Força Gravitacional
        """
        if self.host_body:
            return self.host_body.position

    def calc_e_vec3(self):
        """
        Retorna excentricidade(e) = vetor (v) * vetor (L) / (U) - (n pos)
        """
        if self.host_body:

            host_mass = self.focal_mass
            position_2 = self.focal_pos
            velocity_2 = self.focal_vel

            v_vector = self.calc_velocity_vec(velocity_2)
            angular_L = self.calc_angular_L_vec3(position_2, velocity_2)
            n_pos = self.calc_normal_pos(position_2)
            u_parameter = self.calc_gravitational_parameter(host_mass)

            e_vec3_vector = glm.cross(v_vector, angular_L) / u_parameter - n_pos
            return e_vec3_vector
        return

    def get_semi_major_axis(self):
        """
        Retorna o semi-eixo maior sendo (a) = -(U) / 2 * Energia Específica(ee)
        """
        if self.host_body:
            # main_body = self.host_body

            main_mass = self.focal_mass
            r = (glm.length(self._position - self.focal_pos)) * c.SIMULATION_DISTANCE_SCALED
            v2 = glm.length(self._velocity - self.focal_vel)
            u_parameter = self.calc_gravitational_parameter(main_mass)

            specific_energy = math.pow(v2, 2)/2 - u_parameter/r
            semi_axis = -u_parameter / (2 * specific_energy)

            return semi_axis
        return

    def get_bond_status(self, e):
        if e is not None and self.host_body is not None:
            e = glm.length(e)
            if self.get_semi_major_axis() > 0 and ( 0 <= e < 1):
                return True
        return False

    def chain_function(self, orbits):
        self.rel_pos = self.calc_rel_pos()

        # de alguma forma calcular focal
        
        self.e_vec3 = self.calc_e_vec3()
        self.has_bond = self.get_bond_status(self.e_vec3)

        if self.has_bond and not orbits:
            orbital_object = Orbit(self)
            orbits.append(orbital_object)

        elif self.has_bond and orbits:
            is_registered = False

            for i in range(len(orbits)):
                if orbits[i]._object_name == self.name:
                    orbits[i].update_orbit()
                    is_registered = True

            if not is_registered:
                orbital_object = Orbit(self)
                orbits.append(orbital_object)


@dataclass
class Orbit:
        
        """
        Projeta uma elipse correspondente a órbita ligada de Kepler, a partir do corpo primário.
        """
        
        size: ClassVar[int] = 500
        
        _sel_object: Object
        _color: tuple = (1.0, 1.0, 1.0)
        
        _object_name: str = field(init=False,                   default_factory=str)
        _object_radius: float = field(init=False,               default_factory=float)
        _object_semi_major_axis: float = field(init=False,      default_factory=float)
        
        _object_position: glm.vec3 = field(init=False,          default_factory=glm.vec3) 
        _object_angular_momentum: glm.vec3 = field(init=False,  default_factory=glm.vec3)
        _object_n_angular_momentum: glm.vec3 = field(init=False,default_factory=glm.vec3)
        _object_epsilon: glm.vec3 = field(init=False,           default_factory=glm.vec3)
        _object_L_epsilon: float = field(init=False,            default=0)
        _object_n_epsilon: glm.vec3 = field(init=False,         default_factory=glm.vec3)
        _object_transversal: glm.vec3 = field(init=False,       default_factory=glm.vec3)
        
        _object_host: Object = field(init=False,        default=None)
        _object_host_radius: float = field(init=False,  default_factory=float)
        
        _trajectory_offset: glm.vec3 = field(init=False,        default_factory=glm.vec3)
        _draw_array: bool = field(init=False,       default_factory=bool)
        
        _trajectory_value: tuple = field(init=False,  default=tuple)
        qty_verts: int = field(init=False,          default=0)
        verts: int = field(init=False,              default=0)
        VAO: int = field(init=False,                default=0)
        VBO: int = field(init=False,                default=0)

        # debugging
        draw_text: str = field(init=False,          default=str)
        
        def __post_init__(self):
            
            self._color = (r.uniform(0, 1),
                           r.uniform(0, 1),
                           r.uniform(0, 1))
            
            self._draw_array = True
            # Parametros dos Corpos
            # ---------------------
            self._object_name = self._sel_object.name
            self._object_radius = self._sel_object.radius
            self._object_position = self._sel_object.position
            self._object_angular_momentum = self._sel_object.angular_momentum
            self._object_n_angular_momentum = glm.normalize(self._object_angular_momentum)
            
            # Elementos Orbitais
            # ------------------
            self._object_epsilon = self._sel_object.calc_e_vec3() 
            self._object_L_epsilon = glm.length(self._object_epsilon)
            self._object_n_epsilon = glm.normalize(self._object_epsilon)
            self._object_transversal = glm.cross(self._object_n_angular_momentum,
                                                self._object_n_epsilon)
            self._object_semi_major_axis = self._sel_object.get_semi_major_axis()
            
            # Host
            # ----
            self._object_host = self._sel_object.host_body
            self._object_host_radius = self._object_host.radius
            
            # Trajetória
            # ----------
            self._trajectory_value = self.create_orbit()
            self.VAO = self._trajectory_value[0]
            self.VBO = self._trajectory_value[1]
            self.qty_verts = self._trajectory_value[2]
        def __hash__(self):
            return hash(self._sel_object.name)
        
        @property
        def sel_object(self):
            return self._sel_object
        
        @property
        def draw_array(self):
            return self._draw_array
        
        @property
        def color(self):
            return self._color
        
        @property
        def object_angular_momentum(self):
            return self._object_angular_momentum
        
        @property
        def object_n_angular_momentum(self):
            return self._object_n_angular_momentum 
        
        @property
        def object_epsilon(self):
            return self._object_epsilon
        
        @property
        def object_L_epsilon(self):
            return self._object_L_epsilon

        @property
        def object_n_epsilon(self):
            return self._object_n_epsilon
        
        @property
        def object_position(self):
            return self._object_position

        @property
        def object_semi_major_axis(self):
            return self._object_semi_major_axis
        
        @property
        def object_host(self):
            return self._object_host
        
        @property
        def object_host_radius(self):
            return self._object_host_radius
        
        @property
        def object_host_radius(self):
            return self._object_host_radius
        
        @property
        def object_radius(self):
            return self._object_radius
        
        @property
        def object_transversal(self):
            return self._object_transversal
        
        @property
        def trajectory_offset(self):
            return self._trajectory_offset
        
        @trajectory_offset.setter
        def trajectory_offser(self, value):
            self._trajectory_offset = value
            
        @object_position.setter
        def object_position(self, value):
            self._object_position = value
        
        @object_angular_momentum.setter
        def object_angular_momentum(self, value):
            self._object_angular_momentum = value
        
        @object_n_angular_momentum.setter
        def object_n_angular_momentum(self, value):
            self._object_n_angular_momentum = value
        
        @object_semi_major_axis.setter
        def object_semi_major_axis(self, value):
            self._object_semi_major_axis = value
        
        @object_radius.setter
        def object_radius(self, value):
            self._object_radius = value
        
        @object_epsilon.setter
        def object_epsilon(self, value):
            self._object_epsilon = value
        
        @object_n_epsilon.setter
        def object_n_epsilon(self, value):
            self._object_n_epsilon = value
            
        @object_L_epsilon.setter
        def object_L_epsilon(self, value):
            self._object_L_epsilon = value
            
        @object_host_radius.setter
        def object_host_radius(self, value):
            self._object_host_radius = value
        
        @object_transversal.setter
        def object_transversal(self, value):
            self._object_transversal = value
        
        @draw_array.setter
        def draw_array(self, value):
            self._draw_array = value
        
        @object_host.setter
        def object_host(self, value):
            self._object_host = value
        
        def read_asdict(self):
            print(asdict(self))
        
        def draw(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                epsilon = self.object_L_epsilon
                axis = self.object_semi_major_axis
                host_r = self.object_host_radius
                obj_r = self.object_radius
                
                if not (axis > 0 and (0 <= epsilon < 1)):
                    self.draw_array = False
                    return np.empty((0, 6), dtype=np.float32), 0
                
                peri_r = (axis * (1.0 - epsilon)) / c.SIMULATION_DISTANCE_SCALED 
                if peri_r <= (host_r + obj_r):
                    self.draw_array = False
                    return np.empty((0, 6), dtype=np.float32), 0
                self.draw_array = True
                return func(self, *args, **kwargs)
            return wrapper
        
        def get_rad_dist(self, theta):
            """
            Retorna a distância radial (r) = a * (1 - e²) / (1 + e*cos(theta)) alinhada ao eixo transversal.
            """
            if self.object_semi_major_axis > 0 and ( 0 <= self.object_L_epsilon < 1):
                semi_major_axis = self.object_semi_major_axis
                transversal = self.object_transversal
                e_epsilon = self.object_L_epsilon
                n_epsilon = self.object_n_epsilon

                radial_distance = semi_major_axis * (1 - glm.pow(e_epsilon, 2)) / (1 + (e_epsilon * glm.cos(theta)))

                t_radial_distance = (radial_distance * glm.cos(theta) * n_epsilon
                                    + radial_distance * glm.sin(theta) * transversal)

                #print(e_epsilon)
                return t_radial_distance
            return glm.vec3(0.0, 0.0, 0.0)

        @draw
        def trajectory(self):
            verts = []
            delta_theta = (2 * math.pi) / self.size
            host = self.sel_object.host_body
            
            if isinstance(host, Barycenter) and self.sel_object in host.members:
                total_mass = host.mass
                companion_mass = total_mass - self.sel_object.mass
                orbit_scale = companion_mass / total_mass
                #print(f"{self.sel_object.name}",f"\n{self.sel_object.position}" ,f"\nis istance: {orbit_scale}", f"\n{center}")
            else:
                orbit_scale = 1.0
                #print(f"is istance else: {orbit_scale}")
                
            for i in range(self.size):
                theta = i * delta_theta
                trajectory_vert = ((self.get_rad_dist(theta) * orbit_scale) / c.SIMULATION_DISTANCE_SCALED) #+ self.sel_object.focal_pos
                verts.append([trajectory_vert.x,
                            trajectory_vert.y,
                            trajectory_vert.z,
                            self.color[0],
                            self.color[1],
                            self.color[2]])
            qty_verts = len(verts)
            verts = np.array(verts, 
                            dtype=np.float32)
            
            return verts, qty_verts

        def create_orbit(self):
            # verify
            trajectory = self.trajectory()
            
            verts = trajectory[0]
            qty_verts = trajectory[1]
            
            VAO = glGenVertexArrays(1)
            glBindVertexArray(VAO)

            VBO = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER,
                        VBO)
            glBufferData(GL_ARRAY_BUFFER,
                        verts.nbytes,
                        verts, 
                        GL_DYNAMIC_DRAW)

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

            return VAO, VBO, qty_verts
        
        def update_orbit(self):
            """
            Realiza uma atualização parcial dos atributos do Vertex no Buffer Object (VBO).
            """
            self.object_position = self.sel_object.position # focal pos
            self.object_radius = self._sel_object.radius
            self.object_angular_momentum = self.sel_object.angular_momentum
            self.object_n_angular_momentum = glm.normalize(self.object_angular_momentum)
            self.object_semi_major_axis = self.sel_object.get_semi_major_axis() 
            self.object_epsilon = self._sel_object.e_vec3
            self.object_L_epsilon = glm.length(self.object_epsilon)
            self.object_n_epsilon = glm.normalize(self.object_epsilon)
            self.object_transversal = glm.cross(self.object_n_angular_momentum,
                                                self.object_n_epsilon)
            
            self.object_host = self.sel_object.host_body
            self.object_host_radius = self.object_host.radius
            
            self._trajectory_value = self.trajectory()
            self.verts = self._trajectory_value[0]
            self.qty_verts = self._trajectory_value[1]
            
            if not self.draw_array or self.qty_verts == 0:
                return
            
            glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
            glBufferSubData(GL_ARRAY_BUFFER, 0, self.verts.nbytes, self.verts)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

        def render(self, shaderId):
            """
            Vincula o nome do Vertex Array Object gerado em glGenVertexArrays
            para encapsular o VBO, descrição dos vértices e estado de ativação dos
            atributos, para assim sequenciar a construção dos primitivos em DrawArray.
            """
            if self.draw_array and self.qty_verts > 0:
                glBindVertexArray(self.VAO)
                glDrawArrays(GL_LINE_LOOP, 0, self.qty_verts)
                glBindVertexArray(0)
 
        
@dataclass
class Barycenter:
    name: str
    members: list
    mass: float = 1.0
    host: Object = False
    
    radius: float = 0.0
    _position: glm.vec3 = field(init=False, default_factory=glm.vec3)
    _velocity: glm.vec3 = field(init=False, default_factory=glm.vec3)
    
    @property
    def position(self): return self._position
    
    @property
    def velocity(self): return self._velocity
    
    @velocity.setter
    def velocity(self, v): self._velocity = v
    
    @position.setter
    def position(self, v): self._position = v
        
    def __hash__(self):
        return hash(self.name)    
    
    def update(self):
        barycenter_mass = sum(m.mass for m in self.members)
        
        focal_point_x = 0
        focal_point_y = 0
        focal_point_z = 0
        
        focal_vel_x = 0
        focal_vel_y = 0
        focal_vel_z = 0
        
        for orb in self.members:
            
            focal_point_x += orb.position.x * orb.mass
            focal_point_y += orb.position.y * orb.mass
            focal_point_z += orb.position.z * orb.mass
            
            focal_vel_x += orb.velocity.x * orb.mass
            focal_vel_y += orb.velocity.y * orb.mass
            focal_vel_z += orb.velocity.z * orb.mass

        result_pos_x = focal_point_x / barycenter_mass
        result_pos_y = focal_point_y / barycenter_mass
        result_pos_z = focal_point_z / barycenter_mass
        
        result_vel_x = focal_vel_x / barycenter_mass
        result_vel_y = focal_vel_y / barycenter_mass
        result_vel_z = focal_vel_z / barycenter_mass
        
        self._position = glm.vec3(result_pos_x,
                              result_pos_y,
                              result_pos_z)
        
        self._velocity = glm.vec3(result_vel_x,
                              result_vel_y,
                              result_vel_z)
        
        self.mass = barycenter_mass
 
        
def define_primary(body_a, body_b):
        dist = glm.length(body_a.position - body_b.position) * c.SIMULATION_DISTANCE_SCALED
        if dist <= 0:
            return 0
        return body_b.mass / math.pow(dist, 2)
    
def is_binary(binary_a, binary_b):
        if binary_a.mass <= 0 or binary_b.mass <=0:
            return False
        
        satellite = binary_a if binary_a.mass < binary_b.mass else binary_b      
        primary = binary_a if binary_a.mass >= binary_b.mass else binary_b
        
        mass_ratio = satellite.mass / primary.mass
        if mass_ratio < 0.1:
            return False

        binary_group = [satellite, primary]
        
        binary_mass = sum(m.mass for m in binary_group)
        
        focal_point_x = 0
        focal_point_y = 0
        focal_point_z = 0
        
        for orb in binary_group:
            
            focal_point_x += orb.position.x * orb.mass
            focal_point_y += orb.position.y * orb.mass
            focal_point_z += orb.position.z * orb.mass
            
        result_pos_x = focal_point_x / binary_mass
        result_pos_y = focal_point_y / binary_mass
        result_pos_z = focal_point_z / binary_mass
        
        position = glm.vec3(result_pos_x,
                              result_pos_y,
                              result_pos_z)
        
        dist_primary = glm.length(position - primary.position) * c.SIMULATION_DISTANCE_SCALED
        primary_radius = primary.radius * c.RADII_SCALE / 1000
        
        return dist_primary > primary_radius

def hierarchy(bodies: list) -> dict:

        node = list(bodies)
        hierarchy = {b: None for b in node}
        barycenter = []
        assigned = set()
        
        sorted_node = sorted(node, key=lambda b: b.mass, reverse=True)
        
        for i, body in enumerate(sorted_node):
            if body in assigned:
                continue
            for j in range(i + 1, len(sorted_node)):
                candidate = sorted_node[j]
                if candidate in assigned:
                    continue
                if is_binary(body, candidate):
                    if define_dominance(body, candidate, bodies):
                        continue
                    bc = Barycenter(
                        name=f"BC_{body.name}_{candidate.name}",
                        members=[body, candidate]
                    )
                    
                    bc.update()
                    
                    barycenter.append(bc)
                    hierarchy[body] = bc
                    hierarchy[candidate] = bc
                    hierarchy[bc] = None
                    
                    assigned.add(body)
                    assigned.add(candidate)
                    node.append(bc)
                    break
                
        all_node = sorted(node, key=lambda b: b.mass, reverse=True)
        
        for body in all_node:
            if hierarchy.get(body):
                continue
            
            if not body.rel if hasattr(body, 'rel') else False:
                continue
            
            primary_host = None
            primary_host_f = 0.0
            
            candidates = [n for n in all_node if n is not body and n.mass > body.mass]
            
            for candidate in candidates:
                primary_host_candidate = hierarchy.get(candidate)
                if primary_host_candidate and define_hill_zone(body, candidate, primary_host_candidate):
                    dom = define_primary(body, candidate)
                    if dom > primary_host_f: 
                        primary_host_f = dom
                        primary_host = candidate
            
            if primary_host is None and candidates:
                primary_host = max(candidates,
                                   key=lambda c: define_primary(body, c))
                
            hierarchy[body] = primary_host
        # print(f"H: {hierarchy}\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n B: {barycenter}\n")
        return hierarchy, barycenter
    
def update_focal_point(hierarchy: dict, barycenter: list):
        for bc in barycenter:
            bc.update()
        
        for body, host in hierarchy.items():
            if host is None:
                continue
            if not hasattr(body, 'focal_pos'):
                continue
            
            if isinstance(host, Barycenter):
                if body in host.members: 
                    other = next(m for m in host.members if m is not body)
                    body.focal_pos = other.position
                    body.focal_vel = other.velocity
                    body.focal_mass = other.mass
                else: 
                    body.focal_pos  = host.position 
                    body.focal_vel  = host.velocity
                    body.focal_mass = host.mass
            else: 
                body.focal_pos  = host.position 
                body.focal_vel  = host.velocity
                body.focal_mass = host.mass
    # W.I.P

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

def define_hill_zone(current_body, parent_body, host_body):
    if parent_body and host_body:
        current_body_dist = glm.length(current_body.position - parent_body.position) * c.SIMULATION_DISTANCE_SCALED
        parent_body_dist = glm.length(parent_body.position - host_body.position) * c.SIMULATION_DISTANCE_SCALED

        hill_zone = parent_body_dist * math.cbrt(parent_body.mass / (3 * host_body.mass))

        if hill_zone > current_body_dist:
            return True
        return False

def define_dominance(body_a, body_b, body_list):
    dist = glm.length(body_a.position - body_b.position) * c.SIMULATION_DISTANCE_SCALED
    if dist <= 0:
        return True

    mutual_acc = (body_a.mass + body_b.mass) / math.pow(dist, 2)
    
    binary_group = [body_a, body_b]
    binary_mass = sum(m.mass for m in binary_group)
    
    focal_point_x = 0
    focal_point_y = 0
    focal_point_z = 0
    
    for orb in binary_group:
            
        focal_point_x += orb.position.x * orb.mass
        focal_point_y += orb.position.y * orb.mass
        focal_point_z += orb.position.z * orb.mass
            
    result_pos_x = focal_point_x / binary_mass
    result_pos_y = focal_point_y / binary_mass
    result_pos_z = focal_point_z / binary_mass
        
    position = glm.vec3(result_pos_x,
                            result_pos_y,
                            result_pos_z)
    
    max_mass = max(body_a.mass, body_b.mass)
    for other in body_list:
        if other is body_a or other is body_b:
            continue
        if other.mass <= max_mass:
            continue
        dist_other = glm.length(position - other.position) * c.SIMULATION_DISTANCE_SCALED
        if dist_other <= 0:
            continue
        acc_other = other.mass / math.pow(dist_other, 2)
        if acc_other > mutual_acc:
            return True
    return False
        