                                                
import glm                                                                      # pip install PyGLM
from circle import *
from OpenGL.GL import *                                                         # pip install PyOpenGL PyOpenGL_accelerate                                                
from OpenGL.GLU import *                                                         
from OpenGL.GLUT import *                                                       
from shader import Shader
from camera import Camera


# Constantes Globais
WIDTH, HEIGHT = 1280, 720

# Objetos Globais
camera = Camera(WIDTH=1280, HEIGHT=720)
obj = []
myShader = None

# Configurações Iniciais
def init(): 
    global obj, myShader
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Project Astra")
    glEnable(GL_DEPTH_TEST)
    glutSetCursor(GLUT_CURSOR_NONE)
    glClearColor(0.0, 0.0, 0.0, 1.0)
                                           
    here = os.path.dirname(os.path.abspath(__file__))                           
    myShader = Shader(os.path.join(here, "0_vertexShader.glsl"), 
                      os.path.join(here, "0_fragmentShader.glsl"))

    obj.append(Sphere())
    obj.append(Sphere(radius=1, r=0, g=1, b=0))

# Render
def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    projection = glm.perspective(glm.radians(45.0), WIDTH / HEIGHT, 0.1, 100.0)

    myShader.bind()
    view = getViewMatrix()
    myShader.setUniformMat4("projection", projection)
    myShader.setUniformMat4("model", glm.mat4(1.0))
    myShader.setUniformMat4("view", view)
    obj[0].render(myShader.shaderId)
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

