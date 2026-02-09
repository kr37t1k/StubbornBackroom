# Path: addons/audio_manager/AudioManager.gd
@tool
extends Node

# Audio paths (all optional - game runs without them)
const HUM_PATH := "res://assets/audio/atomiste.wav"
const FLICKER_PATH := "res://assets/audio/light_flicker.ogg"
const ENTITY_PATH := "res://assets/audio/entity_approach.ogg"

var hum_player: AudioStreamPlayer3D
var flicker_player: AudioStreamPlayer3D
var is_muted := false

func _ready():
	# Create players dynamically (no scene dependency)
	hum_player = _create_3d_player("HumPlayer", HUM_PATH, -15, false)  # Changed autoplay to false to prevent immediate playback
	if hum_player:
		hum_player.play()  # Start playing after creation if successful
	flicker_player = _create_3d_player("FlickerPlayer", FLICKER_PATH, -20, false)
	

func _create_3d_player(name3d: String, path: String, volume_db: float, autoplay: bool) -> AudioStreamPlayer3D:
	if not FileAccess.file_exists(path):  # Check if file exists before loading
		printerr("Audio file does not exist: ", path)
		return null
		
	var player := AudioStreamPlayer3D.new()
	player.name = name3d
	player.stream = load(path)
	player.volume_db = volume_db
	player.autoplay = autoplay
	player.max_distance = 50.0
	add_child(player)
	return player


func play_flicker_sound(position: Vector3):
	if is_muted: return
	flicker_player.global_position = position
	flicker_player.play()

func toggle_mute():
	is_muted = not is_muted
	AudioServer.set_bus_mute(AudioServer.get_bus_index("Master"), is_muted)
