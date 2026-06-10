#version 330 core

out vec4 a_frag_color;

in vec3 v_txr;

uniform samplerCube s_txr;

void main(){
    a_frag_color = texture(s_txr, v_txr);
}
