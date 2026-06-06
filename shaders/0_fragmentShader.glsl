#version 330 core

in vec3 f_color;
in vec3 f_normal;

out vec4 fragColor;

uniform vec3 lightDir;
uniform vec3 lightColor;
uniform bool glow;

void main(){

    if (glow) { 
    fragColor = vec4(f_color, 1.0);
    } else {
    
    float ambient_strenght = 0.01;
    vec3 ambient = ambient_strenght * lightColor;
    
    vec3 norm = normalize(f_normal);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    vec3 result = diffuse * f_color;
    fragColor = vec4(result, 1.0);
    }
}
