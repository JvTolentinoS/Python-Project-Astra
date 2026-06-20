import os
import math
import glm                                                                      # pip install PyGLM
import ctypes
from OpenGL.GL import *                                                         # pip install PyOpenGL PyOpenGL_accelerate
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np                                                             
import system_dict as sys_dic
import constants as c
import objects as o_func
from objects import Object
from objects import Barycenter
from objects import Orbit
from objects import Skybox
from shader import Shader
from camera import Camera

camera = None
bdg_obj = None
system_obj_list = []
orbits = []

my_shader = None
my_HDR_shader = None
my_BLUR_shader = None

hdr_FBO = None
rbo_depth = None
color_buffer = None
ping_pong_Colorbuffer = None
ping_pong_FBO = None
msaa_FBO = None

quadVAO = 0
quadVBO = None

last_frame = 0.0
delta_time = 0.0


def init():
    global system_obj_list, bdg_obj, camera
    global hdr_FBO, rbo_depth, color_buffer, ping_pong_Colorbuffer, ping_pong_FBO, msaa_FBO
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

    attachments = [GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1]

    # msaa frame buffer pointer
    # -------------------------
    msaa_FBO = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, msaa_FBO)

    # msaa para buffer/bloom
    # ----------------------
    msaa_color_buffer = glGenTextures(2)
    for i in range(2):
        glBindTexture(GL_TEXTURE_2D_MULTISAMPLE, msaa_color_buffer[i])
        glTexImage2DMultisample(GL_TEXTURE_2D_MULTISAMPLE, 8, GL_RGBA16F, c.WIDTH, c.HEIGHT, GL_TRUE)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + i, GL_TEXTURE_2D_MULTISAMPLE, msaa_color_buffer[i], 0)

    # msaa render buffer pointer
    # --------------------------
    msaa_rbo = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, msaa_rbo)
    glRenderbufferStorageMultisample(GL_RENDERBUFFER, 8, GL_DEPTH_COMPONENT, c.WIDTH, c.HEIGHT)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, msaa_rbo)
    glDrawBuffers(2, attachments)
    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        print(f"FRAMEBUFFER: {status}")
    glBindFramebuffer(GL_FRAMEBUFFER, 0)

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
    glUniform1i(glGetUniformLocation(my_BGD_shader.shaderId, "s_txr"), 0)
    my_BGD_shader.unbind()

    bdg_obj = Skybox()

    # dicionário de objetos da simulação
    # -----------------------------
    system_obj_list = [Object(name=key, **value) for key, value in sys_dic.system_obj_dict.items()]
    camera.objs_list = system_obj_list
    camera.orb_list = orbits

# Lógica de Simulação
# -------------------
def simulate():
    
    global system_obj_list, orbits
    global last_frame, delta_time
    
    is_paused = camera.pause
    accs = {}
    
    if is_paused is False:        
        for obj in system_obj_list:
            t_accs = glm.vec3(0.0,0.0,0.0)
            
            for obj2 in system_obj_list:
                if obj != obj2:
                    vec_dist = obj2.position - obj.position
                    distance = glm.distance(obj2.position, obj.position)
                    if distance > 0:
                        direction = glm.vec3(vec_dist) / distance
                        distance *= c.SIMULATION_DISTANCE_SCALED
                        distance *= c.SCALE_KM 
                        
                        gravF = (c.G * obj._mass * obj2._mass) / math.pow(distance, 2)
                        acc1 = (gravF / obj._mass) / c.SCALE_KM
                        
                        t_accs += direction * acc1
                        
                accs[obj] = t_accs
        
        for obj in system_obj_list: 
            obj.accelerate(accs[obj], delta_time)
            obj.update_velocity_scaled()
            
        for obj in system_obj_list:
            for obj2 in system_obj_list:
                if obj != obj2:
                    obj._velocity *= obj.check_collision(obj2)
                        
        for obj in system_obj_list:
            obj.update_position(delta_time)
            obj.update_position_scaled()
                
        for obj in system_obj_list:
            for obj2 in system_obj_list:
                if obj != obj2:
                    o_func.define_rel(obj, obj2)
                    
        hierarchy, barycenter = o_func.hierarchy(system_obj_list)
        o_func.update_focal_point(hierarchy, barycenter)
        
        for body, host in hierarchy.items():
            if hasattr(body, 'host_body'):
                body.host_body = host
        
        for obj in system_obj_list:
            obj.host_body = hierarchy.get(obj)
        
        for obj in system_obj_list:
            obj.chain_function(orbits)

def render():
    global last_frame, delta_time
    global hdr_FBO, rbo_depth, color_buffer, quadVAO, ping_pong_FBO, ping_pong_Colorbuffer, msaa_FBO

    current_frame = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    fps_delta_time = current_frame - last_frame
    last_frame = current_frame
    delta_time = fps_delta_time * c.SIMULATION_TIME_SPEED
    
    simulate()
    
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glBindFramebuffer(GL_FRAMEBUFFER, hdr_FBO)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glBindFramebuffer(GL_FRAMEBUFFER, msaa_FBO)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_MULTISAMPLE)

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

    for obj in system_obj_list:
        if obj.glow:
            my_shader.setUniform("glow", 1)
            my_shader.setUniform("activateLight", 1)
            my_shader.setUniform("radius", obj._radius)
            my_shader.setUniformGlm("light.position", obj._position)
            my_shader.setUniform("lightColor", 1.0, 1.0, 1.0)
        else:
            my_shader.setUniform("glow", 0)

        model = glm.translate(obj._position)
        my_shader.setUniformMat4("model", model)
        obj.render(my_shader.shaderId)

    my_shader.unbind()

    my_shader.bind()
    my_shader.setUniform("orbit", 1)
    if orbits: 
        for obj in orbits:
            host = obj.sel_object.host_body
            if isinstance(host, Barycenter) and obj.sel_object in host.members:
                center = host.position
            else: 
                center = obj.sel_object.focal_pos
            model = glm.translate(glm.mat4(1.0), center)
            my_shader.setUniformMat4("model", model)
            obj.render(my_shader.shaderId)
    my_shader.setUniform("orbit", 0)
    my_shader.unbind
    
    glDisable(GL_MULTISAMPLE)

    glBindFramebuffer(GL_READ_FRAMEBUFFER, msaa_FBO)
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, hdr_FBO)

    glReadBuffer(GL_COLOR_ATTACHMENT0)
    glDrawBuffer(GL_COLOR_ATTACHMENT0)
    glBlitFramebuffer(0, 0, c.WIDTH, c.HEIGHT, 0, 0, c.WIDTH, c.HEIGHT, GL_COLOR_BUFFER_BIT, GL_NEAREST)

    glReadBuffer(GL_COLOR_ATTACHMENT1)
    glDrawBuffer(GL_COLOR_ATTACHMENT1)
    glBlitFramebuffer(0, 0, c.WIDTH, c.HEIGHT, 0, 0, c.WIDTH, c.HEIGHT, GL_COLOR_BUFFER_BIT, GL_NEAREST)

    glBindFramebuffer(GL_FRAMEBUFFER, 0)

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
    projection = glm.perspective(glm.radians(45.0), width / height, 100, 3000000.0)
    my_shader.bind()
    my_shader.setUniformMat4("projection", projection)
    my_shader.unbind()
    
def renderQuad():
    global quadVAO, quadVBO
    if (quadVAO == 0):
        verts = [
                -1.0, 1.0, 0.0,     0.0, 1.0,
                -1.0,-1.0, 0.0,    0.0, 0.0,
                 1.0, 1.0, 0.0,     1.0, 1.0,
                 1.0,-1.0, 0.0,    1.0, 0.0
        ]

        verts = np.array(verts, dtype=np.float32)

        quadVAO = glGenVertexArrays(1)
        glBindVertexArray(quadVAO)

        quadVBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, quadVBO)
        glBufferData(GL_ARRAY_BUFFER,
                    verts.nbytes,
                    verts, GL_STATIC_DRAW)

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

