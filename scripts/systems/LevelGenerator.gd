# scripts/systems/LevelGenerator.gd
class_name LevelGenerator extends Node3D

const CHUNK_SIZE := 16.0
const LOAD_RADIUS := 2  # Chunks around player
var loaded_chunks := {}  # {Vector2i: Node3D}

func generate_initial_chunks(center_pos: Vector3):
	var center_chunk = _world_to_chunk(center_pos)
	for x in range(-LOAD_RADIUS, LOAD_RADIUS + 1):
		for z in range(-LOAD_RADIUS, LOAD_RADIUS + 1):
			_load_chunk(Vector2i(center_chunk.x + x, center_chunk.z + z))

func regenerate_around_player(player_pos: Vector3):
	var player_chunk = _world_to_chunk(player_pos)
	
	# Unload distant chunks
	var to_unload = []
	for chunk_pos in loaded_chunks:
		if chunk_pos.distance_to(player_chunk) > LOAD_RADIUS + 1:
			to_unload.append(chunk_pos)
	for pos in to_unload:
		_unload_chunk(pos)
	
	# Load new chunks
	for x in range(-LOAD_RADIUS, LOAD_RADIUS + 1):
		for z in range(-LOAD_RADIUS, LOAD_RADIUS + 1):
			var target = Vector2i(player_chunk.x + x, player_chunk.z + z)
			if not loaded_chunks.has(target):
				_load_chunk(target)

func _load_chunk(chunk_pos: Vector2i):
	var chunk = _create_chunk_mesh(chunk_pos)
	chunk.name = "Chunk_" + str(chunk_pos)
	add_child(chunk)
	loaded_chunks[chunk_pos] = chunk

func _unload_chunk(chunk_pos: Vector2i):
	if loaded_chunks.has(chunk_pos):
		loaded_chunks[chunk_pos].queue_free()
		loaded_chunks.erase(chunk_pos)

func _create_chunk_mesh(chunk_pos: Vector2i) -> Node3D:
	var chunk = Node3D.new()
	
	# Single modular mesh reused via MultiMesh (critical for perf)
	var floor = _create_floor_multimesh(chunk_pos)
	var walls = _create_walls_multimesh(chunk_pos)
	
	chunk.add_child(floor)
	chunk.add_child(walls)
	chunk.global_position = Vector3(chunk_pos.x * CHUNK_SIZE, 0, chunk_pos.y * CHUNK_SIZE)
	
	return chunk

func _create_floor_multimesh(chunk_pos: Vector2i) -> MultiMeshInstance3D:
	var mm = MultiMesh.new()
	mm.mesh = preload("res://assets/meshes/WallBlack.obj")
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.instance_count = 16  # 4x4 grid
	
	var mmi = MultiMeshInstance3D.new()
	mmi.multimesh = mm
	
	# Position instances in grid
	var idx = 0
	for x in 4:
		for z in 4:
			var transform = Transform3D.IDENTITY
			transform.origin = Vector3(x * 4.0, 0, z * 4.0)
			mm.set_instance_transform(idx, transform)
			idx += 1
	
	return mmi
	
func _create_walls_multimesh(chunk_pos: Vector2i) -> MultiMeshInstance3D:
	# Wall configuration
	const WALL_HEIGHT := 3.2  # Slightly uneven ceiling for unease
	const SEGMENT_LENGTH := 4.0
	const CHUNK_SEGMENTS := 4  # 4x4 grid of 4m segments = 16m chunk
	
	# Preload modular wall segment (single 4m x 3.2m plane facing +Z)
	# Create this once in Blender: default plane scaled to (4.0, 0.1, 3.2)
	
	# Setup MultiMesh
	var mm := MultiMesh.new()
	mm.mesh = preload("res://assets/meshes/WallBlack.obj")
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true  # For moisture variation via vertex colors
	
	# Calculate instance count: perimeter only (no interior walls)
	# 4 sides × 4 segments per side = 16 wall segments per chunk
	mm.instance_count = CHUNK_SEGMENTS * 4
	
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = mm
	mmi.name = "Walls"
	
	# Apply procedural yellow shader with moisture variatio
	var material := preload("res://assets/shaders/yellow_wall.tres")  # ShaderMaterial resource
	#if material:
		#mmi.material_override = material
	
	# Position wall segments around chunk perimeter
	var instance_idx := 0
	var chunk_world_pos := Vector3(chunk_pos.x * CHUNK_SIZE, 0, chunk_pos.y * CHUNK_SIZE)
	
	# Helper: slightly vary height for unease (procedural but deterministic per chunk)
	var height_seed := hash(chunk_pos) * 0.01
	
	# North wall (facing -Z)
	for i in range(CHUNK_SEGMENTS):
		var transform := Transform3D.IDENTITY
		transform.origin = Vector3(
			i * SEGMENT_LENGTH,
			0,
			0  # North edge of chunk
		)
		# Slight height variation (0-8cm) for "settling" effect
		var height_offset := sin((chunk_pos.x + i) * 0.7 + height_seed) * 0.08
		transform = transform.scaled(Vector3(1.0, 1.0 + height_offset, 1.0))
		transform = transform.rotated(Vector3(0, 1, 0), deg_to_rad(180))  # Face inward (-Z)
		mm.set_instance_transform(instance_idx, transform)
		
		# Vertex color for moisture intensity (darker = damper)
		var moisture := sin((chunk_pos.x * 13.0 + i * 3.7) * 0.4) * 0.3 + 0.4
		mm.set_instance_color(instance_idx, Color(moisture, moisture, moisture, 1.0))
		
		instance_idx += 1
	
	# East wall (facing -X)
	for i in range(CHUNK_SEGMENTS):
		var transform := Transform3D.IDENTITY
		transform.origin = Vector3(
			CHUNK_SIZE - 0.1,  # Offset slightly inward to avoid z-fighting with adjacent chunks
			0,
			i * SEGMENT_LENGTH
		)
		var height_offset := sin((chunk_pos.y + i) * 0.9 + height_seed * 1.3) * 0.06
		transform = transform.scaled(Vector3(1.0, 1.0 + height_offset, 1.0))
		transform = transform.rotated(Vector3(0, 1, 0), deg_to_rad(90))  # Face inward (-X)
		mm.set_instance_transform(instance_idx, transform)
		
		var moisture := sin((chunk_pos.y * 17.0 + i * 2.9) * 0.5) * 0.4 + 0.3
		mm.set_instance_color(instance_idx, Color(moisture, moisture, moisture, 1.0))
		
		instance_idx += 1
	
	# South wall (facing +Z)
	for i in range(CHUNK_SEGMENTS):
		var transform := Transform3D.IDENTITY
		transform.origin = Vector3(
			i * SEGMENT_LENGTH,
			0,
			CHUNK_SIZE - 0.1  # Offset inward
		)
		var height_offset := sin((chunk_pos.x * 2.3 + i * 1.1) * 0.6 + height_seed * 0.7) * 0.07
		transform = transform.scaled(Vector3(1.0, 1.0 + height_offset, 1.0))
		# No rotation needed (default faces +Z)
		mm.set_instance_transform(instance_idx, transform)
		
		var moisture := sin((chunk_pos.x * 19.0 + i * 4.1) * 0.3) * 0.35 + 0.45
		mm.set_instance_color(instance_idx, Color(moisture, moisture, moisture, 1.0))
		
		instance_idx += 1
	
	# West wall (facing +X)
	for i in range(CHUNK_SEGMENTS):
		var transform := Transform3D.IDENTITY
		transform.origin = Vector3(
			0,
			0,
			i * SEGMENT_LENGTH
		)
		var height_offset := sin((chunk_pos.y * 3.1 + i * 0.8) * 0.7 + height_seed * 1.8) * 0.09
		transform = transform.scaled(Vector3(1.0, 1.0 + height_offset, 1.0))
		transform = transform.rotated(Vector3(0, 1, 0), deg_to_rad(-90))  # Face inward (+X)
		mm.set_instance_transform(instance_idx, transform)
		
		var moisture := sin((chunk_pos.y * 23.0 + i * 3.3) * 0.6) * 0.4 + 0.35
		mm.set_instance_color(instance_idx, Color(moisture, moisture, moisture, 1.0))
		
		instance_idx += 1
	
	# Position entire wall system at chunk origin
	mmi.global_position = chunk_world_pos
	
	return mmi

# Deterministic hash for chunk-based variation (avoids expensive noise textures)
func hash(v: Vector2i) -> int:
	var x = v.x * 1664525 + 1013904223
	var y = v.y * 1567890 + 987654321
	return (x ^ y) & 0x7fffffff
	
func _world_to_chunk(pos: Vector3) -> Vector2i:
	return Vector2i(floor(pos.x / CHUNK_SIZE), floor(pos.z / CHUNK_SIZE))
