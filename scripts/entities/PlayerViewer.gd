class_name PlayerViewer extends CharacterBody3D

var game_manager: Node
var audio_manager: Node
var grass_field: Node

@export var move_speed := 5.0
@export var run_speed := 9.0
@export var jump_height := 9.0 # Сила прыжка
@export var mouse_sensitivity := 0.002
@export var acceleration := 8.0  # Для плавности разгона
@export var friction := 10.0      # Для плавности остановки

# Sway - flashlight
@export var sway_amount = 0.5
@export var sway_speed = 5.0

# Настройки шагов
@export var step_sounds: Array[AudioStream] = [
	preload("res://assets/audio/Concrete 1.wav"), 
	preload("res://assets/audio/Concrete 2.wav")
]
@export var grass_step_sounds: Array[AudioStream] = [
	preload("res://assets/audio/Grass 1.wav"),
	preload("res://assets/audio/Gravel 1.wav"),
	preload("res://assets/audio/Gravel - Run.wav")
]
@onready var step_player: AudioStreamPlayer3D = $StepSoundPlayer
@onready var grass_step_player: AudioStreamPlayer3D = $GrassStepSoundPlayer

var step_timer := 0.0
var base_step_interval := 0.6 # Интервал между шагами при ходьбе
var run_step_interval := 0.35 # Интервал при беге

@onready var camera: Camera3D = $Camera3D
@onready var audioX = $"/root/AudioManager"
@onready var flashlight: SpotLight3D = $Camera3D/SpotLight3D

#var input_dir = {"x":0,"y":0}
var sanity_drain_rate := 0.3
var last_sanity_damage := 0.0
var gravity: float = ProjectSettings.get_setting("physics/3d/default_gravity")

func _ready():
	game_manager = get_tree().current_scene.find_child("Main", true, false)
	grass_field = game_manager.find_child("GrassField", true, false) if game_manager else null
	
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _input(event):
	# Выход на Escape
	if event.is_action_pressed("ui_cancel"): # По умолчанию это Esc
		get_tree().quit()
	
	if event is InputEventKey and Input.is_action_pressed("flashlight"):
		flashlight.visible = !flashlight.visible
		audioX.flicker_player.play()
	
	# Поворот мыши
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * mouse_sensitivity)
		camera.rotate_x(-event.relative.y * mouse_sensitivity)
		camera.rotation.x = clamp(camera.rotation.x, deg_to_rad(-80), deg_to_rad(80))
func _physics_process(delta):
	# 1. Гравитация (работает всегда, когда мы не на полу)
	if not is_on_floor():
		velocity.y -= gravity * delta
	
	# 2. Обработка прыжка
	# "ui_accept" по умолчанию привязан к Пробелу (Space)
	if Input.is_action_just_pressed("ui_accept") and is_on_floor():
		velocity.y = jump_height
		audioX.play_entity_sound(camera.position)

	# 3. Скорость (Бег/Ходьба)
	var target_speed = run_speed if Input.is_action_pressed("run") else move_speed

	# 4. Направление движения (WASD)
	# Используем Input Map (настрой move_left/right/forward/back в настройках проекта)
	var input_dir = Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var direction = (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()
	
	# 5. Плавное движение
	if direction:
		velocity.x = lerp(velocity.x, direction.x * target_speed, acceleration * delta)
		velocity.z = lerp(velocity.z, direction.z * target_speed, acceleration * delta)
	else:
		velocity.x = move_toward(velocity.x, 0, friction * delta)
		velocity.z = move_toward(velocity.z, 0, friction * delta)
	
	if is_on_floor() and direction.length() > 0.1:
		# Определяем текущий темп (бег или ходьба)
		var current_interval = run_step_interval if Input.is_action_pressed("run") else base_step_interval
		
		step_timer += delta
		if step_timer >= current_interval:
			_play_step_sound()
			_play_grass_step_sound()
			step_timer = 0.0
	else:
		step_timer = 0.0
	# 6. Финальное применение движения
	move_and_slide()


func _play_step_sound():
	if step_sounds.size() > 0:
		# Выбираем случайный звук из массива для естественности
		step_player.stream = step_sounds.pick_random()
		# Немного меняем высоту звука (pitch), чтобы шаги не звучали одинаково
		step_player.pitch_scale = randf_range(0.9, 1.1)
		step_player.play()

func _play_grass_step_sound():
	if grass_step_sounds.size() > 0:
		# Выбираем случайный звук шагов по траве
		var grass_sound = grass_step_sounds.pick_random()
		grass_step_player.stream = grass_sound
		grass_step_player.pitch_scale = randf_range(0.95, 1.05)
		grass_step_player.volume_db = -8.0 + randf_range(-2.0, 2.0)
		grass_step_player.play()
		
		# Обновляем позицию шага для визуального эффекта травы
		if grass_field and grass_field.has_method("update_grass_step_position"):
			grass_field.update_grass_step_position(global_position)

func _process(_delta):
	_handle_flashlight_sway(_delta)
	_handle_sanity()

func _handle_flashlight_sway(delta):
	var mouse_input = Input.get_last_mouse_velocity()
	flashlight.rotation.y = lerp(flashlight.rotation.y, -mouse_input.x * sway_amount * 0.001, delta * sway_speed)
	flashlight.rotation.x = lerp(flashlight.rotation.x, -mouse_input.y * sway_amount * 0.001, delta * sway_speed)
	
	flashlight.rotation = flashlight.rotation.lerp(Vector3.ZERO, delta * sway_speed)

func _handle_sanity():
	var light_level = _get_light_at_position(global_position)
	var current_time = Time.get_ticks_msec()
	
	if light_level < 0.3 and current_time - last_sanity_damage > 1000:
		if game_manager and game_manager.has_method("decrease_sanity"):
			game_manager.decrease_sanity(sanity_drain_rate)
		last_sanity_damage = current_time

func _get_light_at_position(_pos: Vector3) -> float:
	return 0.5
