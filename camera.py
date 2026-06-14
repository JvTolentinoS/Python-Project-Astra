import math
import glm
from OpenGL.GLUT import *  
import constants as c


class Camera:
        
        
        current_speed = 0.0
        
        def __init__(self,
                    WIDTH,
                    HEIGHT,
                    camera_pos = glm.vec3(0.0, 0.0, 0.0),   
                    camera_front = glm.vec3(0.0, 0.0, -1.0), 
                    camera_up = glm.vec3(0.0, 1.0, 0.0),     
                    camera_right = glm.vec3(1.0, 0.0, 0.0),  
                    yaw = -90.0,                            # horizonte de rotação                       
                    pitch = 0.0,                            # perpendicular de rotação 
                    movement_speed = 500):                                           
            
            self.camera_pos = camera_pos
            self.camera_front = camera_front
            self.camera_up = camera_up
            self.camera_right = camera_right
            self.yaw = yaw
            self.pitch = pitch
            self.mouse_sensitivity = 0.1
            self.movement_speed = movement_speed
            
            # controle de mouse
            self.first_mouse = True
            self.ignore_warp_event = False
            self.last_x = None
            self.last_y = None
            
            # direção de movimento do teclado
            self.foward = False 
            self.backward = False
            self.left = False 
            self.right = False 
            self.up = False
            self.down = False

            # para simulação
            self.objs_list = []
            self.pause = False
            self.current_speed = 0
            self.selector = False
            self.target_pointer = 0

            # Tela
            self.WIDTH = WIDTH
            self.HEIGHT = HEIGHT

            # Projeção
            self.far = 3000000
            self.near = 100.0

        def get_view_matrix(self):
            view = glm.lookAt(self.camera_pos, 
                              self.camera_pos 
                              + self.camera_front,
                              self.camera_up)
            return view

        def process_mouse_movement(self, 
                                 xoffset, 
                                 yoffset, 
                                 constrain_pitch = True):
            xoffset *= self.mouse_sensitivity
            yoffset *= self.mouse_sensitivity

            self.yaw += xoffset
            self.pitch += yoffset

            if constrain_pitch:
                if self.pitch > 45.0:
                    self.pitch = 45.0
                if self.pitch < -45.0:
                    self.pitch = -45.0

            self.update_camera_vectors()

        def update_camera_vectors(self):
            front = glm.vec3()
            vec3y = glm.vec3(0.0, 1.0, 0.0)  # workaround para reduzir verbosidade do glm

            front.x = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
            front.y = math.sin(glm.radians(self.pitch))
            front.z = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
            
            self.camera_front = glm.normalize(front)
            self.camera_right = glm.normalize(glm.cross(self.camera_front, vec3y))
            self.camera_up = glm.normalize(glm.cross(self.camera_right, self.camera_front))
        
        def process_keyboard(self, direction, deltaTime = 1):
            velocity = self.movement_speed * deltaTime
            if direction == "FOWARD":
                self.camera_pos += self.camera_front * velocity
            if direction == "BACKWARD":
                self.camera_pos -= self.camera_front * velocity
            if direction == "LEFT":
                self.camera_pos -= self.camera_right * velocity
            if direction == "RIGHT":
                self.camera_pos += self.camera_right * velocity
            if direction == "UP":
                self.camera_pos += self.camera_up * velocity
            if direction == "DOWN":
                self.camera_pos -= self.camera_up * velocity

        # Mouse Input/Tracking
        def mouse_look_callback(self, xpos, ypos):

            HEIGHT_MIDDLE_POINT, WIDTH_MIDDLE_POINT = int(self.HEIGHT / 2), int(self.WIDTH / 2)

            if self.ignore_warp_event:
                self.ignore_warp_event = False
                return

            if self.first_mouse:
                self.last_x = xpos
                self.last_y = ypos
                self.first_mouse = False

            xoffset = xpos - self.last_x
            yoffset = self.last_y - ypos

            self.process_mouse_movement(xoffset, yoffset)

            self.last_x = WIDTH_MIDDLE_POINT
            self.last_y = HEIGHT_MIDDLE_POINT
            self.ignore_warp_event = True
            glutWarpPointer(WIDTH_MIDDLE_POINT, HEIGHT_MIDDLE_POINT)

        # Key Down
        def key_down_callback(self, key, x, y):

            if key == b"w" or key == b'W':
                self.foward = True
            if key == b"s" or key == b'S':
                self.backward = True
            if key == b"d" or key == b'D':
                self.right = True
            if key == b"a" or key == b'A':
                self.left = True
            if key == b"q" or key == b'Q':
                self.up = True
            if key == b"e" or key == b'E':
                self.down = True
            if key == b"p" or key == b'P':
                if not self.pause:
                    self.pause = True
                    print("Pausado")
                else: 
                    self.pause = False
                    print("Despausado") 
            if key == b"+":
                if self.movement_speed < 900:
                    self.movement_speed += 50 
            if key == b"-":
                if self.movement_speed > 50:
                    self.movement_speed -= 50
            if key == b"o" or key == b"O": # selector
                if self.target_pointer < len(self.objs_list):
                    self.selector = True
                    self.select_target(self.objs_list)
                    self.target_pointer += 1
                else:
                    self.target_pointer = 0

        # Key Release
        
        # Key Up
        def key_up_callback(self, key, x, y):

            if key == b"w" or key == b'W':
                self.foward = False
            if key == b"s" or key == b'S':
                self.backward = False
            if key == b"d" or key == b'D':
                self.right = False
            if key == b"a" or key == b'A':
                self.left = False
            if key == b"q" or key == b'Q':
                self.up = False
            if key == b"e" or key == b'E':
                self.down = False

        # Movimento de Teclado 
        def do_movement(self):
            if self.foward:
                self.process_keyboard("FOWARD")
            if self.backward:
                self.process_keyboard("BACKWARD")
            if self.right:
                self.process_keyboard("RIGHT")
            if self.left:
                self.process_keyboard("LEFT")
            if self.up:
                self.process_keyboard("UP")
            if self.down:
                self.process_keyboard("DOWN")

        # Selector
        def select_target(self, objs = list):
            if self.selector:
                object_position = objs[self.target_pointer].position
                object_radius = objs[self.target_pointer].radius
                x = object_position[0]  
                y = object_position[1]
                z = object_position[2] + 4*object_radius
                
                self.camera_pos = glm.vec3(x, y, z)
                print(objs[self.target_pointer].read_asdict)
                #   print(f"\n# Nome: {objs[self.target_pointer].name} \n" + f"# Massa: {objs[self.target_pointer].mass} kg \n" + f"# Raio: {int(objs[self.target_pointer].radius * (c.RADII_SCALE)/1000)} km")
                
        def get_projection(self):
            return glm.perspective(glm.radians(45.0), 
                                   self.WIDTH / self.HEIGHT, 
                                   self.near, self.far)
            