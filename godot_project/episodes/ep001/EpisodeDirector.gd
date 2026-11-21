extends Node3D
## Deterministic 180s timeline director for EP-001 "Бип и красный мячик".
## Uses Movie Maker frame clock when available so playback is FPS-independent.

const DURATION := 180.0
const FPS := 30
const TOTAL_FRAMES := 5400

@export var preview_mode: bool = false
@export var preview_seconds: float = 12.0

var _time := 0.0
var _finished := false
var _fade := 0.0

var camera: Camera3D
var camera_rig: Node3D
var beep: Node3D
var ball: Node3D
var basket: Node3D
var chair: Node3D
var fade_rect: ColorRect
var world_env: WorldEnvironment
var _world: Node3D

var _beep_anim: AnimationPlayer
var _shot := 0
var _last_anim := ""
var _holding_ball := false
var _bound := false
var _movie_mode := false


func _ready() -> void:
	_movie_mode = _detect_movie_mode()
	_configure_display()
	# Nodes may be bound deferred from SceneBuilder
	if _bound:
		_boot()


func _detect_movie_mode() -> bool:
	for a in OS.get_cmdline_args():
		if String(a).begins_with("--write-movie"):
			return true
	# User args after --
	for a in OS.get_cmdline_user_args():
		if String(a).begins_with("--write-movie"):
			return true
	return false


func _bind_nodes(world: Node3D) -> void:
	_world = world
	camera_rig = world.get_node_or_null("CameraRig") as Node3D
	camera = world.get_node_or_null("CameraRig/Camera3D") as Camera3D
	beep = world.get_node_or_null("Beep") as Node3D
	ball = world.get_node_or_null("RedBall") as Node3D
	basket = world.get_node_or_null("GreenBasket") as Node3D
	chair = world.get_node_or_null("YellowChair") as Node3D
	fade_rect = world.get_node_or_null("UI/Fade") as ColorRect
	world_env = world.get_node_or_null("WorldEnvironment") as WorldEnvironment
	_bound = true
	_boot()


func _boot() -> void:
	_find_beep_anim()
	_apply_shot(1, 0.0)
	if fade_rect:
		fade_rect.color = Color(0, 0, 0, 0)
	print("[EP001] Director ready. preview=", preview_mode, " beep=", beep != null, " ball=", ball != null)


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


func _find_beep_anim() -> void:
	_beep_anim = _find_anim_player(beep)
	if _beep_anim:
		print("[EP001] Beep animations: ", _beep_anim.get_animation_list())


func _find_anim_player(node: Node) -> AnimationPlayer:
	if node == null:
		return null
	if node is AnimationPlayer:
		return node
	for c in node.get_children():
		var found := _find_anim_player(c)
		if found:
			return found
	return null


func _process(_delta: float) -> void:
	if _finished or not _bound:
		return
	if beep == null or ball == null or camera == null:
		return
	# Deterministic clock: with --fixed-fps / Movie Maker, drive from frame index.
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
	# Shot ranges from script
	var shot := _shot_at(t)
	if shot != _shot:
		_shot = shot
		print("[EP001] Shot ", shot, " @ ", snapped(t, 0.01))

	_update_camera(t, shot)
	_update_beep(t, shot)
	_update_ball(t, shot)
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


func _apply_shot(_s: int, _t: float) -> void:
	pass


func _play_beep(anim_keywords: Array, fallback_idle := true) -> void:
	if _beep_anim == null:
		return
	var list := _beep_anim.get_animation_list()
	for key in anim_keywords:
		for name in list:
			if String(name).to_lower().find(String(key).to_lower()) >= 0:
				if _last_anim != name:
					_beep_anim.play(name)
					_last_anim = name
				return
	if fallback_idle:
		for name in list:
			if String(name).to_lower().find("idle") >= 0 or String(name).to_lower().find("standing") >= 0:
				if _last_anim != name:
					_beep_anim.play(name)
					_last_anim = name
				return


func _update_beep(t: float, shot: int) -> void:
	# Base pose zones
	var pos := Vector3(0.4, 0.0, 0.6)
	var yaw := 0.0
	var bob := sin(t * 2.0) * 0.01

	match shot:
		1:
			pos = Vector3(0.5, 0.0, 0.8)
			yaw = deg_to_rad(-20)
			_play_beep(["idle", "standing"])
			# wake stretch hint via slight lean
			beep.rotation.x = sin(clampf((t - 1.0) / 4.0, 0.0, 1.0) * PI) * 0.08
		2:
			pos = Vector3(0.5, 0.0, 0.8)
			yaw = deg_to_rad(-10)
			_play_beep(["idle", "standing"])
			beep.rotation.x = -0.15 * sin(clampf((t - 6.0) / 6.0, 0.0, 1.0) * PI)
		3:
			pos = Vector3(0.45, 0.0, 0.7)
			yaw = deg_to_rad(10)
			_play_beep(["wave", "thumbsup", "yes"])
			beep.rotation.x = 0.0
		4:
			pos = Vector3(0.35, 0.0, 0.5)
			yaw = deg_to_rad(-35)
			_play_beep(["idle"])
		5:
			pos = Vector3(0.35, 0.0, 0.5)
			yaw = deg_to_rad(-40)
			_play_beep(["idle"])
		6:
			# walk to ball
			var u := clampf((t - 45.0) / 9.0, 0.0, 1.0)
			pos = Vector3(0.35, 0.0, 0.5).lerp(Vector3(0.15, 0.0, -0.15), u)
			yaw = deg_to_rad(-50)
			_play_beep(["walk", "running"])
		7:
			pos = Vector3(0.15, 0.0, -0.15)
			yaw = deg_to_rad(-60)
			_play_beep(["punch", "yes", "idle"])
			# push gesture
			beep.rotation.x = 0.12
		8:
			pos = Vector3(0.2, 0.0, -0.1)
			yaw = deg_to_rad(-20)
			_play_beep(["idle"])
			beep.rotation.x = 0.0
		9:
			pos = Vector3(0.25, 0.0, 0.0)
			yaw = deg_to_rad(30)
			_play_beep(["no", "idle"])
		10:
			pos = Vector3(0.3, 0.0, 0.1)
			yaw = deg_to_rad(70)
			_play_beep(["idle"])
		11:
			var u2 := clampf((t - 97.0) / 12.0, 0.0, 1.0)
			pos = Vector3(0.3, 0.0, 0.1).lerp(Vector3(1.55, 0.0, -1.35), u2)
			yaw = deg_to_rad(110)
			_play_beep(["walk"])
		12:
			pos = Vector3(1.55, 0.0, -1.35)
			yaw = deg_to_rad(140)
			_play_beep(["yes", "thumbsup", "idle"])
		13:
			pos = Vector3(1.55, 0.0, -1.35)
			yaw = deg_to_rad(150)
			_play_beep(["idle"])
			_holding_ball = true
			beep.rotation.x = 0.05
		14:
			var u3 := clampf((t - 137.0) / 11.0, 0.0, 1.0)
			pos = Vector3(1.55, 0.0, -1.35).lerp(Vector3(-1.5, 0.0, 0.9), u3)
			yaw = deg_to_rad(-40)
			_play_beep(["walk"])
			_holding_ball = true
		15:
			pos = Vector3(-1.5, 0.0, 0.9)
			yaw = deg_to_rad(-20)
			_play_beep(["yes", "dance", "idle"])
			_holding_ball = false
			beep.rotation.x = 0.0
		16:
			pos = Vector3(-1.5, 0.0, 0.9)
			yaw = deg_to_rad(0)
			_play_beep(["idle"])
		17:
			pos = Vector3(-1.2, 0.0, 0.6)
			yaw = deg_to_rad(20)
			_play_beep(["wave"])
		18:
			pos = Vector3(-1.0, 0.0, 0.5)
			yaw = deg_to_rad(0)
			_play_beep(["idle", "standing"])

	pos.y = bob
	beep.position = beep.position.lerp(pos, 0.2)
	beep.rotation.y = lerp_angle(beep.rotation.y, yaw, 0.15)


func _update_ball(t: float, shot: int) -> void:
	var p := Vector3(0.0, 0.14, -0.35)
	var spinning := 0.0

	if shot <= 6:
		p = Vector3(0.0, 0.14, -0.35)
	elif shot == 7:
		# just pushed
		p = Vector3(0.05, 0.14, -0.4)
	elif shot == 8:
		var u := clampf((t - 65.0) / 12.0, 0.0, 1.0)
		p = Vector3(0.05, 0.14, -0.4).lerp(Vector3(1.85, 0.14, -1.55), smoothstep(0.0, 1.0, u))
		spinning = u * 8.0
	elif shot == 9 or shot == 10:
		p = Vector3(1.95, 0.14, -1.65) # partially behind chair
		spinning = 0.2
	elif shot == 11:
		p = Vector3(1.95, 0.14, -1.65)
	elif shot == 12:
		p = Vector3(1.75, 0.14, -1.45)
	elif shot == 13 or shot == 14:
		# held by Beep — follow hands height
		p = beep.global_position + Vector3(0.05, 0.42, 0.18)
	elif shot >= 15:
		# in basket
		if basket:
			p = basket.global_position + Vector3(0.0, 0.22, 0.0)
		else:
			p = Vector3(-1.7, 0.22, 1.0)

	ball.global_position = ball.global_position.lerp(p, 0.25 if shot < 13 else 0.45)
	if spinning != 0.0:
		ball.rotate_x(spinning * 0.03)


func _update_camera(t: float, shot: int) -> void:
	var cam_pos := Vector3(0.0, 1.35, 3.2)
	var look := Vector3(0.2, 0.55, 0.2)
	var fov := 42.0

	match shot:
		1:
			cam_pos = Vector3(0.0, 1.6, 4.5)
			look = Vector3(0.2, 0.55, 0.0)
			fov = 50.0
		2:
			cam_pos = Vector3(0.9, 1.15, 2.8)
			look = beep.global_position + Vector3(0, 0.35, 0)
			fov = 40.0
		3:
			cam_pos = Vector3(0.7, 1.0, 2.1)
			look = beep.global_position + Vector3(0, 0.4, 0)
			fov = 36.0
		4:
			cam_pos = Vector3(-0.6, 1.3, 3.0)
			look = Vector3(0.15, 0.35, 0.1)
			fov = 42.0
		5:
			cam_pos = Vector3(0.35, 0.55, 1.1)
			look = ball.global_position
			fov = 34.0
		6:
			cam_pos = Vector3(-1.0, 1.2, 2.6)
			look = beep.global_position + Vector3(0, 0.3, 0)
			fov = 42.0
		7:
			cam_pos = Vector3(-0.8, 1.05, 2.2)
			look = Vector3(0.1, 0.3, -0.2)
			fov = 40.0
		8:
			cam_pos = Vector3(-0.2, 1.2, 3.0)
			look = ball.global_position
			fov = 44.0
		9:
			cam_pos = Vector3(0.9, 1.1, 1.8)
			look = beep.global_position + Vector3(0, 0.4, 0)
			fov = 36.0
		10:
			cam_pos = Vector3(0.4, 1.35, 2.4)
			look = Vector3(1.6, 0.35, -1.3)
			fov = 42.0
		11:
			cam_pos = Vector3(-0.3, 1.4, 2.5)
			look = beep.global_position + Vector3(0, 0.35, 0)
			fov = 44.0
		12:
			cam_pos = Vector3(0.2, 1.2, 1.2)
			look = Vector3(1.6, 0.4, -1.3)
			fov = 40.0
		13:
			cam_pos = Vector3(0.4, 1.15, 1.0)
			look = beep.global_position + Vector3(0, 0.4, 0)
			fov = 38.0
		14:
			cam_pos = Vector3(0.2, 1.45, 3.2)
			look = beep.global_position + Vector3(0, 0.35, 0)
			fov = 46.0
		15:
			cam_pos = Vector3(-0.2, 1.3, 3.0)
			look = basket.global_position + Vector3(0, 0.25, 0) if basket else Vector3(-1.6, 0.25, 1.0)
			fov = 42.0
		16:
			cam_pos = Vector3(-1.2, 0.85, 2.2)
			look = basket.global_position + Vector3(0, 0.25, 0) if basket else Vector3(-1.6, 0.25, 1.0)
			fov = 34.0
		17:
			cam_pos = Vector3(0.0, 1.15, 2.4)
			look = beep.global_position + Vector3(0, 0.4, 0)
			fov = 36.0
		18:
			cam_pos = Vector3(0.2, 1.85, 5.0)
			look = Vector3(0.0, 0.7, 0.0)
			fov = 52.0

	camera_rig.global_position = camera_rig.global_position.lerp(cam_pos, 0.08)
	camera.look_at(look, Vector3.UP)
	camera.fov = lerp(camera.fov, fov, 0.1)


func _update_fade(t: float) -> void:
	if fade_rect == null:
		return
	var a := 0.0
	if t < 1.2:
		a = 1.0 - clampf(t / 1.2, 0.0, 1.0)
	var end_t := preview_seconds if preview_mode else DURATION
	if t > end_t - 4.0:
		a = clampf((t - (end_t - 4.0)) / 4.0, 0.0, 1.0)
	fade_rect.color = Color(0, 0, 0, a)


func smoothstep(e0: float, e1: float, x: float) -> float:
	var t := clampf((x - e0) / (e1 - e0), 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t)
