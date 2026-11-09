extends "res://scripts/actor.gd"
## 성 사람들. 가만히 서서 가끔 고개를 돌린다. 할 말이 있으면 머리 위에 표시.

var npc_id := ""
var mark: Label
var t := 0.0

func _ready() -> void:
	add_to_group("npc")
	var n: Dictionary = DB.npcs[npc_id]
	add_child(Fx.shadow(18, 6))
	make_sprite(Doll.texture(n.look))
	var w: String = {"captain": "sword", "m_warrior": "sword", "m_rogue": "dagger", "m_mage": "staff", "m_priest": "bell", "smith": "club", "mujin": "dagger"}.get(npc_id, "")
	if w != "":
		var ws := Sprite2D.new()
		ws.texture = Fx.tex("weapon_" + w)
		ws.hframes = 7; ws.vframes = 3
		ws.offset = Vector2(0, -22)
		ws.z_index = 1
		add_child(ws)
		ws.set_meta("w", true)
	add_name(n.name, Color(0.75, 1, 0.6))
	mark = UI.label("!", 14, Color(1, 0.85, 0.3))
	mark.position = Vector2(-4, -72)
	mark.z_index = 41
	add_child(mark)
	t = randf() * 5

func face_to(c: Vector2i) -> void:
	var d := c - cell
	if d != Vector2i.ZERO: facing = d
	update_frame()

func _process(delta: float) -> void:
	t += delta
	if t > 4.0:
		t = randf() * 1.5
		facing = [Vector2i(0, 1), Vector2i(0, 1), Vector2i(1, 0), Vector2i(-1, 0)][randi() % 4]
	update_frame()
	for ch in get_children():
		if ch is Sprite2D and ch.has_meta("w"):
			ch.frame = spr.frame; ch.flip_h = spr.flip_h
	mark.visible = Talk.has_news(npc_id)
	mark.text = "?" if Talk.has_turn_in(npc_id) else "!"
	mark.position.y = -72 + sin(Time.get_ticks_msec() / 200.0) * 2
