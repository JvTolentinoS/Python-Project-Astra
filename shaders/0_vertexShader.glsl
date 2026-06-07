#version 330 core

layout(location = 0) in vec3 a_pos;
layout(location = 1) in vec3 a_color;
layout(location = 2) in vec3 a_normal;

uniform mat4 model;
uniform mat4 projection;
uniform mat4 view;

out vec3 f_color;
out vec3 f_normal;
out vec3 f_position;

void main(){
    f_color = a_color;
    f_position = vec3(model * vec4(a_pos, 1.0)); 
    f_normal = mat3(transpose(inverse(model))) * a_normal;
    gl_Position = projection * view * model * vec4(a_pos, 1.0);
}
