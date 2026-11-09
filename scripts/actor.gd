class_name Actor
extends Node2D
## 칸 단위로 움직이는 것 (주인공·몬스터·사람). 한 칸 32픽셀.

const T := 32

var world: Node2D
var cell := Vector2i.ZERO
var facing := Vector2i(0, 1)
var moving := false
var step_time := 0.42
var spr: Sprite2D
var mat: ShaderMaterial
var anim_frame := 0
var walk_phase := 0
var act_until := 0.0      # 공격·주문 자세를 보여 줄 때까지
var act_frame := 0
var name_lbl: Label

func place(c: Vector2i) -> void:
	cell = c
	position = cell_pos(c)

static func cell_pos(c: Vector2i) -> Vector2:
	return Vector2(c.x * T + T / 2.0, c.y * T + T - 2)

func make_sprite(tex: Texture2D, hf := 7, vf := 3, off := Vector2(0, -22)) -> Sprite2D:
	spr = Sprite2D.new()
	spr.texture = tex
	spr.hframes = hf
	spr.vframes = vf
	spr.offset = off
	mat = Fx.flash_material()
	spr.material = mat
	add_child(spr)
	return spr

func add_name(text: String, col: Color, y := -52.0) -> void:
	name_lbl = UI.label(text, 10, col, true, true)
	name_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_lbl.size = Vector2(120, 12)
	name_lbl.position = Vector2(-60, y)
	name_lbl.z_index = 40
	add_child(name_lbl)

## 한 칸 걸어가기. 막혀 있으면 돌아서기만.
func try_step(d: Vector2i) -> bool:
	facing = d
	if moving: return false
	var to := cell + d
	if not world.is_free(to, self): 
		update_frame()
		return false
	world.move_actor(self, cell, to)
	cell = to
	moving = true
	return true

## 매 프레임 목표 칸으로 미끄러지듯 이동 (도착하면 on_arrive). 남은 거리는 다음 걸음에 이어 씀.
var walk_dist := 0.0
func move_tick(delta: float) -> void:
	if not moving: return
	var goal := cell_pos(cell)
	var sp := T / step_time
	var step := sp * delta
	var left := position.distance_to(goal)
	walk_dist += minf(step, left)
	if step >= left:
		position = goal
		moving = false
		on_arrive()
	else:
		position = position.move_toward(goal, step)

func on_arrive() -> void:
	pass

func pose(frame: int, sec: float) -> void:
	act_frame = frame
	act_until = Time.get_ticks_msec() / 1000.0 + sec

func update_frame() -> void:
	if spr == null: return
	var row := Doll.row_of(facing)
	spr.flip_h = facing.x < 0
	var now := Time.get_ticks_msec() / 1000.0
	var col := 0
	if now < act_until: col = act_frame
	elif moving: col = [1, 0, 2, 0][int(walk_dist / 7.0) % 4]
	spr.frame = row * spr.hframes + col

func flash(col := Color.WHITE) -> void:
	mat.set_shader_parameter("tint", col)
	mat.set_shader_parameter("flash", 1.0)
	var tw := create_tween()
	tw.tween_method(func(v): mat.set_shader_parameter("flash", v), 1.0, 0.0, 0.2)

func dist_to(c: Vector2i) -> int:
	return absi(c.x - cell.x) + absi(c.y - cell.y)
