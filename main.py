import os
import math
import glm                                                                      # pip install PyGLM
from OpenGL.GL import *                                                         # pip install PyOpenGL PyOpenGL_accelerate                                                
from OpenGL.GLU import *                                                         
from OpenGL.GLUT import *                                                       
import numpy as np
from objects import Object
from objects import Background
from shader import Shader
from camera import Camera
import constants as c


camera = None
my_shader = None
my_HDR_shader = None
bdg_obj = None
objs = []

hdr_FBO = None
rbo_depth = None 
color_buffer = None
quadVAO = 0
quadVBO = None

last_frame = 0.0
delta_time = 0.0

exposure = 1.0

# config
def init(): 
    global my_shader, my_BGD_shader, my_HDR_shader, objs, bdg_obj, camera, hdr_FBO, rbo_depth, color_buffer

    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowSize(c.WIDTH, c.HEIGHT)
    glutCreateWindow(b"Project Astra") 

    glutSetOption(GLUT_MULTISAMPLE, 8)
    glEnable(GL_DEPTH_TEST)
    
    glutSetCursor(GLUT_CURSOR_NONE)
    camera = Camera(c.WIDTH, c.HEIGHT)

    here = os.path.dirname(os.path.abspath(__file__))                           
    my_shader = Shader(os.path.join(here, "shaders/0_vertexShader.glsl"), 
                       os.path.join(here, "shaders/0_fragmentShader.glsl"))
    my_BGD_shader = Shader(os.path.join(here, "shaders/0_bgd_vertexShader.glsl"), 
                           os.path.join(here, "shaders/0_bgd_fragmentShader.glsl"))
    my_HDR_shader = Shader(os.path.join(here, "shaders/0_hdr_vertexShader.glsl"),
                           os.path.join(here, "shaders/0_hdr_fragmentShader.glsl"))
    
    # frame buffer pointer
    hdr_FBO = glGenFramebuffers(1)

    # collor buffer pointer
    color_buffer = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, color_buffer)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, c.WIDTH, c.HEIGHT, 0, GL_RGBA, GL_FLOAT, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # render buffer pointer
    rbo_depth = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, rbo_depth)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, c.WIDTH, c.HEIGHT)

    # conectando os buffers
    glBindFramebuffer(GL_FRAMEBUFFER, hdr_FBO)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color_buffer, 0)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, rbo_depth)

    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        print(f"FRAMEBUFFER: {GL_FRAMEBUFFER_COMPLETE}")
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    my_HDR_shader.bind()
    glUniform1i(glGetUniformLocation(my_HDR_shader.shaderId, "hdr_buffer"), 0)
    my_HDR_shader.setUniform("exposure", exposure)
    my_HDR_shader.unbind()

    objs = [
        Object(init_position=glm.vec3(20000, 0, 0), init_velocity=glm.vec3(0, 0, 0), mass=7.34e22, density=3340, r=0.5, g=0.5, b=0.5, name="Moon"),
        Object(init_position=glm.vec3(10000, 0, 0), init_velocity=glm.vec3(0, 3000, 0), mass=5.97e24, density=5514, r=0.4, g=0.4, b=1, name="Earth"),
        Object(init_position=glm.vec3(0, 0, 0), init_velocity=glm.vec3(0, 0, 0), mass=1.90e27, density=1326, r=0.8, g=0.8, b=0.5, name="Theia", glow=True)
    ]

    bdg_obj = Background("assets/background.png")

    # exposure uniform will be set each frame after binding the HDR shader

def simulate():
    global objs, my_shader, last_frame, delta_time

    is_paused = camera.pause

    if is_paused is False:
        for obj in objs:
            for obj2 in objs:
                if obj != obj2:
                    dx = obj2.get_position()[0] - obj.get_position()[0]
                    dy = obj2.get_position()[1] - obj.get_position()[1]
                    dz = obj2.get_position()[2] - obj.get_position()[2]
                    distance = glm.sqrt(math.pow(dx, 2) + math.pow(dy, 2) + math.pow(dz, 2))
                    
                    if distance > 0:
                            direction = [
                                dx / distance, 
                                dy / distance, 
                                dz / distance
                            ]
                            
                            distance *= 1000 # para escalar a simulação em 3^10
                            
                            gravF = (c.G * obj.mass * obj2.mass) / math.pow(distance, 2)
                            acc1 = gravF / obj.mass

                            acc = [
                                direction[0] * acc1,
                                direction[1] * acc1,
                                direction[2] * acc1
                            ]
                            
                            obj.accelerate(acc[0], acc[1], acc[2], dt=delta_time)

                            obj.velocity *= obj.check_collision(obj2)

                            if obj.mass < obj2.mass:
                                orbital_info = [obj2.name, distance, gravF, obj2.mass]
                                obj.orbits.append(orbital_info)
            obj.update_position(dt=delta_time)    
            obj.angular_momentum = obj.get_angular_momentum()                            

def render():
    global last_frame, delta_time, hdr_FBO, rbo_depth, color_buffer, quadVAO

    current_frame = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    delta_time = current_frame - last_frame
    last_frame = current_frame

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glBindFramebuffer(GL_FRAMEBUFFER, hdr_FBO)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    my_BGD_shader.bind()
    glDepthMask(GL_FALSE)
    bdg_obj.render(my_BGD_shader.shaderId)
    glDepthMask(GL_TRUE)
    my_BGD_shader.unbind()

    my_shader.bind()
    my_shader.setUniformMat4("projection", camera.get_projection())
    my_shader.setUniformMat4("view", camera.get_view_matrix())
    my_shader.setUniform("glow", 0)

    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, color_buffer)

    for obj in objs:
        model = glm.translate(obj.position)
        my_shader.setUniformMat4("model", model)
        
        if obj.glow:
            light_dir = glm.normalize(glm.vec3(0.0, 0.0, 0.0) - obj.position)
            my_shader.setUniform("glow", 1)
            my_shader.setUniform("lightDir", light_dir.x, light_dir.y, light_dir.z)
            my_shader.setUniform("lightColor", 1.0, 1.0, 1.0)
        else: 
            my_shader.setUniform("glow", 0)
        obj.render(my_shader.shaderId)
        # print(f"{obj.name} position: {obj.getPosition()} radius: {obj.radius} mass: {obj.mass} density: {obj.density}")
        # print(f"{obj.orbits}")
    my_shader.unbind()
    
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    my_HDR_shader.bind()
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, color_buffer)
    renderQuad()
    my_HDR_shader.unbind()
    glutSwapBuffers()


def reshape(width, height):
    glViewport(0, 0, width, height)
    projection = glm.perspective(glm.radians(45.0), width / height, 0.1, 100.0)
    my_shader.bind()
    my_shader.setUniformMat4("projection", projection)
    my_shader.unbind()   
    

def renderQuad():
    global quadVAO, quadVBO
    if (quadVAO == 0):
        vertices = [
                -1.0, 1.0, 0.0, 0.0, 1.0,
                -1.0, -1.0, 0.0, 0.0, 0.0,
                1.0, 1.0, 0.0, 1.0, 1.0,
                1.0, -1.0, 0.0, 1.0, 0.0
        ]

        vertices = np.array(vertices, dtype=np.float32)

        quadVAO = glGenVertexArrays(1)
        glBindVertexArray(quadVAO)

        quadVBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, quadVBO)
        glBufferData(GL_ARRAY_BUFFER, 
                    vertices.nbytes,
                    vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5*4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5*4, ctypes.c_void_p(3*4))

    glBindVertexArray(quadVAO)
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
    glBindVertexArray(0)    


def idle():
    camera.do_movement()                                                                     # REVISAR
    simulate()
    glutPostRedisplay()       

def main():
    glutInit()
    init()
    glutReshapeFunc(reshape)
    glutIdleFunc(idle)
    glutPassiveMotionFunc(camera.mouse_look_callback)
    glutKeyboardFunc(camera.key_down_callback)
    glutKeyboardUpFunc(camera.key_up_callback)
    glutDisplayFunc(render)
    glutMainLoop()

if __name__ == "__main__":
    main()

