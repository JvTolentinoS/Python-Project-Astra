#version 330 core
out vec4 fragColor;

in vec2 tex_coords;

uniform sampler2D hdr_buffer;
uniform bool hdr;
uniform float exposure;

void main()
{             
    const float gamma = 2.2;
    vec3 hdr_color = texture(hdr_buffer, tex_coords).rgb;
        vec3 result = vec3(1.0) - exp(-hdr_color * exposure);
        
        result = pow(result, vec3(1.0 / gamma));
        fragColor = vec4(result, 1.0);
}
