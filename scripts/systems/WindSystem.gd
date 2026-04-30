# scripts/systems/WindSystem.gd
# Система ветра с фоновым шумом и звуком шуршания травы

class_name WindSystem extends Node3D

@export var wind_noise_volume: float = -25.0
@export var wind_gust_variation: float = 5.0
@export var wind_change_speed: float = 0.1
@export var wind_stream: AudioStream = preload("res://assets/audio/atomiste.wav")

var current_wind_volume: float = 0.0
var target_wind_volume: float = 0.0
var wind_timer: float = 0.0

@onready var wind_audio_player: AudioStreamPlayer3D = $WindAudioPlayer

func _ready():
	if wind_audio_player:
		if wind_stream:
			wind_audio_player.stream = wind_stream
		wind_audio_player.volume_db = wind_noise_volume
		wind_audio_player.play()

func _process(delta):
	# Плавно меняем громкость ветра для эффекта порывов
	wind_timer += delta
	
	if randf() < 0.01:  # 1% шанс изменения цели каждую секунду
		target_wind_volume = randf_range(wind_noise_volume - wind_gust_variation, wind_noise_volume + wind_gust_variation)
	
	# Плавно приближаемся к цели
	current_wind_volume = lerp(current_wind_volume, target_wind_volume, delta * wind_change_speed)
	
	if wind_audio_player:
		wind_audio_player.volume_db = current_wind_volume

func set_wind_intensity(intensity: float):
	# intensity от 0.0 до 1.0
	target_wind_volume = lerp(-35.0, -15.0, intensity)