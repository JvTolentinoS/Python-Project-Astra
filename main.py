import math
import numpy as np                                                              # pip install numpy
import os
import glm                                                                      # pip install PyGLM
from circle import *
from OpenGL.GL import *                                                         # pip install PyOpenGL PyOpenGL_accelerate                                                
from OpenGL.GLU import *                                                         
from OpenGL.GLUT import *                                                       
from shader import Shader
from camera import Camera

camera = Camera()
WIDTH, HEIGHT = 1280, 720
HEIGHT_MIDDLE_POINT, WIDTH_MIDDLE_POINT = int(HEIGHT / 2), int(WIDTH / 2)
lastX, lastY = WIDTH / 2, HEIGHT / 2
firstMouse = True
ignore_warp_event = False
foward, backward, left, right, up, down = False, False, False, False, False, False,  


obj = None
myShader = None

# Pre rendering settings
def init(): 
    global obj, myShader
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Project Astra")
    glEnable(GL_DEPTH_TEST)
    glutSetCursor(GLUT_CURSOR_NONE)
    obj = Sphere() 
    glClearColor(0.0, 0.0, 0.0, 1.0)                                           
    here = os.path.dirname(os.path.abspath(__file__))                           
    myShader = Shader(os.path.join(here, "0_vertexShader.glsl"), 
                      os.path.join(here, "0_fragmentShader.glsl"))

    projection = glm.perspective(glm.radians(45.0), WIDTH / HEIGHT, 0.1, 100.0) 

    myShader.bind()
    myShader.setUniformMat4("projection", projection)
    myShader.setUniformMat4("model", glm.mat4(1.0))
    myShader.unbind()

# render function for screen space
def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    myShader.bind()
    view = getViewMatrix()
    myShader.setUniformMat4("view", view)
    obj.render(myShader.shaderId)
    myShader.unbind()
    glutSwapBuffers()

# View Matrix for camera rendering
def getViewMatrix():
    return camera.getViewMatrix()

# Mouse Input/Tracking
def mouseLookCallback(xpos, ypos):
    global lastX, lastY, firstMouse, ignore_warp_event

    if ignore_warp_event:
        ignore_warp_event = False
        lastX = WIDTH_MIDDLE_POINT
        lastY = HEIGHT_MIDDLE_POINT
        return

    if firstMouse:
        lastX = xpos
        lastY = ypos
        firstMouse = False

    xoffset = xpos - lastX
    yoffset = lastY - ypos

    camera.processMouseMovement(xoffset, yoffset)

    lastX = WIDTH_MIDDLE_POINT
    lastY = HEIGHT_MIDDLE_POINT
    ignore_warp_event = True
    glutWarpPointer(WIDTH_MIDDLE_POINT, HEIGHT_MIDDLE_POINT)

# Key Down
def keyDownCallback(key, x, y):
    global foward, backward, left, right, up, down

    if key == b"w":
        foward = True
    if key == b"s":
        backward = True
    if key == b"d":
        right = True
    if key == b"a":
        left = True
    if key == b"q":
        up = True
    if key == b"e":
        down = True

# Key Release
def keyUpCallback(key, x, y):
    global foward, backward, left, right, up, down

    if key == b"w":
        foward = False
    if key == b"s":
        backward = False
    if key == b"d":
        right = False
    if key == b"a":
        left = False
    if key == b"q":
        up = False
    if key == b"e":
        down = False

# WASD horizontal axis and QE for up/down 
def doMovement():
    if foward:
        camera.processKeyboard("FOWARD")
    if backward:
        camera.processKeyboard("BACKWARD")
    if right:
        camera.processKeyboard("RIGHT")
    if left:
        camera.processKeyboard("LEFT")
    if up:
        camera.processKeyboard("UP")
    if down:
        camera.processKeyboard("DOWN")

def reshape(width, height):
    glViewport(0, 0, width, height)
    projection = glm.perspective(glm.radians(45.0), width / height, 0.1, 100.0)
    myShader.bind()
    myShader.setUniformMat4("projection", projection)
    myShader.unbind()   
    
def idle():
    doMovement()                                                                     # REVISAR
    glutPostRedisplay()                                                         
    
def main():
    glutInit()
    init()
    glutReshapeFunc(reshape)
    glutIdleFunc(idle)
    glutPassiveMotionFunc(mouseLookCallback)
    glutKeyboardFunc(keyDownCallback)
    glutKeyboardUpFunc(keyUpCallback)
    glutDisplayFunc(render)
    glutMainLoop()

if __name__ == "__main__":
    main()

