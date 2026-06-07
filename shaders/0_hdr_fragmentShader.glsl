#version 330 core
out vec4 fragColor;

in vec2 tex_coords;

uniform sampler2D hdr_buffer;
uniform sampler2D bloom_blur;
uniform float exposure;

void main()
{             
    const float gamma = 1.2;
    vec3 hdr_color = texture(hdr_buffer, tex_coords).rgb;
    vec3 bloom_color = texture(bloom_blur, tex_coords).rgb;

        hdr_color += bloom_color;

    vec3 result = vec3(1.0) - exp(-hdr_color * exposure);
        
    result = pow(result, vec3(1.0 / gamma));
    fragColor = vec4(result, 1.0);
}
