#version 330 core

layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec3 a_color;

uniform mat4 model; 
uniform mat4 projection;
uniform mat4 view;
    
out vec3 f_color;

void main(){
    f_color = a_color;
    gl_Position = projection * view * model * vec4(a_pos, 1.0);
} 