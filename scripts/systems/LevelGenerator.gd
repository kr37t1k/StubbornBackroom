# scripts/systems/LevelGenerator.gd
# ТЕКУЩЕЕ: Отключён в пользу GrassField для лиминального пространства
# Этот скрипт оставлен для совместимости, но генерация отключена

class_name LevelGenerator extends Node3D

func _ready():
	# Отключаем старую генерацию комнат
	print("LevelGenerator отключён. Используется GrassField для бесконечного поля.")
	pass
	# generate_initial_chunks(Vector3.ZERO)  # Закомментировано

# Старый код генерации комнат закомментирован
# Удалён для экономии места и избежания конфликтов
# Все функции генерации удалены
