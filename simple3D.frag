
uniform vec4 u_light_diffuse;
uniform vec4 u_mat_diffuse;
uniform vec4 u_light_specular;
uniform vec4 u_mat_specular;
uniform float u_mat_shininess;
uniform vec4 u_light_ambient;
uniform vec4 u_mat_ambient;

uniform vec4 u_light_diffuse_2;
uniform vec4 u_light_specular_2;
uniform vec4 u_light_ambient_2;
uniform int atten_check;

varying vec4 v_normal;
varying vec4 v_s;
varying vec4 v_h;
varying vec4 v_s_2;
varying vec4 v_h_2;


void main(void)
{
	float dist = length(v_s);
	float dist_2 = length(v_s_2);
	float att = 1.0 / ((0.1 + 1.5*dist));
	float att_2 = 1.0 / ((0.1 + 0.5*dist_2 + 1.0*dist_2*dist_2));
	att = clamp(att, 0.0, 1.0);
	att_2 = clamp(att_2, 0.0, 1.0);

	if (atten_check == 0){
		att = 0.5;
	}

	float lambert = max(dot(v_normal, normalize(v_s)), 0.0);
	float lambert_2 = max(dot(v_normal, normalize(v_s_2)), 0.0);

	float phong = max(dot(v_normal, v_h), 0.0);
	float phong_2 = max(dot(v_normal, v_h_2), 0.0);

	vec4 color = vec4(0.0);
	color += 5.0* (u_light_diffuse * u_mat_diffuse * att * lambert + u_light_specular * u_mat_specular * att * pow(phong,u_mat_shininess)) + (u_light_ambient * u_mat_ambient * 0.1);

    gl_FragColor = color + (5.0* (u_light_diffuse_2 * u_mat_diffuse * att_2 * lambert_2 + u_light_specular_2 * u_mat_specular * att_2 * pow(phong_2,u_mat_shininess)) + (u_light_ambient_2 * u_mat_ambient * 0.1));
}