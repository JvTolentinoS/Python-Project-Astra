#version 330 core

in vec2 v_texture;

uniform sampler2D s_texture;

out vec4 fragColor;

void main(){
    fragColor = texture(s_texture, v_texture);
}
