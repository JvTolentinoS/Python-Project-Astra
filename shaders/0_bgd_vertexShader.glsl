#version 330 core

layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec3 a_color;
layout(location = 2) in vec2 a_texture;

out vec2 v_texture;

void main(){
    v_texture = a_texture;
    gl_Position = vec4(a_pos.xy, 0.0, 1.0);
}
