extends Node2D
## 날아가는 기술 (불꽃·얼음·벼락·정기탄·표창)

signal landed

var kind := "fire"
var from := Vector2.ZERO
var to_node: Node2D
var t := 0.0
var dur := 0.25

func _ready() -> void:
	position = from
	z_index = 20
	if kind == "thunder": dur = 0.18

func _process(delta: float) -> void:
	if not is_instance_valid(to_node):
		queue_free(); return
	t += delta
	var target: Vector2 = to_node.position + Vector2(0, -22)
	position = from.lerp(target, minf(1.0, t / dur))
	queue_redraw()
	if t >= dur:
		landed.emit()
		Fx.anim(get_parent(), "spark", 4, target, 20, 21)
		if kind == "thunder":
			for i in 3: Fx.anim(get_parent(), "spark", 4, target + Vector2(randf_range(-30, 30), randf_range(-20, 20)), 18, 21)
		queue_free()

func _draw() -> void:
	var col: Color = {"fire": Color(1, 0.6, 0.2), "ice": Color(0.7, 0.95, 1), "thunder": Color(1, 1, 0.6), "orb": Color(0.7, 1, 0.9), "star": Color(0.85, 0.85, 0.9)}.get(kind, Color.WHITE)
	if kind == "thunder":
		var target: Vector2 = to_node.position + Vector2(0, -22) - position
		var top := target + Vector2(0, -180)
		var prev := top
		for i in 6:
			var nxt := top.lerp(target, (i + 1) / 6.0) + Vector2(randf_range(-6, 6), 0)
			draw_line(prev, nxt, col, 2.0)
			prev = nxt
		return
	if kind == "star":
		var a := t * 30
		for k in 4: draw_line(Vector2.ZERO, Vector2.from_angle(a + k * PI / 2) * 5, col, 2.0)
		return
	draw_circle(Vector2.ZERO, 6, Color(col, 0.3))
	draw_circle(Vector2.ZERO, 4, col)
	draw_circle(Vector2(-1, -1), 2, Color(1, 1, 1, 0.9))
