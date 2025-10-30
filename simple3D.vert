attribute vec3 a_position;
attribute vec3 a_normal;

uniform mat4 u_model_matrix;
uniform mat4 u_projection_view_matrix;
uniform mat4 u_projection_matrix;
uniform mat4 u_view_matrix;

// uniform vec4 u_color;

uniform vec4 u_eye_position;

uniform vec4 u_light_position;
uniform vec4 u_light_position_2;



varying vec4 v_color;  //Leave the varying variables alone to begin with
varying vec4 v_normal;
varying vec4 v_s;
varying vec4 v_h;
varying vec4 v_s_2;
varying vec4 v_h_2;


void main(void)
{
	vec4 position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
	vec4 normal = vec4(a_normal.x, a_normal.y, a_normal.z, 0.0);

	// LOCAL COORDINATES

	position = u_model_matrix * position;
	v_normal = normalize(u_model_matrix * normal);


	// GLOBAL COORDINATES

	v_s = (u_light_position - position);
	v_s_2 = (u_light_position_2 - position);

	vec4 v = normalize(u_eye_position - position);
	vec4 v_2 = normalize(u_eye_position - position);
	v_h = normalize(v_s + v);
	v_h_2 = normalize(v_s_2 + v_2);

	// float light_factor_1 = max(dot(normalize(normal), normalize(vec4(1, 2, 3, 0))), 0.0);
	// float light_factor_2 = max(dot(normalize(normal), normalize(vec4(-3, -2, -1, 0))), 0.0);
	// v_color = (light_factor_1 + light_factor_2) * u_color; // ### --- Change this vector (pure white) to color variable --- #####



	// ### --- Change the projection_view_matrix to separate view and projection matrices --- ### 
	
	position = u_view_matrix * position;
	position = u_projection_matrix * position;

	gl_Position = position;
}