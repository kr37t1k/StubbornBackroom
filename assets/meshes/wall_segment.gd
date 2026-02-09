#@tool
extends Node
class_name WallSegmentMesh


func _init():
	# Generate 4m wide × 3.2m tall vertical plane
	var mesh := ArrayMesh.new()
	
	# Vertices (clockwise from bottom-left)
	var verts := PackedVector3Array([
		Vector3(-2.0, 0.0, 0.0),   # BL
		Vector3( 2.0, 0.0, 0.0),   # BR
		Vector3( 2.0, 3.2, 0.0),   # TR
		Vector3(-2.0, 3.2, 0.0)    # TL
	])
	
	# UVs (full texture coverage)
	var uvs := PackedVector2Array([
		Vector2(0, 1),
		Vector2(1, 1),
		Vector2(1, 0),
		Vector2(0, 0)
	])
	
	# Indices (two triangles)
	var indices := PackedInt32Array([0, 1, 2, 0, 2, 3])
	
	# Normals (facing +Z direction)
	var normals := PackedVector3Array([
		Vector3(0, 0, 1),
		Vector3(0, 0, 1),
		Vector3(0, 0, 1),
		Vector3(0, 0, 1)
	])
	
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = verts
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_INDEX] = indices
	
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	mesh.surface_set_name(0, "wall_surface")
	
	# Save as reusable resource
	ResourceSaver.save(mesh, "res://assets/meshes/wall_segment.tres")
