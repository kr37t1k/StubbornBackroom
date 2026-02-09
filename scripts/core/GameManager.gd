# scripts/GameManager.gd
class_name GameManager extends Node

@onready var player = $PlayerViewer
@onready var level_generator = $LevelGenerator
@onready var audio_manager = $AudioManager

var current_sanity: float = 100.0
var is_game_over := false

func _ready():
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	level_generator.generate_initial_chunks(player.global_position)

func decrease_sanity(amount: float):
	current_sanity = clamp(current_sanity - amount, 0, 100)
	if current_sanity <= 0 and not is_game_over:
		trigger_game_over()

func trigger_game_over():
	is_game_over = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	get_tree().paused = true
	# Show game over screen here later

func save_game():
	var save_data = {
		"position": player.global_position,
		"sanity": current_sanity,
		"timestamp": Time.get_unix_time_from_system()
	}
	ResourceSaver.save(save_data, "user://save.dat")

func load_game():
	if ResourceLoader.exists("user://save.dat"):
		var data = ResourceLoader.load("user://save.dat")
		player.global_position = data.position
		current_sanity = data.sanity
		level_generator.regenerate_around_player(player.global_position)
