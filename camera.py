import math
import glm

class Camera:
        def __init__(self,
                    cameraPos = glm.vec3(0.0, 0.0, 1.0),    # posição inicial
                    cameraFront = glm.vec3(0.0, 0.0, -1.0), # aonde a camera está olhando
                    cameraUp = glm.vec3(0.0, 1.0, 0.0),     # direção para cima da camera
                    cameraRight = glm.vec3(1.0, 0.0, 0.0),  # direção lateral
                    yaw = -90.0,                            # horizonte de rotação                       
                    pitch = 0.0,                            # perpendicular de rotação 
                    movementSpeed = 0.05):                     # velocidade do passo    

            self.cameraPos = cameraPos
            self.cameraFront = cameraFront
            self.cameraUp = cameraUp
            self.cameraRight = cameraRight
            self.yaw = yaw
            self.pitch = pitch
            self.mouseSensitivity = 0.1
            self.movementSpeed = movementSpeed
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
