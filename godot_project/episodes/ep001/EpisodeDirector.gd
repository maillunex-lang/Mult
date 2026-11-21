extends Node3D
## Clear preschool storytelling timeline for EP-001 (180s / 30 FPS).

const DURATION := 180.0
const FPS := 30

@export var preview_mode: bool = false
@export var preview_seconds: float = 12.0

var camera: Camera3D
var camera_rig: Node3D
var beep: Node3D
var ball: Node3D
var basket: Node3D
var chair: Node3D
var fade_rect: ColorRect

var _world: Node3D
var _bound := false
var _finished := false
var _movie_mode := false
var _time := 0.0
var _shot := 0
var _holding_ball := false

# Soft-toy part refs for procedural animation
var _arm_l: Node3D
var _arm_r: Node3D
var _hand_l: Node3D
var _hand_r: Node3D
var _head: Node3D
var _antenna: Node3D
var _base_arm_l := Vector3.ZERO
var _base_arm_r := Vector3.ZERO
var _base_hand_l := Vector3.ZERO
var _base_hand_r := Vector3.ZERO
var _base_head := Vector3.ZERO


func _ready() -> void:
	_movie_mode = _detect_movie_mode()
	_configure_display()
	if _bound:
		_boot()


func _detect_movie_mode() -> bool:
	for a in OS.get_cmdline_args():
		if String(a).begins_with("--write-movie"):
			return true
	return false


func _configure_display() -> void:
	var mode := str(ProjectSettings.get_setting("bip/render/mode", "FINAL"))
	if OS.get_cmdline_user_args().has("--preview") or mode == "PREVIEW":
		preview_mode = true
	if preview_mode:
		DisplayServer.window_set_size(Vector2i(1280, 720))
		get_viewport().size = Vector2i(1280, 720)
	else:
		DisplayServer.window_set_size(Vector2i(1920, 1080))
		get_viewport().size = Vector2i(1920, 1080)


func _bind_nodes(world: Node3D) -> void:
	_world = world
	camera_rig = world.get_node_or_null("CameraRig") as Node3D
	camera = world.get_node_or_null("CameraRig/Camera3D") as Camera3D
	beep = world.get_node_or_null("Beep") as Node3D
	ball = world.get_node_or_null("RedBall") as Node3D
	basket = world.get_node_or_null("GreenBasket") as Node3D
	chair = world.get_node_or_null("YellowChair") as Node3D
	fade_rect = world.get_node_or_null("UI/Fade") as ColorRect
	_cache_beep_parts()
	_bound = true
	_boot()


func _cache_beep_parts() -> void:
	if beep == null:
		return
	_arm_l = _find_part(beep, "ArmL")
	_arm_r = _find_part(beep, "ArmR")
	_hand_l = _find_part(beep, "HandL")
	_hand_r = _find_part(beep, "HandR")
	_head = _find_part(beep, "Head")
	_antenna = _find_part(beep, "AntennaBall")
	if _arm_l: _base_arm_l = _arm_l.position
	if _arm_r: _base_arm_r = _arm_r.position
	if _hand_l: _base_hand_l = _hand_l.position
	if _hand_r: _base_hand_r = _hand_r.position
	if _head: _base_head = _head.position


func _find_part(root: Node, part_name: String) -> Node3D:
	if root.name == part_name and root is Node3D:
		return root as Node3D
	for c in root.get_children():
		var found := _find_part(c, part_name)
		if found:
			return found
	return null


func _boot() -> void:
	if fade_rect:
		fade_rect.color = Color(0, 0, 0, 0)
	print("[EP001] Soft-toy director ready. beep=", beep != null, " ball=", ball != null)


func _process(_delta: float) -> void:
	if _finished or not _bound:
		return
	if beep == null or ball == null or camera == null:
		return
	if _movie_mode:
		_time = float(Engine.get_frames_drawn()) / float(FPS)
	else:
		_time += _delta

	var end_t := preview_seconds if preview_mode else DURATION
	if _time >= end_t:
		_finish()
		return
	_update_timeline(_time)


func _finish() -> void:
	_finished = true
	print("[EP001] Finished at t=", _time)
	await get_tree().create_timer(0.05).timeout
	get_tree().quit()


func _update_timeline(t: float) -> void:
	var shot := _shot_at(t)
	if shot != _shot:
		_shot = shot
		print("[EP001] Shot ", shot, " @ ", snapped(t, 0.01))
	_update_beep(t, shot)
	_update_ball(t, shot)
	_update_camera(t, shot)
	_update_fade(t)


func _shot_at(t: float) -> int:
	if t < 6.0: return 1
	if t < 15.0: return 2
	if t < 25.0: return 3
	if t < 34.0: return 4
	if t < 45.0: return 5
	if t < 55.0: return 6
	if t < 65.0: return 7
	if t < 77.0: return 8
	if t < 85.0: return 9
	if t < 97.0: return 10
	if t < 111.0: return 11
	if t < 125.0: return 12
	if t < 137.0: return 13
	if t < 149.0: return 14
	if t < 160.0: return 15
	if t < 167.0: return 16
	if t < 175.0: return 17
	return 18


func _update_beep(t: float, shot: int) -> void:
	var pos := Vector3(0.35, 0.0, 0.55)
	# PI = face camera (+Z). Small offsets turn left/right for storytelling.
	var face := PI
	var yaw := face
	var action := "idle"

	match shot:
		1:
			pos = Vector3(0.35, 0.0, 0.55)
			yaw = face + deg_to_rad(-10)
			action = "wake"
		2:
			pos = Vector3(0.35, 0.0, 0.55)
			yaw = face + deg_to_rad(-5)
			action = "stretch"
		3:
			pos = Vector3(0.35, 0.0, 0.55)
			yaw = face + deg_to_rad(8)
			action = "wave"
		4, 5:
			pos = Vector3(0.25, 0.0, 0.35)
			yaw = face + deg_to_rad(35) # look toward ball
			action = "look"
		6:
			var u := clampf((t - 45.0) / 9.0, 0.0, 1.0)
			pos = Vector3(0.25, 0.0, 0.35).lerp(Vector3(0.15, 0.0, -0.05), _smooth(u))
			yaw = face + deg_to_rad(40)
			action = "walk"
		7:
			pos = Vector3(0.15, 0.0, -0.05)
			yaw = face + deg_to_rad(45)
			action = "push"
		8:
			pos = Vector3(0.2, 0.0, 0.0)
			yaw = face + deg_to_rad(25)
			action = "watch"
		9:
			pos = Vector3(0.25, 0.0, 0.05)
			yaw = face + deg_to_rad(-15)
			action = "surprise"
		10:
			pos = Vector3(0.4, 0.0, 0.15)
			yaw = face + deg_to_rad(-70)
			action = "look"
		11:
			var u2 := clampf((t - 97.0) / 13.0, 0.0, 1.0)
			pos = Vector3(0.4, 0.0, 0.15).lerp(Vector3(1.45, 0.0, -1.15), _smooth(u2))
			yaw = face + deg_to_rad(-100)
			action = "walk"
		12:
			pos = Vector3(1.45, 0.0, -1.15)
			yaw = face + deg_to_rad(-120)
			action = "happy"
		13:
			pos = Vector3(1.45, 0.0, -1.15)
			yaw = face + deg_to_rad(-130)
			action = "pickup"
			_holding_ball = true
		14:
			var u3 := clampf((t - 137.0) / 11.0, 0.0, 1.0)
			pos = Vector3(1.45, 0.0, -1.15).lerp(Vector3(-1.35, 0.0, 0.95), _smooth(u3))
			yaw = face + deg_to_rad(50)
			action = "walk"
			_holding_ball = true
		15:
			pos = Vector3(-1.35, 0.0, 0.95)
			yaw = face + deg_to_rad(20)
			action = "drop"
			_holding_ball = false
		16:
			pos = Vector3(-1.25, 0.0, 0.85)
			yaw = face
			action = "idle"
		17:
			pos = Vector3(-0.9, 0.0, 0.55)
			yaw = face + deg_to_rad(-8)
			action = "wave"
		18:
			pos = Vector3(-0.7, 0.0, 0.45)
			yaw = face
			action = "idle"

	# Soft bob
	var bob := sin(t * 2.2) * 0.008
	if action == "walk":
		bob = abs(sin(t * 7.0)) * 0.025
	pos.y = bob
	beep.position = beep.position.lerp(pos, 0.18)
	beep.rotation.y = lerp_angle(beep.rotation.y, yaw, 0.12)
	_animate_parts(t, action)


func _animate_parts(t: float, action: String) -> void:
	# Reset lean
	beep.rotation.x = lerp_angle(beep.rotation.x, 0.0, 0.1)
	beep.rotation.z = lerp_angle(beep.rotation.z, 0.0, 0.1)

	var arm_wave := 0.0
	var arm_push := 0.0
	var head_tilt := 0.0
	var stretch := 0.0

	match action:
		"wake":
			head_tilt = sin(clampf((t - 1.0) / 4.0, 0.0, 1.0) * PI) * 0.12
		"stretch":
			stretch = sin(clampf((t - 6.0) / 7.0, 0.0, 1.0) * PI) * 0.18
			beep.rotation.x = -stretch
			arm_wave = stretch * 0.8
		"wave":
			arm_wave = abs(sin(t * 5.0)) * 0.55
		"look":
			head_tilt = 0.1
		"walk":
			arm_wave = sin(t * 7.0) * 0.2
			beep.rotation.z = sin(t * 7.0) * 0.04
		"push":
			arm_push = 0.35
			beep.rotation.x = 0.12
		"watch":
			head_tilt = 0.08
		"surprise":
			head_tilt = -0.12
			arm_wave = 0.25
		"happy":
			arm_wave = abs(sin(t * 4.0)) * 0.35
			beep.rotation.z = sin(t * 4.0) * 0.05
		"pickup":
			arm_push = 0.45
			beep.rotation.x = 0.08
		"drop":
			arm_push = 0.25
			arm_wave = abs(sin(t * 5.0)) * 0.4

	if _head:
		_head.rotation.x = lerp_angle(_head.rotation.x, head_tilt, 0.15)
	if _arm_r:
		_arm_r.position = _base_arm_r + Vector3(0, arm_wave * 0.08, 0)
		_arm_r.rotation.z = lerp_angle(_arm_r.rotation.z, -arm_wave - arm_push, 0.2)
	if _hand_r:
		_hand_r.position = _base_hand_r + Vector3(0, arm_wave * 0.12 + arm_push * 0.05, arm_push * 0.08)
	if _arm_l:
		_arm_l.position = _base_arm_l + Vector3(0, arm_wave * 0.05, 0)
		_arm_l.rotation.z = lerp_angle(_arm_l.rotation.z, arm_wave * 0.6 + arm_push * 0.5, 0.2)
	if _hand_l:
		_hand_l.position = _base_hand_l + Vector3(0, arm_wave * 0.08 + arm_push * 0.05, arm_push * 0.08)
	if _antenna:
		_antenna.position.y = lerp(_antenna.position.y, 0.77 + sin(t * 3.0) * 0.01, 0.2)


func _update_ball(t: float, shot: int) -> void:
	var p := Vector3(0.1, 0.0, -0.2)
	var spin := 0.0
	if shot <= 6:
		p = Vector3(0.1, 0.0, -0.2)
	elif shot == 7:
		p = Vector3(0.2, 0.0, -0.35)
	elif shot == 8:
		var u := clampf((t - 65.0) / 12.0, 0.0, 1.0)
		p = Vector3(0.2, 0.0, -0.35).lerp(Vector3(1.85, 0.0, -1.55), _smooth(u))
		spin = 10.0
	elif shot == 9 or shot == 10:
		# Partially behind chair — still visible for toddlers
		p = Vector3(1.95, 0.0, -1.70)
	elif shot == 11:
		p = Vector3(1.95, 0.0, -1.70)
	elif shot == 12:
		p = Vector3(1.70, 0.0, -1.40)
	elif shot == 13 or shot == 14:
		p = beep.global_position + Vector3(0.0, 0.42, 0.16)
	elif shot >= 15:
		if basket:
			p = basket.global_position + Vector3(0.0, 0.20, 0.0)
		else:
			p = Vector3(-1.55, 0.20, 1.1)

	var blend := 0.22 if shot < 13 else 0.4
	ball.global_position = ball.global_position.lerp(p, blend)
	if spin > 0.0:
		ball.rotate_x(spin * 0.025)


func _update_camera(_t: float, shot: int) -> void:
	# Always keep Beep readable; avoid extreme close-ups of fragments.
	var cam_pos := Vector3(0.0, 1.35, 4.0)
	var look := beep.global_position + Vector3(0, 0.35, 0)
	var fov := 42.0

	match shot:
		1:
			cam_pos = Vector3(0.2, 1.45, 4.2)
			look = Vector3(0.2, 0.55, 0.1)
			fov = 46.0
		2, 3:
			cam_pos = Vector3(1.0, 1.15, 2.6)
			look = beep.global_position + Vector3(0, 0.4, 0)
			fov = 38.0
		4:
			cam_pos = Vector3(-0.5, 1.25, 3.0)
			look = (beep.global_position + ball.global_position) * 0.5 + Vector3(0, 0.25, 0)
			fov = 42.0
		5:
			cam_pos = Vector3(0.4, 0.7, 1.4)
			look = ball.global_position + Vector3(0, 0.1, 0)
			fov = 34.0
		6, 7:
			cam_pos = Vector3(-1.0, 1.15, 2.5)
			look = (beep.global_position + ball.global_position) * 0.5 + Vector3(0, 0.25, 0)
			fov = 40.0
		8:
			cam_pos = Vector3(-0.3, 1.25, 3.2)
			look = ball.global_position + Vector3(0, 0.1, 0)
			fov = 44.0
		9:
			cam_pos = Vector3(0.9, 1.1, 2.0)
			look = beep.global_position + Vector3(0, 0.4, 0)
			fov = 36.0
		10:
			cam_pos = Vector3(0.3, 1.35, 2.8)
			look = Vector3(1.7, 0.35, -1.4)
			fov = 42.0
		11, 12, 13:
			cam_pos = Vector3(0.1, 1.3, 2.2)
			look = beep.global_position + Vector3(0, 0.35, 0)
			fov = 40.0
		14:
			cam_pos = Vector3(0.3, 1.45, 3.4)
			look = beep.global_position + Vector3(0, 0.35, 0)
			fov = 46.0
		15:
			cam_pos = Vector3(0.0, 1.3, 3.2)
			look = basket.global_position + Vector3(0, 0.25, 0) if basket else Vector3(-1.5, 0.25, 1.0)
			fov = 42.0
		16:
			cam_pos = Vector3(-1.0, 0.95, 2.3)
			look = basket.global_position + Vector3(0, 0.25, 0) if basket else Vector3(-1.5, 0.25, 1.0)
			fov = 34.0
		17:
			cam_pos = Vector3(0.2, 1.15, 2.5)
			look = beep.global_position + Vector3(0, 0.4, 0)
			fov = 36.0
		18:
			cam_pos = Vector3(0.2, 1.7, 4.8)
			look = Vector3(0.0, 0.7, 0.0)
			fov = 50.0

	camera_rig.global_position = camera_rig.global_position.lerp(cam_pos, 0.08)
	camera.look_at(look, Vector3.UP)
	camera.fov = lerp(camera.fov, fov, 0.1)


func _update_fade(t: float) -> void:
	if fade_rect == null:
		return
	var a := 0.0
	if t < 1.0:
		a = 1.0 - clampf(t / 1.0, 0.0, 1.0)
	var end_t := preview_seconds if preview_mode else DURATION
	if t > end_t - 3.5:
		a = clampf((t - (end_t - 3.5)) / 3.5, 0.0, 1.0)
	fade_rect.color = Color(0, 0, 0, a)


func _smooth(x: float) -> float:
	var t := clampf(x, 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t)
