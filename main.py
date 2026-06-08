import os
import math
import glm                                                                      # pip install PyGLM
import ctypes
from OpenGL.GL import *                                                         # pip install PyOpenGL PyOpenGL_accelerate                                                
from OpenGL.GLU import *                                                         
from OpenGL.GLUT import *                                                       
import numpy as np
import constants as c
from objects import Object
from objects import Orbit
from objects import Background
from shader import Shader
from camera import Camera


camera = None
bdg_obj = None
objs = []

my_shader = None
my_HDR_shader = None
my_BLUR_shader = None

hdr_FBO = None
rbo_depth = None 
color_buffer = None
ping_pong_Colorbuffer = None
ping_pong_FBO = None

quadVAO = 0
quadVBO = None  

last_frame = 0.0
delta_time = 0.0

# config
def init(): 
    global objs, bdg_obj, camera, text_container
    global hdr_FBO, rbo_depth, color_buffer, ping_pong_Colorbuffer, ping_pong_FBO
    global my_shader, my_BGD_shader, my_HDR_shader, my_BLUR_shader

    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE)
    glutInitWindowSize(c.WIDTH, c.HEIGHT)
    glutCreateWindow(b"Project Astra") 

    glutSetOption(GLUT_MULTISAMPLE, 8)
    glEnable(GL_DEPTH_TEST)
    
    glutSetCursor(GLUT_CURSOR_NONE)
    camera = Camera(c.WIDTH, c.HEIGHT)

    # programas de shader
    # -------------------
    here = os.path.dirname(os.path.abspath(__file__))                           
    my_shader = Shader(os.path.join(here, "shaders/0_vertexShader.glsl"), 
                       os.path.join(here, "shaders/0_fragmentShader.glsl"))
    my_BGD_shader = Shader(os.path.join(here, "shaders/0_bgd_vertexShader.glsl"), 
                           os.path.join(here, "shaders/0_bgd_fragmentShader.glsl"))
    my_HDR_shader = Shader(os.path.join(here, "shaders/0_hdr_vertexShader.glsl"),
                           os.path.join(here, "shaders/0_hdr_fragmentShader.glsl"))
    my_BLUR_shader = Shader(os.path.join(here, "shaders/0_blur_vertexShader.glsl"),
                           os.path.join(here, "shaders/0_blur_fragmentShader.glsl"))


    # frame buffer pointer
    # --------------------
    hdr_FBO = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, hdr_FBO)
    
    # color buffer pointer e buffer pointer para bloom
    # ------------------------------------------------
    color_buffer = glGenTextures(2)
    for i in range(2):
        glBindTexture(GL_TEXTURE_2D, color_buffer[i])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, c.WIDTH, c.HEIGHT, 0, GL_RGBA, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE) # necessario para não repetir a textura
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + i, GL_TEXTURE_2D, color_buffer[i], 0)


    # render buffer pointer
    # ---------------------
    rbo_depth = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, rbo_depth)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, c.WIDTH, c.HEIGHT)

    # conectando os buffers
    # ---------------------
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, rbo_depth)
    attachments = [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1] 
        
    glDrawBuffers(2, attachments)

    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        print(f"FRAMEBUFFER: {status}")
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    # buffer de blur
    # --------------
    ping_pong_FBO = glGenFramebuffers(2)
    ping_pong_Colorbuffer = glGenTextures(2)

    for i in range(2):
        glBindFramebuffer(GL_FRAMEBUFFER, ping_pong_FBO[i])
        glBindTexture(GL_TEXTURE_2D, ping_pong_Colorbuffer[i])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, c.WIDTH, c.HEIGHT, 0, GL_RGBA, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE) # necessario para não repetir a textura
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, ping_pong_Colorbuffer[i], 0)
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
            print(f"FRAMEBUFFER: {status}")
    
    # sampling 
    # --------
    my_HDR_shader.bind()
    glUniform1i(glGetUniformLocation(my_HDR_shader.shaderId, "hdr_buffer"), 0)
    glUniform1i(glGetUniformLocation(my_HDR_shader.shaderId, "bloom_blur"), 1)
    my_HDR_shader.unbind()

    my_BLUR_shader.bind()
    glUniform1i(glGetUniformLocation(my_BLUR_shader.shaderId, "image"), 0)
    my_BLUR_shader.unbind()

    my_BGD_shader.bind()
    glUniform1i(glGetUniformLocation(my_BLUR_shader.shaderId, "s_texture"), 0)
    my_BGD_shader.unbind()

    bdg_obj = Background()

    # array de objetos da simulação
    # -----------------------------
    objs = [
        Object(init_position=glm.vec3(24005, 0, 0), init_velocity=glm.vec3(0.0, 0.0, 2582), mass=3.30e23, density=5514, r=0.4, g=0.4, b=0.4, name="Mercury"),
        Object(init_position=glm.vec3(0, 0, 0), init_velocity=glm.vec3(0.0, 0.0, 0.0), mass=1.989e30, density=1410, r=0.8, g=0.8, b=0.5, name="Sun", glow=True),
    ]
    # para o seletor
    # --------------
    camera.objs_list = objs

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
                            
                        distance *= 1000 # para escalar a simulação em 10³
                            
                        gravF = (c.G * obj.mass * obj2.mass) / math.pow(distance, 2)
                        acc1 = (gravF / obj.mass) / c.SCALE_KM

                        acc = [
                            direction[0] * acc1,
                            direction[1] * acc1,
                            direction[2] * acc1
                        ]
                            
                        obj.accelerate(acc[0], acc[1], acc[2], dt=delta_time)

                        obj.velocity *= obj.check_collision(obj2)
                        
                        if obj.mass < obj2.mass:
                            orbital_info = [
                                obj2.name, 
                                distance, 
                                gravF, 
                                obj2.mass, 
                                glm.vec3(obj2.velocity),
                                glm.vec3(obj2.position),
                            ]
                            is_registered = False
                                
                            if not obj.orbits:
                                obj.orbits.append(orbital_info)
                                is_registered = True
                            else:
                                for i in range(len(obj.orbits)):
                                    if obj.orbits[i][0] == orbital_info[0]:
                                        obj.orbits[i][1] = distance
                                        obj.orbits[i][2] = gravF
                                        obj.orbits[i][3] = obj2.mass
                                        obj.orbits[i][4] = glm.vec3(obj2.velocity)
                                        obj.orbits[i][5] = glm.vec3(obj2.position)
                                        is_registered = True
                                        
                            if not is_registered:
                                obj.orbits.append(orbital_info)
                                   
            obj.update_position(dt=delta_time)
            obj.main_attractor_pos = obj.get_main_attractor_pos()
            obj.eccentricity = obj.get_eccentricity_vector()                          

def render():
    global last_frame, delta_time
    global hdr_FBO, rbo_depth, color_buffer, quadVAO, ping_pong_FBO, ping_pong_Colorbuffer

    current_frame = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    delta_time = current_frame - last_frame
    last_frame = current_frame

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glBindFramebuffer(GL_FRAMEBUFFER, hdr_FBO)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # renderização do skybox
    # ----------------------
    my_BGD_shader.bind()
    glDepthFunc(GL_LEQUAL)
    view = glm.mat4(glm.mat3(camera.get_view_matrix()))
    my_BGD_shader.setUniformMat4("projection", glm.mat4(camera.get_projection()))
    my_BGD_shader.setUniformMat4("view", view)
    bdg_obj.render(my_BGD_shader.shaderId)
    glDepthFunc(GL_LESS)
    my_BGD_shader.unbind()

    # termos para o calculo de atenuação
    # ----------------------------------
    my_shader.bind()

    my_shader.setUniform("light.constant", c.light_attenuation_constant) 
    my_shader.setUniform("light.linear", c.light_attenuation_linear)
    my_shader.setUniform("light.quadratic", c.light_attenuation_quadratic)

    # matrizes de visualização e projeção
    # -----------------------------------
    my_shader.setUniformMat4("projection", camera.get_projection())
    my_shader.setUniformMat4("view", camera.get_view_matrix())
    
    # uniformes de luminosidade
    # -------------------------
    my_shader.setUniform("lightColor", 1.0, 1.0, 1.0)
    my_shader.setUniform("glow", 0)

    # renderização dos corpos
    # -----------------------
    for obj in objs:
        if obj.glow:
            my_shader.setUniform("glow", 1)
            my_shader.setUniform("radius", obj.radius)
            my_shader.setUniformGlm("light.position", obj.position)
            my_shader.setUniform("lightColor", 1.0, 1.0, 1.0)
        else:
            my_shader.setUniform("glow", 0)

        model = glm.translate(obj.position)
        my_shader.setUniformMat4("model", model)
        obj.render(my_shader.shaderId)
        # print(f"{obj.name} position: {obj.get_position()} radius: {obj.radius} mass: {obj.mass} density: {obj.density}")
        # print(f"{obj.orbits}")
    
    for obj in objs:
        if obj.orbits:
            orbit_format = Orbit(obj)
            model = orbit_format.get_rotation()
            my_shader.setUniformMat4("model", model)
            orbit_format.render(my_shader.shaderId)
                
    my_shader.unbind()
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # gaussian blur
    # -------------
    horizontal = True
    first_iteration = True

    my_BLUR_shader.bind()
    glUniform1i(glGetUniformLocation(my_BLUR_shader.shaderId, "image"), 0)
    for i in range(10):
        glBindFramebuffer(GL_FRAMEBUFFER, ping_pong_FBO[int(horizontal)])
        my_BLUR_shader.setUniformi("horizontal", horizontal)
        glBindTexture(GL_TEXTURE_2D, 
                      color_buffer[1] if first_iteration else ping_pong_Colorbuffer[int(not horizontal)])
        renderQuad()
        horizontal = not horizontal
        if (first_iteration):
            first_iteration = False
    my_BLUR_shader.unbind()
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

    my_HDR_shader.bind()
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, color_buffer[0])
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D, ping_pong_Colorbuffer[0])
    my_HDR_shader.setUniform("exposure", c.EXPOSURE)
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
                -1.0, 1.0, 0.0,     0.0, 1.0,
                -1.0, -1.0, 0.0,    0.0, 0.0,
                 1.0, 1.0, 0.0,     1.0, 1.0,
                 1.0, -1.0, 0.0,    1.0, 0.0
        ]

        vertices = np.array(vertices, dtype=np.float32)

        quadVAO = glGenVertexArrays(1)
        glBindVertexArray(quadVAO)

        quadVBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, quadVBO)
        glBufferData(GL_ARRAY_BUFFER, 
                    vertices.nbytes,
                    vertices, GL_STATIC_DRAW)
        
        glVertexAttribPointer(0, 
                              3, 
                              GL_FLOAT, 
                              GL_FALSE, 
                              5*4, 
                              ctypes.c_void_p(0))
        glVertexAttribPointer(1, 
                              2, 
                              GL_FLOAT, 
                              GL_FALSE, 
                              5*4, 
                              ctypes.c_void_p(3*4))

        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
    
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

