#version 330 core

out vec4 a_frag_color;

in vec3 v_texture;

uniform samplerCube s_texture;

void main(){
    a_frag_color = texture(s_texture, v_texture);
}
