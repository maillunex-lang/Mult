extends Node3D
## Builds the EP-001 set from imported GLB assets and soft lighting.


func _ready() -> void:
	_build_environment()
	_spawn_room()
	_spawn_furniture()
	_spawn_props()
	_spawn_beep()
	_spawn_camera_and_ui()
	var director_script := load("res://episodes/ep001/EpisodeDirector.gd")
	var director := Node3D.new()
	director.name = "Director"
	director.set_script(director_script)
	add_child(director)
	director.call_deferred("_bind_nodes", self)


func _build_environment() -> void:
	var we := WorldEnvironment.new()
	we.name = "WorldEnvironment"
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.62, 0.78, 0.90)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.98, 0.94, 0.88)
	env.ambient_light_energy = 0.35
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.tonemap_exposure = 0.95
	env.adjustment_enabled = true
	env.adjustment_contrast = 1.05
	env.adjustment_saturation = 1.08
	we.environment = env
	add_child(we)

	var sun := DirectionalLight3D.new()
	sun.name = "Sun"
	sun.light_color = Color(1.0, 0.97, 0.90)
	sun.light_energy = 0.85
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 20.0
	sun.rotation_degrees = Vector3(-48, -28, 0)
	add_child(sun)

	var fill := OmniLight3D.new()
	fill.name = "Fill"
	fill.light_color = Color(0.85, 0.92, 1.0)
	fill.light_energy = 0.35
	fill.omni_range = 10.0
	fill.position = Vector3(-1.8, 2.0, 1.8)
	add_child(fill)

	var window_light := OmniLight3D.new()
	window_light.name = "WindowLight"
	window_light.light_color = Color(0.92, 0.96, 1.0)
	window_light.light_energy = 0.9
	window_light.omni_range = 7.0
	window_light.position = Vector3(0.0, 1.5, -1.8)
	add_child(window_light)


func _spawn_room() -> void:
	var room := _instance_glb("res://locations/beep_room/room_shell.glb", "Room")
	if room:
		room.position = Vector3.ZERO
		_style_room(room)
	else:
		_fallback_room()


func _style_room(room: Node) -> void:
	for mi in _all_mesh_instances(room):
		var n := String(mi.name).to_lower()
		var mat := StandardMaterial3D.new()
		mat.roughness = 0.85
		if n.find("floor") >= 0:
			mat.albedo_color = Color(0.76, 0.60, 0.40)
			mat.roughness = 0.7
		elif n.find("rug") >= 0 or n.find("mint") >= 0:
			mat.albedo_color = Color(0.42, 0.78, 0.70)
			mat.roughness = 0.95
		elif n.find("sky") >= 0:
			mat.albedo_color = Color(0.55, 0.78, 0.98)
			mat.emission_enabled = true
			mat.emission = Color(0.45, 0.7, 0.95)
			mat.emission_energy_multiplier = 0.8
		elif n.find("glass") >= 0:
			mat.albedo_color = Color(0.65, 0.82, 0.95, 0.55)
			mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			mat.roughness = 0.15
		elif n.find("ceil") >= 0:
			mat.albedo_color = Color(0.94, 0.92, 0.88)
		elif n.find("base") >= 0 or n.find("frame") >= 0 or n.find("win") >= 0:
			mat.albedo_color = Color(0.92, 0.90, 0.84)
		else:
			mat.albedo_color = Color(0.90, 0.84, 0.74) # cream walls
		mi.material_override = mat


func _fallback_room() -> void:
	var floor_mesh := MeshInstance3D.new()
	floor_mesh.name = "Floor"
	var box := BoxMesh.new()
	box.size = Vector3(6, 0.1, 5)
	floor_mesh.mesh = box
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(0.78, 0.62, 0.42)
	mat.roughness = 0.75
	floor_mesh.material_override = mat
	floor_mesh.position.y = -0.05
	add_child(floor_mesh)


func _spawn_furniture() -> void:
	var chair := _instance_glb("res://props/toys/yellow_armchair.glb", "YellowChair")
	if chair:
		chair.position = Vector3(1.7, 0.0, -1.4)
		chair.rotation_degrees.y = -145
		chair.scale = Vector3(1.0, 1.0, 1.0)
		_tint_meshes(chair, Color(0.95, 0.82, 0.22))

	var shelf := _instance_glb("res://props/furniture/bookcaseOpenLow.glb", "Shelf")
	if shelf == null:
		shelf = _instance_glb("res://props/furniture/bookcaseOpen.glb", "Shelf")
	if shelf:
		shelf.position = Vector3(-2.5, 0.0, -1.9)
		shelf.scale = Vector3(1.8, 1.8, 1.8)
		shelf.rotation_degrees.y = 90

	var lamp := _instance_glb("res://props/furniture/lampRoundFloor.glb", "Lamp")
	if lamp:
		lamp.position = Vector3(2.35, 0.0, 1.4)
		lamp.scale = Vector3(1.5, 1.5, 1.5)

	var bear := _instance_glb("res://props/furniture/bear.glb", "Bear")
	if bear:
		bear.position = Vector3(-2.2, 0.62, -1.75)
		bear.scale = Vector3(1.3, 1.3, 1.3)

	var books := _instance_glb("res://props/furniture/books.glb", "Books")
	if books:
		books.position = Vector3(-2.4, 0.95, -1.85)
		books.scale = Vector3(1.6, 1.6, 1.6)

	var side := _instance_glb("res://props/furniture/sideTable.glb", "SideTable")
	if side:
		side.position = Vector3(2.35, 0.0, -0.5)
		side.scale = Vector3(1.4, 1.4, 1.4)

	# Keep set uncluttered: one yellow armchair is enough for EP-001.


func _spawn_props() -> void:
	var ball := _instance_glb("res://props/ball/red_ball.glb", "RedBall")
	if ball:
		ball.position = Vector3(0.05, 0.0, -0.25)

	var basket := _instance_glb("res://props/basket/green_basket.glb", "GreenBasket")
	if basket:
		basket.position = Vector3(-1.6, 0.0, 1.05)
		_tint_meshes(basket, Color(0.32, 0.72, 0.40))

	var blocks := _instance_glb("res://props/blocks/color_blocks.glb", "Blocks")
	if blocks:
		blocks.position = Vector3(-0.7, 0.0, 0.55)


func _spawn_beep() -> void:
	# Prefer source Quaternius robot (reliable skinning) and scale to ~65cm.
	var beep := _instance_glb("res://characters/beep/quaternius_source.glb", "Beep")
	if beep == null:
		beep = _instance_glb("res://characters/beep/beep.glb", "Beep")
	if beep:
		# Original Quaternius height ~5.0 units -> 0.65m
		beep.scale = Vector3(0.13, 0.13, 0.13)
		beep.position = Vector3(0.35, 0.0, 0.55)
		_recolor_beep(beep)
		_add_antenna(beep)


func _recolor_beep(beep: Node) -> void:
	var turq := Color("75D4E8")
	var soft := Color(0.86, 0.90, 0.92)
	var dark := Color(0.07, 0.07, 0.1)
	for mi in _all_mesh_instances(beep):
		var n: String = String(mi.name).to_lower()
		var mat := StandardMaterial3D.new()
		mat.roughness = 0.55
		mat.metallic = 0.04
		# Body / limbs / head -> turquoise soft plastic
		if n.find("eye") >= 0 or n.find("black") >= 0:
			mat.albedo_color = dark
		elif n.find("head") >= 0 or n.find("torso") >= 0 or n.find("arm") >= 0 \
				or n.find("leg") >= 0 or n.find("foot") >= 0 or n.find("hand") >= 0 \
				or n.find("shoulder") >= 0 or n.find("main") >= 0:
			mat.albedo_color = turq
		else:
			# Default most robot meshes to turquoise; keep very dark as eyes/joints
			var mesh: Mesh = mi.mesh
			var sample := Color(0.6, 0.35, 0.1)
			if mesh != null and mesh.get_surface_count() > 0:
				var src: Material = mesh.surface_get_material(0)
				if src is BaseMaterial3D:
					sample = (src as BaseMaterial3D).albedo_color
			if sample.v < 0.18:
				mat.albedo_color = dark
			elif sample.r > 0.35 and sample.g < 0.5:
				mat.albedo_color = turq
			else:
				mat.albedo_color = soft if sample.g > 0.35 else turq
		mi.material_override = mat


func _add_antenna(beep: Node3D) -> void:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(1.0, 0.84, 0.18)
	mat.roughness = 0.4
	var stem := MeshInstance3D.new()
	stem.name = "AntennaStem"
	var cyl := CylinderMesh.new()
	cyl.top_radius = 0.012
	cyl.bottom_radius = 0.012
	cyl.height = 0.09
	stem.mesh = cyl
	stem.material_override = mat
	# Local space of unscaled Quaternius (~5u tall). Parent scale 0.13 -> ~65cm.
	cyl.top_radius = 0.08
	cyl.bottom_radius = 0.08
	cyl.height = 0.55
	stem.mesh = cyl
	stem.position = Vector3(0, 4.15, 0)
	beep.add_child(stem)
	var tip := MeshInstance3D.new()
	tip.name = "AntennaBall"
	var sph := SphereMesh.new()
	sph.radius = 0.18
	sph.height = 0.36
	tip.mesh = sph
	tip.material_override = mat
	tip.position = Vector3(0, 4.55, 0)
	beep.add_child(tip)


func _tint_meshes(root: Node, color: Color) -> void:
	for mi in _all_mesh_instances(root):
		var mat := StandardMaterial3D.new()
		mat.albedo_color = color
		mat.roughness = 0.7
		mi.material_override = mat


func _all_mesh_instances(root: Node) -> Array:
	var out: Array = []
	_collect_mi(root, out)
	return out


func _collect_mi(n: Node, out: Array) -> void:
	if n is MeshInstance3D:
		out.append(n)
	for c in n.get_children():
		_collect_mi(c, out)


func _spawn_camera_and_ui() -> void:
	var rig := Node3D.new()
	rig.name = "CameraRig"
	rig.position = Vector3(0.0, 1.5, 4.2)
	add_child(rig)
	var cam := Camera3D.new()
	cam.name = "Camera3D"
	cam.current = true
	cam.fov = 45
	cam.near = 0.05
	cam.far = 50
	rig.add_child(cam)

	var ui := CanvasLayer.new()
	ui.name = "UI"
	add_child(ui)
	var fade := ColorRect.new()
	fade.name = "Fade"
	fade.color = Color(0, 0, 0, 0)
	fade.set_anchors_preset(Control.PRESET_FULL_RECT)
	fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ui.add_child(fade)


func _instance_glb(path: String, node_name: String) -> Node3D:
	if not ResourceLoader.exists(path):
		push_warning("Missing asset: " + path)
		return null
	var packed := load(path)
	if packed == null or not (packed is PackedScene):
		push_warning("Failed load: " + path)
		return null
	var inst: Node = (packed as PackedScene).instantiate()
	inst.name = node_name
	add_child(inst)
	return inst as Node3D
