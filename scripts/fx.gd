class_name Fx
extends RefCounted
## 번쩍임·불꽃·먼지·숫자 같은 화면 효과.

static var _flash_shader: Shader
static var _tex := {}

static func tex(n: String) -> Texture2D:
	if not _tex.has(n):
		_tex[n] = load("res://assets/sprites/%s.png" % n)
	return _tex[n]

## 맞으면 하얗게 번쩍이게 하는 재질
static func flash_material() -> ShaderMaterial:
	if _flash_shader == null:
		_flash_shader = Shader.new()
		_flash_shader.code = """
shader_type canvas_item;
uniform float flash : hint_range(0.0, 1.0) = 0.0;
uniform vec4 tint : source_color = vec4(1.0);
void fragment() {
	vec4 c = texture(TEXTURE, UV) * COLOR;
	c.rgb = mix(c.rgb, tint.rgb, flash);
	COLOR = c;
}
"""
	var m := ShaderMaterial.new()
	m.shader = _flash_shader
	return m

## 칸 그림을 한 번 재생하고 사라지는 효과
static func anim(parent: Node, n: String, frames: int, pos: Vector2, fps := 16.0, z := 5) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = tex(n)
	s.hframes = frames
	s.position = pos
	s.z_index = z
	parent.add_child(s)
	var tw := s.create_tween()
	tw.tween_method(func(v: float): s.frame = mini(frames - 1, int(v)), 0.0, float(frames), frames / fps)
	tw.tween_callback(s.queue_free)
	return s

static func number(parent: Node, pos: Vector2, text: String, col := Color(1, 0.95, 0.7)) -> void:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", Game.font_bold)
	l.add_theme_font_size_override("font_size", 12)
	l.add_theme_color_override("font_color", col)
	l.add_theme_color_override("font_outline_color", Color(0.17, 0.12, 0.18))
	l.add_theme_constant_override("outline_size", 3)
	l.position = pos + Vector2(-10, -52)
	l.z_index = 20
	parent.add_child(l)
	var tw := l.create_tween()
	tw.set_parallel(true)
	tw.tween_property(l, "position:y", l.position.y - 12, 0.6).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(l, "modulate:a", 0.0, 0.3).set_delay(0.35)
	tw.chain().tween_callback(l.queue_free)

## 아주 잠깐 멈춤 (타격감)
static func hitstop(node: Node, sec := 0.05) -> void:
	Engine.time_scale = 0.05
	await node.get_tree().create_timer(sec, true, false, true).timeout
	Engine.time_scale = 1.0

## 발밑 그림자 (타원)
static func shadow(w: float, h := 3.0) -> Node2D:
	var p := Polygon2D.new()
	var pts := PackedVector2Array()
	for i in 16:
		var a := TAU * i / 16.0
		pts.append(Vector2(cos(a) * w * 0.5, sin(a) * h * 0.5))
	p.polygon = pts
	p.color = Color(0.08, 0.05, 0.12, 0.35)
	p.z_index = -1
	return p
