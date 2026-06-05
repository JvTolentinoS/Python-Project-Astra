                                                
import math
import os
import glm                                                                      # pip install PyGLM
from objects import Object
from objects import Background
from OpenGL.GL import *                                                         # pip install PyOpenGL PyOpenGL_accelerate                                                
from OpenGL.GLU import *                                                         
from OpenGL.GLUT import *                                                       
from shader import Shader
from camera import Camera


# Constantes Globais
WIDTH, HEIGHT = 1280, 720
lastFrame = 0.0
deltaTime = 0.0

# Objetos Globais
camera = Camera(WIDTH=1280, HEIGHT=720)
myShader = None
bdg_obj = None
objs = []

# Configurações Iniciais
def init(): 
    global myShader, myBgdShader, objs, bdg_obj
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutSetOption(GLUT_MULTISAMPLE, 8)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Project Astra")
    glEnable(GL_DEPTH_TEST)
    glutSetCursor(GLUT_CURSOR_NONE)
    glClearColor(0.0, 0.0, 0.0, 1.0)
                                           
    here = os.path.dirname(os.path.abspath(__file__))                           
    myShader = Shader(os.path.join(here, "0_vertexShader.glsl"), 
                      os.path.join(here, "0_fragmentShader.glsl"))
    myBgdShader = Shader(os.path.join(here, "0_bgd_vertexShader.glsl"), 
                         os.path.join(here, "0_bgd_fragmentShader.glsl"))
    objs = [
        Object(initPosition=glm.vec3(1500, 0, 0), initVelocity=glm.vec3(0, 500, 0), mass=7.34e22, density=3340, r=0.5, g=0.5, b=0.5, name="Moon"),
        Object(initPosition=glm.vec3(0, 0, 0), initVelocity=glm.vec3(0,0, 0), mass=5.97e24, density=5514, r=0.4, g=0.4, b=1, name="Earth"),
    ]

    bdg_obj = Background("background.jpg")



def simulate():
    global objs, myShader, lastFrame, deltaTime, came

    isPaused = camera.pause

    currentFrame = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    deltaTime = currentFrame - lastFrame
    lastFrame = currentFrame
    if (isPaused == False):
        for obj in objs:
            for obj2 in objs:
                if obj != obj2:
                    dx = obj2.getPosition()[0] - obj.getPosition()[0]
                    dy = obj2.getPosition()[1] - obj.getPosition()[1]
                    dz = obj2.getPosition()[2] - obj.getPosition()[2]
                    distance = glm.sqrt(math.pow(dx, 2) + math.pow(dy, 2) + math.pow(dz, 2))
                    if distance > 0:
                            direction = [dx / distance, 
                                        dy / distance, 
                                        dz / distance]
                            
                            distance *= 1000

                            G = 6.67430e-11 # Constante gravitacional
                            
                            gravF = (G * obj.mass * obj2.mass) / math.pow(distance, 2)
                            acc1 = gravF / obj.mass

                            acc = [direction[0] * acc1,
                                direction[1] * acc1,
                                direction[2] * acc1]
                            
                            obj.accelerate(acc[0], acc[1], acc[2], dt=deltaTime)

                            obj.velocity *= obj.checkCollision(obj2)

                            if obj.mass < obj2.mass:
                                orbital_info = [obj2.name, distance, gravF, obj2.mass]
                                obj.orbits.append(orbital_info)
            obj.updatePosition(dt=deltaTime)    
            obj.angularMomentum = obj.getAngularMomentum()
                            



# Render
def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    projection = glm.perspective(glm.radians(45.0), WIDTH / HEIGHT, 0.1, 750000)

    
    myBgdShader.bind()
    glDepthMask(GL_FALSE)
    bdg_obj.render(myShader.shaderId)
    glDepthMask(GL_TRUE)
    myBgdShader.unbind()

    myShader.bind()
    view = getViewMatrix()
    myShader.setUniformMat4("projection", projection)
    myShader.setUniformMat4("view", view)
    myShader.setUniform("lightDir", 0.5, -1.0, 0.3)
    myShader.setUniform("lightColor", 1.0, 1.0, 1.0)
    for obj in objs:
        model = glm.translate(obj.position)
        myShader.setUniformMat4("model", model)
        obj.render(myShader.shaderId)
        # print(f"{obj.name} position: {obj.getPosition()} radius: {obj.radius} mass: {obj.mass} density: {obj.density}")
        # print(f"{obj.orbits}")
        print(f"{obj.angularMomentum}")

    myShader.unbind()
    glutSwapBuffers()

# View Matrix para Camera
def getViewMatrix():
    return camera.getViewMatrix()

def reshape(width, height):
    glViewport(0, 0, width, height)
    projection = glm.perspective(glm.radians(45.0), width / height, 0.1, 100.0)
    myShader.bind()
    myShader.setUniformMat4("projection", projection)
    myShader.unbind()   
    
def idle():
    camera.doMovement()                                                                     # REVISAR
    simulate()
    glutPostRedisplay()       

def main():
    glutInit()
    init()
    glutReshapeFunc(reshape)
    glutIdleFunc(idle)
    glutPassiveMotionFunc(camera.mouseLookCallback)
    glutKeyboardFunc(camera.keyDownCallback)
    glutKeyboardUpFunc(camera.keyUpCallback)
    glutDisplayFunc(render)
    glutMainLoop()

if __name__ == "__main__":
    main()

