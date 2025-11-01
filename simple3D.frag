uniform vec4 u_light_positions[10];
uniform vec4 u_light_diffuse[10];
uniform vec4 u_light_specular[10];
uniform vec4 u_light_ambient[10];
uniform int u_num_lights;

uniform vec4 u_mat_diffuse;
uniform vec4 u_mat_specular;
uniform vec4 u_mat_ambient;
uniform float u_mat_shininess;

uniform int u_atten_check;

uniform sampler2D u_tex01;
uniform sampler2D u_tex02;
uniform int u_use_texture;

varying vec4 v_normal;
varying vec4 v_position;
varying vec4 v_view;
varying vec2 v_uv;

void main(void)
{
	vec4 color = vec4(0.0);

	for(int i = 0; i < 10; i++)
	{
		if(i >= u_num_lights) break;

		vec4 mat_diffuse = u_mat_diffuse;
		vec4 mat_specular = u_mat_specular;
		if(u_use_texture == 1) {
			mat_diffuse = u_mat_diffuse * texture2D(u_tex01, v_uv);
			mat_specular = u_mat_specular * texture2D(u_tex02, v_uv);
    	}

		vec4 light_dir = u_light_positions[i] - v_position;
		float dist = length(light_dir);
		vec4 s = normalize(light_dir);
		vec4 h = normalize(s + v_view);

		float att = 1.0;
		if(u_atten_check == 1)
		{
			att = 1.0 / (0.1 + 0.5 * dist + 1.0 * dist * dist);
			att = clamp(att, 0.0, 1.0);
		}

		float lambert = max(dot(v_normal, s), 0.0);
		float phong = max(dot(v_normal, h), 0.0);

		color += u_light_diffuse[i] * mat_diffuse * att * lambert;
		color += u_light_specular[i] * mat_specular * att * pow(phong, u_mat_shininess);
		color += u_light_ambient[i] * u_mat_ambient * 0.1;
	}

	if(u_use_texture == 1) {
        vec4 tex_color = texture2D(u_tex01, v_uv);
		vec4 tex_color2 = texture2D(u_tex02, v_uv);
        color = color * tex_color * tex_color2;
    }
    
    gl_FragColor = color;
}