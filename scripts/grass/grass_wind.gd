@tool
extends Resource
class_name GrassWindShader

# Параметры ветра
@export_range(0.0, 2.0, 0.01) var wind_speed: float = 0.5
@export_range(0.0, 1.0, 0.01) var wind_strength: float = 0.3
@export_range(0.0, 3.0, 0.01) var wind_frequency: float = 1.0

# Параметры шагов игрока
@export_range(0.0, 2.0, 0.01) var step_impact: float = 1.0
@export_range(0.0, 10.0, 0.01) var step_radius: float = 3.0

func get_shader_code() -> String:
	return """
	shader_type spatial;
	render_mode unshaded, blend_mix, depth_draw_opaque, cull_disabled, shadow_objection_disabled;

	uniform float wind_speed : hint_range(0.0, 2.0) = 0.5;
	uniform float wind_strength : hint_range(0.0, 1.0) = 0.3;
	uniform float wind_frequency : hint_range(0.0, 3.0) = 1.0;
	
	uniform float step_impact : hint_range(0.0, 2.0) = 1.0;
	uniform float step_radius : hint_range(0.0, 10.0) = 3.0;
	uniform vec3 step_position = vec3(0.0);
	uniform float step_decay = 5.0;
	uniform float time = 0.0;

	varying vec3 v_world_pos;
	varying float v_height_factor;

	void vertex() {
		v_world_pos = (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
		
		// Базовая высота для вариации
		v_height_factor = VERTEX.y;
		
		// Анимация ветра (синусоидальная волна)
		float wind_time = time * wind_speed;
		float wind_x = sin(v_world_pos.x * wind_frequency + wind_time) * 0.5;
		float wind_z = cos(v_world_pos.z * wind_frequency * 0.7 + wind_time) * 0.5;
		
		// Эффект от шагов (радиальное затухание)
		float dist_to_step = distance(v_world_pos.xz, step_position.xz);
		float step_effect = max(0.0, 1.0 - dist_to_step / step_radius);
		step_effect = smoothstep(1.0, 0.0, step_effect);
		step_effect *= step_impact;
		
		// Добавляем затухание шага со временем (в шейдере это упрощено)
		float step_decay_effect = exp(-step_decay * fmod(time * 2.0, 1.0)) * step_effect;
		
		// Применяем искажение к вершинам (только для верхней части травы)
		float height_factor = smoothstep(0.3, 1.0, v_height_factor);
		vec3 wind_offset = vec3(
			(wind_x + wind_z) * wind_strength * height_factor,
			0.0,
			0.0
		);
		
		// Эффект от шагов (горизонтальное смещение)
		vec3 step_offset = vec3(
			wind_x * step_decay_effect * height_factor * 2.0,
			0.0,
			wind_z * step_decay_effect * height_factor * 2.0
		);
		
		VERTEX.x += wind_offset.x + step_offset.x;
		VERTEX.z += wind_offset.z + step_offset.z;
		
		// Обновляем нормаль для правильного освещения
		NORMAL.x += wind_offset.x * 0.5;
		NORMAL.z += wind_offset.z * 0.5;
		NORMAL = normalize(NORMAL);
	}

	void fragment() {
		ALBEDO = vec3(0.2, 0.5, 0.15); // Зелёный цвет травы
		
		// Вариация цвета для естественности
		float color_var = sin(VIEWPORT_POSITION.x * 0.1) * sin(VIEWPORT_POSITION.y * 0.1) * 0.2 + 0.8;
		ALBEDO.r *= color_var;
		ALBEDO.g *= color_var;
		ALBEDO.b *= color_var;
		
		// Затемнение по высоте
		ALBEDO *= (v_height_factor * 0.5 + 0.5);
		
		// Прозрачность для кончиков травы
		ALPHA = smoothstep(0.0, 0.3, v_height_factor);
	}
	"""
