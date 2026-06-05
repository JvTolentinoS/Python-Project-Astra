#version 330 core

in vec3 f_color;
in vec2 v_texture;

uniform sampler2D s_texture;
uniform int u_is_background;
uniform vec2 scale;

out vec4 fragColor;

void main(){
    if (u_is_background == 1) {
        fragColor = texture(s_texture, v_texture);
    } else {
        float ambientStrength = 0.1; 
        vec3 ambient = ambientStrength * f_color;
        vec3 result = ambient * f_color;
        fragColor = vec4(ambient, 1.0);
    }
}
