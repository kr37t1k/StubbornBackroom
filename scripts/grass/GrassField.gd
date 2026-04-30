# scripts/grass/GrassField.gd
# Генерация бесконечного поля с травой, холмами и оврагами

class_name GrassField extends Node3D

# Настройки ландшафта
@export var chunk_size: float = 32.0
@export var load_radius: int = 3
@export var grass_density: float = 30.0  # Травинки на квадратный метр

# Настройки шума для ландшафта
@export var noise_scale: float = 0.03
@export var height_multiplier: float = 1.5
@export var ravine_depth: float = 2.0
@export var ravine_frequency: float = 0.08

# Ветер
@export var wind_speed: float = 0.8
@export var wind_strength: float = 0.4
@export var step_radius: float = 4.0
@export var step_decay_rate: float = 3.0

var loaded_chunks: Dictionary = {}  # {Vector2i: Node3D}
var noise: FastNoiseLite
var step_position: Vector3 = Vector3.ZERO
var step_active: bool = false
var step_timer: float = 0.0
var rng: RandomNumberGenerator

@onready var player: Node3D = get_parent().find_child("Player", true, false)

func _ready():
	# Попробуем использовать FastNoiseLite, если нет - используем простой рандом
	if FastNoiseLite:
		noise = FastNoiseLite.new()
		noise.seed = randi()
		noise.frequency = noise_scale
		noise.noise_type = FastNoiseLite.TYPE_FBM
	else:
		print("FastNoiseLite не найден, использую простой генератор")
		rng = RandomNumberGenerator.new()
		rng.seed = randi()
	
	await get_tree().process_frame
	print("GrassField: инициализация, noise_seed = ", noise.seed if noise else rng.seed)
	generate_initial_chunks()
	print("GrassField: сгенерировано чанков = ", loaded_chunks.size())

func _physics_process(delta):
	# Обновляем таймер шага
	if step_active:
		step_timer += delta
		if step_timer > 0.3:
			step_active = false
			step_timer = 0.0
	
	# Обновляем позицию шага для эффекта травы
	if player:
		# Проверяем, делает ли игрок шаг (по скорости)
		var player_speed = player.velocity.length()
		if player_speed > 0.5 and player.is_on_floor():
			# Это упрощённая проверка - в идеале нужно отслеживать шаги из PlayerViewer
			pass

func generate_initial_chunks():
	var start_pos = player.global_position if player else Vector3(0, 5, 0)
	var player_chunk = _world_to_chunk(start_pos)
	for x in range(-load_radius, load_radius + 1):
		for z in range(-load_radius, load_radius + 1):
			var chunk_pos = Vector2i(player_chunk.x + x, player_chunk.y + z)
			_load_chunk(chunk_pos)

func regenerate_around_player(player_pos: Vector3):
	var player_chunk = _world_to_chunk(player_pos)
	
	# Unload distant chunks
	var to_unload = []
	for chunk_pos in loaded_chunks:
		if chunk_pos.distance_to(player_chunk) > load_radius + 1:
			to_unload.append(chunk_pos)
	for pos in to_unload:
		_unload_chunk(pos)
	
	# Load new chunks
	for x in range(-load_radius, load_radius + 1):
		for z in range(-load_radius, load_radius + 1):
			var target = Vector2i(player_chunk.x + x, player_chunk.y + z)
			if not loaded_chunks.has(target):
				_load_chunk(target)

func _load_chunk(chunk_pos: Vector2i):
	var chunk = _create_grass_chunk(chunk_pos)
	chunk.name = "GrassChunk_" + str(chunk_pos)
	chunk.position = Vector3(chunk_pos.x * chunk_size, 0, chunk_pos.y * chunk_size)
	add_child(chunk)
	loaded_chunks[chunk_pos] = chunk
	print("GrassField: загружен чанк ", chunk_pos, " в позиции ", chunk.position)

func _unload_chunk(chunk_pos: Vector2i):
	if loaded_chunks.has(chunk_pos):
		loaded_chunks[chunk_pos].queue_free()
		loaded_chunks.erase(chunk_pos)

func _create_grass_chunk(chunk_pos: Vector2i) -> Node3D:
	var chunk = Node3D.new()
	
	print("GrassField: создание чанка ", chunk_pos)
	
	# Создаём ландшафт с холмами и оврагами
	var terrain = _create_terrain_mesh(chunk_pos)
	chunk.add_child(terrain)
	print("GrassField: ландшафт создан")
	
	# Добавляем траву (временное отключение для отладки)
	# var grass = _create_grass_multimesh(chunk_pos)
	# chunk.add_child(grass)
	# print("GrassField: трава создана")
	
	# Создаём коллизию для ландшафта
	var collision = _create_terrain_collision(chunk_pos)
	chunk.add_child(collision)
	print("GrassField: коллизия создана")
	
	return chunk

func _create_terrain_mesh(chunk_pos: Vector2i) -> MeshInstance3D:
	var terrain = MeshInstance3D.new()
	var mesh = ArrayMesh.new()
	
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	var indices := PackedInt32Array()
	
	var segments = 32  # Количество сегментов на сторону
	var step_x = chunk_size / segments
	var step_z = chunk_size / segments
	
	# Генерация вершин
	for z in range(segments + 1):
		for x in range(segments + 1):
			var world_x = chunk_pos.x * chunk_size + x * step_x
			var world_z = chunk_pos.y * chunk_size + z * step_z
			
			# Высота от шума (холмы)
			var height = noise.get_noise_2d(world_x, world_z) * height_multiplier
			
			# Смещаем высоту чтобы базовый уровень был примерно 0
			height = height + 0.5
			
			# Добавляем овраги (дополнительный шум с высокой частотой)
			var ravine_factor = sin(world_x * ravine_frequency) * sin(world_z * ravine_frequency)
			ravine_factor = max(ravine_factor, 0.0)  # Только положительные значения
			
			# Овраги уходят вниз от базового уровня
			if ravine_factor > 0.2:
				height -= (ravine_factor - 0.2) * ravine_depth * 1.5
			
			# Локальные координаты для чанка
			vertices.append(Vector3(x * step_x, height, z * step_z))
			normals.append(Vector3.UP)
			uvs.append(Vector2(x / segments, z / segments))
	
	# Генерация индексов
	for z in range(segments):
		for x in range(segments):
			var a = z * (segments + 1) + x
			var b = z * (segments + 1) + x + 1
			var c = (z + 1) * (segments + 1) + x
			var d = (z + 1) * (segments + 1) + x + 1
			
			# Первый треугольник
			indices.append(a)
			indices.append(c)
			indices.append(b)
			
			# Второй треугольник
			indices.append(b)
			indices.append(c)
			indices.append(d)
	
	# Расчёт нормалей
	for i in range(vertices.size()):
		var normal = _calculate_normal(vertices, i, segments + 1)
		normals[i] = normal
	
	# Создание массивов
	var arrays = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_INDEX] = indices
	
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	
	# Материал для земли
	var material = StandardMaterial3D.new()
	material.albedo_color = Color(0.15, 0.4, 0.1)  # Тёмно-зелёный цвет земли
	material.roughness = 1.0
	material.metallic = 0.0
	
	terrain.mesh = mesh
	terrain.material_override = material
	
	return terrain

func _calculate_normal(vertices: PackedVector3Array, index: int, width: int) -> Vector3:
	if index < 0 or index >= vertices.size():
		return Vector3.UP
	
	var p = vertices[index]
	
	# Находим соседние точки
	var neighbors := PackedVector3Array()
	
	var x = index % width
	var z = index / width
	
	# Соседи
	if x > 0:
		neighbors.append(vertices[index - 1])
	if x < width - 1:
		neighbors.append(vertices[index + 1])
	if z > 0:
		neighbors.append(vertices[index - width])
	if z < (vertices.size() / width) - 1:
		neighbors.append(vertices[index + width])
	
	if neighbors.size() < 2:
		return Vector3.UP
	
	# Вычисляем нормаль через векторное произведение
	var sum_normal = Vector3.ZERO
	for i in range(neighbors.size()):
		for j in range(i + 1, neighbors.size()):
			var edge1 = neighbors[i] - p
			var edge2 = neighbors[j] - p
			sum_normal += edge1.cross(edge2)
	
	return sum_normal.normalized() if sum_normal.length() > 0 else Vector3.UP

func _create_grass_multimesh(chunk_pos: Vector2i) -> MultiMeshInstance3D:
	var grass = MultiMeshInstance3D.new()
	grass.name = "Grass"
	
	var grass_mesh = _create_grass_mesh()
	
	var mm = MultiMesh.new()
	mm.mesh = grass_mesh
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.color_format = MultiMesh.COLOR_3D
	
	# Количество травинки на чанк
	var grass_count = int(chunk_size * chunk_size * grass_density)
	mm.instance_count = grass_count
	
	# Генерируем позиции травинки
	for i in range(grass_count):
		var local_x = randf() * chunk_size
		var local_z = randf() * chunk_size
		var world_x = chunk_pos.x * chunk_size + local_x
		var world_z = chunk_pos.y * chunk_size + local_z
		
		# Получаем высоту ландшафта в этой точке
		var height = _get_terrain_height(world_x, world_z)
		
		var t = Transform3D.IDENTITY
		t.origin = Vector3(local_x, height, local_z)
		
		# Случайный поворот и масштаб для естественности
		var scale = randf_range(0.8, 1.2)
		t = t.scaled(Vector3(scale, scale, scale))
		t = t.rotated(Vector3(0, 1, 0), randf() * TAU)
		
		mm.set_instance_transform(i, t)
		
		# Цвет с вариацией (зелёные оттенки)
		var color_var = randf_range(0.8, 1.2)
		var grass_color = Color(0.2 * color_var, 0.5 * color_var, 0.15 * color_var, 1.0)
		mm.set_instance_color(i, grass_color)
	
	grass.multimesh = mm
	
	# Применяем шейдер травы
	var material = ShaderMaterial.new()
	var shader = preload("res://shaders/grass.shader")
	material.shader = shader
	material.set_shader_parameter("wind_speed", wind_speed)
	material.set_shader_parameter("wind_strength", wind_strength)
	material.set_shader_parameter("step_radius", step_radius)
	material.set_shader_parameter("step_decay_rate", step_decay_rate)
	material.set_shader_parameter("step_position", Vector3(0, 0, 0))
	
	grass.material_override = material
	
	return grass

func _create_grass_mesh() -> Mesh:
	var mesh = ArrayMesh.new()
	var verts := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	var indices := PackedInt32Array()
	
	# Простая модель травинки (двусторонняя плоскость)
	var height = 0.3
	var width = 0.05
	
	# Основная плоскость травы
	verts.append(Vector3(-width/2, 0, 0))
	verts.append(Vector3(-width/2, height, 0))
	verts.append(Vector3(width/2, height, 0))
	verts.append(Vector3(width/2, 0, 0))
	
	normals.append(Vector3(0, 0, -1))
	normals.append(Vector3(0, 0, -1))
	normals.append(Vector3(0, 0, -1))
	normals.append(Vector3(0, 0, -1))
	
	uvs.append(Vector2(0, 0))
	uvs.append(Vector2(0, 1))
	uvs.append(Vector2(1, 1))
	uvs.append(Vector2(1, 0))
	
	indices.append(0)
	indices.append(1)
	indices.append(2)
	indices.append(0)
	indices.append(2)
	indices.append(3)
	
	var arrays = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_INDEX] = indices
	
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return mesh

func _create_terrain_collision(chunk_pos: Vector2i) -> Node:
	var collision = StaticBody3D.new()
	collision.name = "TerrainCollision"
	
	# Создаём коллизию для ландшафта
	var height_map = HeightMapShape3D.new()
	var segments = 32
	
	var height_data := PackedFloat32Array()
	var width = segments + 1
	
	for z in range(segments + 1):
		for x in range(segments + 1):
			var world_x = chunk_pos.x * chunk_size + x * (chunk_size / segments)
			var world_z = chunk_pos.y * chunk_size + z * (chunk_size / segments)
			
			var height = _get_terrain_height(world_x, world_z)
			height_data.append(height)
	
	# Простая коллизия (в идеале нужен более точный подход)
	var mesh_collision = MeshInstance3D.new()
	var mesh = ArrayMesh.new()
	
	var vertices := PackedVector3Array()
	var indices := PackedInt32Array()
	
	for z in range(segments + 1):
		for x in range(segments + 1):
			var world_x = chunk_pos.x * chunk_size + x * (chunk_size / segments)
			var world_z = chunk_pos.y * chunk_size + z * (chunk_size / segments)
			
			var height = _get_terrain_height(world_x, world_z)
			vertices.append(Vector3(world_x, height, world_z))
	
	for z in range(segments):
		for x in range(segments):
			var a = z * width + x
			var b = z * width + x + 1
			var c = (z + 1) * width + x
			var d = (z + 1) * width + x + 1
			
			indices.append(a)
			indices.append(c)
			indices.append(b)
			indices.append(b)
			indices.append(c)
			indices.append(d)
	
	var arrays = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_INDEX] = indices
	
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	
	var concave = ConcavePolygonShape3D.new()
	concave.set_faces(vertices.to_packed_vector3_array() if vertices.size() > 0 else PackedVector3Array())
	
	var shape = CollisionShape3D.new()
	shape.shape = concave
	collision.add_child(shape)
	
	return collision

func _get_terrain_height(world_x: float, world_z: float) -> float:
	var height = 0.0
	
	if noise:
		height = noise.get_noise_2d(world_x, world_z) * height_multiplier
	else:
		# Простой псевдослучайный "шум" если FastNoiseLite не доступен
		height = sin(world_x * 0.1) * cos(world_z * 0.1) * height_multiplier
	
	# Смещаем высоту чтобы базовый уровень был примерно 0
	height = height + 0.5
	
	# Овраги - делаем их более плавными
	var ravine_factor = sin(world_x * ravine_frequency) * sin(world_z * ravine_frequency)
	ravine_factor = max(ravine_factor, 0.0)
	
	# Овраги уходят вниз от базового уровня
	if ravine_factor > 0.2:
		height -= (ravine_factor - 0.2) * ravine_depth * 1.5
	
	return height

func _world_to_chunk(pos: Vector3) -> Vector2i:
	return Vector2i(floor(pos.x / chunk_size), floor(pos.z / chunk_size))

func get_step_position() -> Vector3:
	return step_position

func update_grass_step_position(pos: Vector3):
	step_position = pos
	step_active = true
	step_timer = 0.0
	
	# Обновляем шейдер травы во всех чанках
	for chunk_pos in loaded_chunks:
		var chunk = loaded_chunks[chunk_pos]
		var grass = chunk.find_child("Grass", true, false)
		if grass and grass is MultiMeshInstance3D and grass.material_override:
			var material = grass.material_override
			if material is ShaderMaterial:
				material.set_shader_parameter("step_position", pos)
