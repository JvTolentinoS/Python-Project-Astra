#version 330 core

layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec3 a_color;
layout(location = 2) in vec2 a_texture;

uniform mat4 model; 
uniform mat4 projection;
uniform mat4 view;
uniform int u_is_background;

out vec3 f_color;
out vec2 v_texture;

void main(){
    f_color = a_color;
    v_texture = a_texture;

    if (u_is_background == 1) {
        gl_Position = vec4(a_pos.xy, 0.0, 1.0);
    } else {
        gl_Position = projection * view * model * vec4(a_pos, 1.0);
    }
} 