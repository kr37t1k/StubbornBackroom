# scripts/entities/PlayerController.gd
class_name PlayerViewer extends CharacterBody3D

@onready var game_manager = $GameManager
@onready var audio_manager = $AudioManager

@export var move_speed := 5.0
@export var run_speed := 9.0
@export var mouse_sensitivity := 0.002

var camera: Camera3D
var sanity_drain_rate := 0.3  # per second in darkness
var last_sanity_damage := 0.0

func _ready():
	camera = $Camera3D
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _input(event):
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * mouse_sensitivity)
		camera.rotate_x(-event.relative.y * mouse_sensitivity)
		camera.rotation.x = clamp(camera.rotation.x, deg_to_rad(-80), deg_to_rad(80))

func _process(delta):
	# Sanity drain based on light level
	var light_level = _get_light_at_position(global_position)
	if light_level < 0.3 and Time.get_ticks_msec() - last_sanity_damage > 1000:
		game_manager.decrease_sanity(sanity_drain_rate)
		last_sanity_damage = Time.get_ticks_msec()

func _physics_process(delta):
	var input_dir = Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var direction = (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
	
	if Input.is_action_pressed("run"):
		velocity.x = direction.x * run_speed
		velocity.z = direction.z * run_speed
	else:
		velocity.x = direction.x * move_speed
		velocity.z = direction.z * move_speed
	
	move_and_slide()

func _get_light_at_position(pos: Vector3) -> float:
	# Approximate using baked lightmap or simple distance to nearest light
	# For dev speed: just return 0.2 (always slightly dark for tension)
	return 0.2
