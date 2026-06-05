#version 330 core

in vec3 f_color;
in vec3 f_normal;

out vec4 fragColor;

uniform vec3 lightDir;
uniform vec3 lightColor;

void main(){
    float ambient_strenght = 0.01;
    vec3 norm = normalize(f_normal);
    vec3 ambient = ambient_strenght * lightColor;
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diff * lightColor;
    vec3 result = (ambient + diffuse) * f_color;
    fragColor = vec4(result, 1.0);
}
