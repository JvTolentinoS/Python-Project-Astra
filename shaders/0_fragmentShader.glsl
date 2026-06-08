#version 330 core

layout (location = 0) out vec4 a_frag_color;
layout (location = 1) out vec4 bright_color;

in vec3 f_color;
in vec3 f_normal;
in vec3 f_position;

out vec4 frag_color;

struct Light {
    vec3 position;
    vec3 diffuse; 
    
    float constant;
    float linear;
    float quadratic;
};

uniform float radius;
uniform vec3 lightColor;
uniform bool glow;
uniform Light light;

void main(){
    float ambient_strenght = 0.0;
    vec3 ambient = ambient_strenght * lightColor;

    if (glow) { 
    a_frag_color = vec4(f_color, 1.0);
    vec3 result = f_color * 0.5;
    bright_color = vec4(result, 1.0);

    } else {
    vec3 norm = normalize(f_normal);
    vec3 light_dir = normalize(light.position - f_position);
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diff * lightColor;
    
    float distance = length(light.position - f_position) - radius;
    float attenuation = 1.0 / (light.constant + light.linear*distance + light.quadratic*(distance * distance));
    diffuse *= attenuation; 
    vec3 result = diffuse * f_color;

    float brightness = dot(result, vec3 (0.2126, 0.7152, 0.0722));
        if (brightness > 0.1){
            bright_color = vec4(result, 1.0);
        } else {
            bright_color = vec4(0.0, 0.0, 0.0, 1);
        }
        a_frag_color = vec4((result), 1.0);
    }
}

