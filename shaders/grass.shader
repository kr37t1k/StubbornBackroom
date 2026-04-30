shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_alpha, cull_disabled;

uniform float wind_speed : hint_range(0.0, 2.0) = 0.8;
uniform float wind_strength : hint_range(0.0, 1.0) = 0.4;
uniform float wind_frequency : hint_range(0.0, 5.0) = 1.5;

uniform float step_impact : hint_range(0.0, 3.0) = 1.5;
uniform float step_radius : hint_range(0.0, 10.0) = 4.0;
uniform vec3 step_position = vec3(0.0);
uniform float step_decay_rate : hint_range(0.1, 10.0) = 3.0;

uniform vec4 grass_base_color : hint_color = vec4(0.2, 0.5, 0.15, 1.0);
uniform vec4 grass_light_color : hint_color = vec4(0.4, 0.7, 0.3, 1.0);

varying float v_height;
varying vec3 v_world_pos;
varying float v_time_offset;

void vertex() {
	v_world_pos = (WORLD_MATRIX * vec4(VERTEX, 1.0)).xyz;
	v_height = VERTEX.y;
	v_time_offset = sin(NORMAL.x * 100.0) * 100.0;
	
	// Время для анимации
	float time = TIME * wind_speed + v_time_offset;
	
	// Базовая волна ветра
	float wind_x = sin(v_world_pos.x * wind_frequency + time) * 0.5;
	float wind_z = cos(v_world_pos.z * wind_frequency * 0.7 + time * 0.8) * 0.5;
	
	// Эффект от шагов
	float dist = distance(v_world_pos.xz, step_position.xz);
	float step_factor = max(0.0, 1.0 - dist / step_radius);
	step_factor = smoothstep(1.0, 0.0, step_factor);
	
	// Затухание шага (имитация через модуль времени)
	float step_decay = exp(-step_decay_rate * fmod(time * 0.5 + 1000.0, 1.0));
	step_factor *= step_decay;
	
	// Применяем только к верхней части травинки
	float height_factor = smoothstep(0.2, 1.0, v_height);
	
	// Смещение вершин
	vec3 offset = vec3(
		(wind_x + step_factor * step_impact) * wind_strength * height_factor,
		0.0,
		wind_z * wind_strength * height_factor * 0.5
	);
	
	VERTEX.x += offset.x;
	VERTEX.z += offset.z;
	
	// Обновляем нормаль
	NORMAL.x += offset.x * 2.0;
	NORMAL.z += offset.z;
	NORMAL = normalize(NORMAL);
}

void fragment() {
	// Базовый цвет травы
	vec3 base = grass_base_color.rgb;
	
	// Добавляем вариацию цвета
	float color_var = sin(v_world_pos.x * 0.5) * sin(v_world_pos.z * 0.5) * 0.2 + 1.0;
	base *= color_var;
	
	// Светлее сверху
	float height_light = v_height * 0.3 + 0.7;
	base = mix(base, grass_light_color.rgb, height_light * 0.3);
	
	ALBEDO = base;
	
	// Прозрачность для кончиков
	ALPHA = smoothstep(0.0, 0.3, v_height) * grass_base_color.a;
	
	// Немного затемняем при эффекте шага
	float dist = distance(v_world_pos.xz, step_position.xz);
	float step_vis = max(0.0, 1.0 - dist / (step_radius * 1.5));
	ALPHA *= 1.0 - step_vis * 0.3;
}
