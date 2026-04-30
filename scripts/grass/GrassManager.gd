# scripts/grass/GrassManager.gd
# Управление травой и эффектом ветра

class_name GrassManager extends Node

@export var wind_speed: float = 0.8
@export var wind_strength: float = 0.4
@export var step_radius: float = 4.0
@export var step_decay_rate: float = 3.0

var grass_instances: Array = []
var step_position: Vector3 = Vector3.ZERO
var step_active: bool = false
var step_timer: float = 0.0

func _ready():
	pass

func _physics_process(delta):
	# Обновляем эффект шага
	if step_active:
		step_timer += delta
		if step_timer > 0.3:
			step_active = false
			step_timer = 0.0

func register_grass_instance(grass_node: Node):
	grass_instances.append(grass_node)
	_update_grass_shader(grass_node)

func set_step_position(pos: Vector3):
	step_position = pos
	step_active = true
	step_timer = 0.0
	
	# Обновляем все травинки
	for grass in grass_instances:
		_update_grass_shader(grass)

func _update_grass_shader(grass_node: Node):
	if grass_node and grass_node is MultiMeshInstance3D:
		var material = grass_node.material_override
		if not material:
			material = ShaderMaterial.new()
			var shader = preload("res://shaders/grass.shader")
			material.shader = shader
			grass_node.material_override = material
		
		if material is ShaderMaterial:
			material.set_shader_parameter("wind_speed", wind_speed)
			material.set_shader_parameter("wind_strength", wind_strength)
			material.set_shader_parameter("step_radius", step_radius)
			material.set_shader_parameter("step_decay_rate", step_decay_rate)
			material.set_shader_parameter("step_position", step_position)
