import math
import glm
from OpenGL.GLUT import *  

class Camera:
        def __init__(self,
                    WIDTH,
                    HEIGHT,
                    cameraPos = glm.vec3(0.0, 0.0, 2000),    # posição inicial
                    cameraFront = glm.vec3(0.0, 0.0, -1.0), # aonde a camera está olhando
                    cameraUp = glm.vec3(0.0, 1.0, 0.0),     # direção para cima da camera
                    cameraRight = glm.vec3(1.0, 0.0, 0.0),  # direção lateral
                    yaw = -90.0,                            # horizonte de rotação                       
                    pitch = 0.0,                            # perpendicular de rotação 
                    movementSpeed = 100):                 # velocidade do passo                         

            self.cameraPos = cameraPos
            self.cameraFront = cameraFront
            self.cameraUp = cameraUp
            self.cameraRight = cameraRight
            self.yaw = yaw
            self.pitch = pitch
            self.mouseSensitivity = 0.1
            self.movementSpeed = movementSpeed

            # controle de mouse
            self.firstMouse = True
            self.ignore_warp_event = False
            self.lastX = None
            self.lastY = None
            
            # direção de movimento do teclado
            self.foward = False 
            self.backward = False
            self.left = False 
            self.right = False 
            self.up = False
            self.down = False

            # para simulação
            self.pause = False
            self.simulationSpeed = 1

            # Tela
            self.WIDTH = WIDTH
            self.HEIGHT = HEIGHT

        def getViewMatrix(self):
            view = glm.lookAt(self.cameraPos, 
                              self.cameraPos + 
                              self.cameraFront, 
                              self.cameraUp)
            return view

        def processMouseMovement(self, 
                                   xoffset, 
                                   yoffset, 
                                   constrain_pitch = True):
            xoffset *= self.mouseSensitivity
            yoffset *= self.mouseSensitivity

            self.yaw += xoffset
            self.pitch += yoffset

            if constrain_pitch:
                if self.pitch > 45.0:
                    self.pitch = 45.0
                if self.pitch < -45.0:
                    self.pitch = -45.0

            self.updateCameraVectors()

        def updateCameraVectors(self):
            front = glm.vec3()
            front.x = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
            front.y = math.sin(glm.radians(self.pitch))
            front.z = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
            
            self.cameraFront = glm.normalize(front)
            self.cameraRight = glm.normalize(glm.cross(self.cameraFront, glm.vec3(0.0, 1.0, 0.0)))
            self.cameraUp = glm.normalize(glm.cross(self.cameraRight, self.cameraFront))
        
        def processKeyboard(self, direction, deltaTime = 1):
            velocity = self.movementSpeed * deltaTime
            if direction == "FOWARD":
                self.cameraPos += self.cameraFront * velocity
            if direction == "BACKWARD":
                self.cameraPos -= self.cameraFront * velocity
            if direction == "LEFT":
                self.cameraPos -= self.cameraRight * velocity
            if direction == "RIGHT":
                self.cameraPos += self.cameraRight * velocity
            if direction == "UP":
                self.cameraPos += self.cameraUp * velocity
            if direction == "DOWN":
                self.cameraPos -= self.cameraUp * velocity

                # Mouse Input/Tracking
        
        def mouseLookCallback(self, xpos, ypos):

            HEIGHT_MIDDLE_POINT, WIDTH_MIDDLE_POINT = int(self.HEIGHT / 2), int(self.WIDTH / 2)

            if self.ignore_warp_event:
                self.ignore_warp_event = False
                self.lastX = WIDTH_MIDDLE_POINT
                self.lastY = HEIGHT_MIDDLE_POINT
                return

            if self.firstMouse:
                self.lastX = xpos
                self.lastY = ypos
                self.firstMouse = False

            xoffset = xpos - self.lastX
            yoffset = self.lastY - ypos

            self.processMouseMovement(xoffset, yoffset)

            self.lastX = WIDTH_MIDDLE_POINT
            self.lastY = HEIGHT_MIDDLE_POINT
            self.ignore_warp_event = True
            glutWarpPointer(WIDTH_MIDDLE_POINT, HEIGHT_MIDDLE_POINT)

        # Key Down
        def keyDownCallback(self, key, x, y):

            if key == b"w":
                self.foward = True
            if key == b"s":
                self.backward = True
            if key == b"d":
                self.right = True
            if key == b"a":
                self.left = True
            if key == b"q":
                self.up = True
            if key == b"e":
                self.down = True
            if key == b"p":
                if self.pause == False:
                    self.pause = True
                else: 
                    self.pause = False 
            if key == b"+":
                if self.simulationSpeed == 0.5:
                    self.simulationSpeed += 0.5
                else:
                    self.simulationSpeed += 1
            if key == b"-":
                if self.simulationSpeed >= 1:
                    self.simulationSpeed -= 0.5
                else:
                    self.simulationSpeed -= 0
        # Key Release
        def keyUpCallback(self, key, x, y):

            if key == b"w":
                self.foward = False
            if key == b"s":
                self.backward = False
            if key == b"d":
                self.right = False
            if key == b"a":
                self.left = False
            if key == b"q":
                self.up = False
            if key == b"e":
                self.down = False

        # Movimento de Teclado 
        def doMovement(self):
            if self.foward:
                self.processKeyboard("FOWARD")
            if self.backward:
                self.processKeyboard("BACKWARD")
            if self.right:
                self.processKeyboard("RIGHT")
            if self.left:
                self.processKeyboard("LEFT")
            if self.up:
                self.processKeyboard("UP")
            if self.down:
                self.processKeyboard("DOWN")
