#version 330 core

in vec3 f_color;

out vec4 fragColor;

void main(){
    float ambientStrength = 0.1; 
    vec3 ambient = ambientStrength * f_color;
    vec3 result = ambient * f_color;
    fragColor = vec4(result, 1.0);
}
