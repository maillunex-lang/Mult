extends Node3D
## Clear Soft Toy preschool set — forced readable colors for toddlers.


func _ready() -> void:
	_build_environment()
	_spawn_room()
	_spawn_furniture()
	_spawn_props()
	_spawn_beep()
	_spawn_camera_and_ui()
	var director := Node3D.new()
	director.name = "Director"
	director.set_script(load("res://episodes/ep001/EpisodeDirector.gd"))
	add_child(director)
	director.call_deferred("_bind_nodes", self)


func _build_environment() -> void:
	var we := WorldEnvironment.new()
	we.name = "WorldEnvironment"
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.55, 0.72, 0.88)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.95, 0.92, 0.88)
	env.ambient_light_energy = 0.42
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.tonemap_exposure = 0.9
	env.adjustment_enabled = true
	env.adjustment_contrast = 1.08
	env.adjustment_saturation = 1.2
	we.environment = env
	add_child(we)

	var sun := DirectionalLight3D.new()
	sun.name = "Sun"
	sun.light_color = Color(1.0, 0.97, 0.9)
	sun.light_energy = 0.28
	sun.shadow_enabled = true
	sun.shadow_blur = 4.0
	sun.shadow_opacity = 0.45
	sun.directional_shadow_max_distance = 18.0
	sun.rotation_degrees = Vector3(-58, -20, 0)
	add_child(sun)

	var fill := OmniLight3D.new()
	fill.name = "Fill"
	fill.light_color = Color(0.85, 0.92, 1.0)
	fill.light_energy = 0.55
	fill.omni_range = 12.0
	fill.position = Vector3(-1.2, 2.2, 1.5)
	add_child(fill)

	var warm := OmniLight3D.new()
	warm.name = "Warm"
	warm.light_color = Color(1.0, 0.9, 0.75)
	warm.light_energy = 0.5
	warm.omni_range = 9.0
	warm.position = Vector3(1.4, 1.9, -0.3)
	add_child(warm)


func _spawn_room() -> void:
	var room := _instance_glb("res://locations/beep_room/room_shell.glb", "Room")
	if room:
		room.position = Vector3.ZERO
		_paint_room(room)


func _paint_room(room: Node) -> void:
	for mi in _meshes(room):
		var n := String(mi.name).to_lower()
		var mat := StandardMaterial3D.new()
		mat.roughness = 0.85
		if n.find("floor") >= 0:
			mat.albedo_color = Color(0.72, 0.55, 0.34)
			mat.roughness = 0.7
		elif n.find("rug") >= 0 or n.find("mint") >= 0:
			mat.albedo_color = Color(0.32, 0.72, 0.62)
			mat.roughness = 0.95
		elif n.find("sky") >= 0:
			mat.albedo_color = Color(0.45, 0.72, 0.95)
			mat.emission_enabled = true
			mat.emission = Color(0.4, 0.65, 0.95)
			mat.emission_energy_multiplier = 0.6
		elif n.find("grass") >= 0:
			mat.albedo_color = Color(0.35, 0.65, 0.30)
		elif n.find("glass") >= 0:
			mat.albedo_color = Color(0.7, 0.85, 0.95, 0.45)
			mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			mat.roughness = 0.12
		elif n.find("ceil") >= 0:
			mat.albedo_color = Color(0.90, 0.88, 0.84)
		elif n.find("base") >= 0 or n.find("frame") >= 0 or n.find("win") >= 0:
			mat.albedo_color = Color(0.88, 0.84, 0.76)
		else:
			mat.albedo_color = Color(0.86, 0.78, 0.66) # cream walls — darker so readable
		mi.material_override = mat


func _spawn_furniture() -> void:
	var chair := _instance_glb("res://props/toys/yellow_armchair.glb", "YellowChair")
	if chair:
		chair.position = Vector3(1.75, 0.0, -1.45)
		chair.rotation_degrees.y = -150
		_paint_all(chair, Color(0.98, 0.78, 0.12), 0.7)

	var shelf := _instance_glb("res://props/toys/shelf.glb", "Shelf")
	if shelf:
		shelf.position = Vector3(-2.45, 0.0, -1.9)
		_paint_named(shelf)

	var lamp := _instance_glb("res://props/toys/floor_lamp.glb", "Lamp")
	if lamp:
		lamp.position = Vector3(2.35, 0.0, 1.35)
		_paint_named(lamp)

	var teddy := _instance_glb("res://props/toys/teddy.glb", "Teddy")
	if teddy:
		teddy.position = Vector3(-2.35, 0.48, -1.85)
		_paint_all(teddy, Color(0.70, 0.45, 0.25), 0.85)


func _spawn_props() -> void:
	var ball := _instance_glb("res://props/ball/red_ball.glb", "RedBall")
	if ball:
		ball.position = Vector3(0.1, 0.0, -0.2)
		_paint_all(ball, Color(0.92, 0.10, 0.10), 0.4)

	var basket := _instance_glb("res://props/basket/green_basket.glb", "GreenBasket")
	if basket:
		basket.position = Vector3(-1.55, 0.0, 1.1)
		_paint_all(basket, Color(0.22, 0.68, 0.34), 0.7)

	var blocks := _instance_glb("res://props/blocks/color_blocks.glb", "Blocks")
	if blocks:
		blocks.position = Vector3(-0.55, 0.0, 0.55)
		_paint_blocks(blocks)


func _spawn_beep() -> void:
	var beep := _instance_glb("res://characters/beep/beep_soft.glb", "Beep")
	if beep == null:
		return
	beep.position = Vector3(0.35, 0.0, 0.55)
	# Face toward camera (camera sits on +Z looking at origin).
	beep.rotation_degrees.y = 180.0
	beep.scale = Vector3.ONE
	_paint_beep(beep)


func _paint_beep(beep: Node) -> void:
	var turq := Color("75D4E8")
	var soft := Color(0.93, 0.96, 0.98)
	var dark := Color(0.08, 0.09, 0.12)
	var yellow := Color(1.0, 0.82, 0.12)
	var blush := Color(1.0, 0.55, 0.55)
	var mouth := Color(0.4, 0.15, 0.18)
	for mi in _meshes(beep):
		var n := String(mi.name).to_lower()
		var mat := StandardMaterial3D.new()
		mat.roughness = 0.55
		mat.metallic = 0.0
		if n.find("pupil") >= 0 or n.find("mouth") >= 0:
			mat.albedo_color = dark if n.find("pupil") >= 0 else mouth
			mat.roughness = 0.35
		elif n.find("eye") >= 0 or n.find("shine") >= 0 or n.find("belly") >= 0 or n.find("hand") >= 0 or n.find("foot") >= 0:
			mat.albedo_color = soft
		elif n.find("antenna") >= 0:
			mat.albedo_color = yellow
			mat.roughness = 0.4
		elif n.find("cheek") >= 0:
			mat.albedo_color = blush
		else:
			mat.albedo_color = turq
		mi.material_override = mat


func _paint_all(root: Node, color: Color, rough: float) -> void:
	for mi in _meshes(root):
		var mat := StandardMaterial3D.new()
		mat.albedo_color = color
		mat.roughness = rough
		mi.material_override = mat


func _paint_named(root: Node) -> void:
	for mi in _meshes(root):
		var n := String(mi.name).to_lower()
		var mat := StandardMaterial3D.new()
		mat.roughness = 0.65
		if n.find("book") >= 0:
			# keep varied via hash of name
			var h: int = abs(hash(n)) % 5
			var cols := [
				Color(0.9, 0.3, 0.3), Color(0.3, 0.5, 0.9), Color(0.95, 0.8, 0.15),
				Color(0.35, 0.75, 0.4), Color(0.8, 0.4, 0.8)
			]
			mat.albedo_color = cols[h]
		elif n.find("shade") >= 0:
			mat.albedo_color = Color(1.0, 0.95, 0.8)
			mat.emission_enabled = true
			mat.emission = Color(1.0, 0.95, 0.8)
			mat.emission_energy_multiplier = 0.25
		else:
			mat.albedo_color = Color(0.72, 0.55, 0.34)
		mi.material_override = mat


func _paint_blocks(root: Node) -> void:
	var cols := [
		Color(0.95, 0.28, 0.32), Color(0.28, 0.52, 0.95), Color(0.98, 0.8, 0.12),
		Color(0.32, 0.78, 0.38), Color(0.85, 0.42, 0.85)
	]
	var i := 0
	for mi in _meshes(root):
		var mat := StandardMaterial3D.new()
		mat.albedo_color = cols[i % cols.size()]
		mat.roughness = 0.65
		mi.material_override = mat
		i += 1


func _meshes(root: Node) -> Array:
	var out: Array = []
	_collect(root, out)
	return out


func _collect(n: Node, out: Array) -> void:
	if n is MeshInstance3D:
		out.append(n)
	for c in n.get_children():
		_collect(c, out)


func _spawn_camera_and_ui() -> void:
	var rig := Node3D.new()
	rig.name = "CameraRig"
	rig.position = Vector3(0.0, 1.35, 4.0)
	add_child(rig)
	var cam := Camera3D.new()
	cam.name = "Camera3D"
	cam.current = true
	cam.fov = 42.0
	cam.near = 0.05
	cam.far = 40.0
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
	var packed = load(path)
	if packed == null or not (packed is PackedScene):
		push_warning("Failed load: " + path)
		return null
	var inst: Node = (packed as PackedScene).instantiate()
	inst.name = node_name
	add_child(inst)
	return inst as Node3D
