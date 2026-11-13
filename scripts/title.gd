extends Control
## 처음 화면과 캐릭터 만들기 (이름·성별·머리 모양·머리 색)

const NAMES := ["바람결", "솔빛", "해랑", "가온", "다솜", "누리", "미르", "한별", "도담", "아름", "보람", "새벽"]

var mode := "title"
var sel := 0
var t := 0.0
var items: Array = []
var labels: Array = []
var look := {"g": "m", "hair": "short", "hc": "black"}
var name_edit: LineEdit
var rows := ["이름", "성별", "머리 모양", "머리 색", "시작하기"]
var row := 0
var preview_lbls := []

func _ready() -> void:
	size = Vector2(640, 480)
	_title()

func _title() -> void:
	for ch in get_children(): ch.queue_free()
	mode = "title"; labels.clear()
	var logo := UI.label("해솔국 이야기", 32, Color("f6cf57"))
	logo.add_theme_font_override("font", Game.font_bold)
	logo.add_theme_constant_override("outline_size", 8)
	logo.size = Vector2(640, 40); logo.position = Vector2(0, 120)
	logo.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(logo)
	var sub := UI.label("— 검은 안개의 시작 —", 12, Color("cdb991"))
	sub.size = Vector2(640, 16); sub.position = Vector2(0, 166); sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(sub)
	items = ["새로 시작", "만든 것들"]
	if Game.has_save(): items.push_front("이어하기")
	for i in items.size():
		var l := UI.label("", 12, UI.PAPER)
		l.size = Vector2(640, 16); l.position = Vector2(0, 260 + i * 24); l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		add_child(l); labels.append(l)
	var hint := UI.label("방향키 고르기 · Enter/스페이스 결정", 10, UI.DIM, true, true)
	hint.size = Vector2(640, 12); hint.position = Vector2(0, 448); hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(hint)
	_labels()

func _labels() -> void:
	for i in labels.size():
		labels[i].text = ("◆ %s ◆" % items[i]) if i == sel else items[i]
		labels[i].add_theme_color_override("font_color", UI.GOLD if i == sel else UI.DIM)

func _create() -> void:
	for ch in get_children(): ch.queue_free()
	mode = "create"; row = 0
	var box := UI.box(); box.position = Vector2(140, 70); box.size = Vector2(360, 330)
	add_child(box)
	var tl := UI.label("나를 만들기", 14, UI.GOLD); tl.position = Vector2(16, 10); box.add_child(tl)
	name_edit = LineEdit.new()
	name_edit.text = NAMES[randi() % NAMES.size()]
	name_edit.max_length = 8
	name_edit.position = Vector2(110, 44); name_edit.size = Vector2(140, 22)
	name_edit.add_theme_font_override("font", Game.font)
	name_edit.add_theme_font_size_override("font_size", 12)
	box.add_child(name_edit)
	preview_lbls.clear()
	for i in rows.size():
		var l := UI.label("", 12, UI.PAPER); l.position = Vector2(20, 46 + i * 34); l.size = Vector2(320, 16)
		box.add_child(l); preview_lbls.append(l)
	var hint := UI.label("↑↓ 고르기 · ←→ 바꾸기 · 이름 칸을 눌러 직접 적기", 10, UI.DIM, true, true)
	hint.position = Vector2(16, 300); box.add_child(hint)
	_create_labels()

func _create_labels() -> void:
	var gname := {"m": "사내", "f": "여인"}
	var hname := {"short": "짧은 머리", "topknot": "상투", "long": "댕기 머리", "bun": "쪽 찐 머리"}
	var cname := {"black": "검정", "brown": "밤색", "chestnut": "갈색", "ash": "잿빛"}
	var vals := ["", gname[look.g], hname[look.hair], cname[look.hc], ""]
	for i in rows.size():
		var on := i == row
		var txt: String = rows[i] if i < 4 else "◆ 해솔성으로 떠나기 ◆"
		if i in [1, 2, 3]: txt = "%s      ◀ %s ▶" % [rows[i], vals[i]]
		preview_lbls[i].text = ("▶ " if on else "   ") + txt
		preview_lbls[i].add_theme_color_override("font_color", UI.GOLD if on else UI.PAPER)

func _cycle(key: String, opts: Array, d: int) -> void:
	look[key] = opts[posmod(opts.find(look[key]) + d, opts.size())]

func _process(delta: float) -> void:
	t += delta
	queue_redraw()
	if has_node("Licenses") or Time.get_ticks_msec() < lic_until:
		return
	if mode == "title":
		if Input.is_action_just_pressed("up") or Input.is_action_just_pressed("down"):
			sel = posmod(sel + (1 if Input.is_action_just_pressed("down") else -1), items.size()); _labels(); Sound.play("select", 0.0, -6)
		if Input.is_action_just_pressed("talk") or Input.is_action_just_pressed("attack"):
			Sound.play("chest", 0.0, -4)
			if items[sel] == "만든 것들":
				_licenses()
				return
			if items[sel] == "이어하기" and Game.load_save():
				set_process(false)
				get_tree().call_group("main", "start", Game.c, false)
			else:
				_create()
		return
	if name_edit.has_focus():
		if Input.is_action_just_pressed("talk") or Input.is_action_just_pressed("down"): name_edit.release_focus()
		return
	var d := 0
	if Input.is_action_just_pressed("left"): d = -1
	if Input.is_action_just_pressed("right"): d = 1
	if Input.is_action_just_pressed("up"): row = posmod(row - 1, rows.size())
	if Input.is_action_just_pressed("down"): row = posmod(row + 1, rows.size())
	if d != 0:
		match row:
			0: name_edit.text = NAMES[posmod(NAMES.find(name_edit.text) + d, NAMES.size())]
			1: _cycle("g", ["m", "f"], d)
			2: _cycle("hair", ["short", "topknot", "long", "bun"], d)
			3: _cycle("hc", ["black", "brown", "chestnut", "ash"], d)
		Sound.play("select", 0.0, -8)
	if Input.is_action_just_pressed("talk") or Input.is_action_just_pressed("attack"):
		if row == 0: name_edit.grab_focus()
		elif row == 4: _go()
	if Input.is_action_just_pressed("cancel"): _title()
	if Input.is_anything_pressed(): _create_labels()

var lic_until := 0

## 만든 것들·라이선스 (Godot 엔진·글꼴)
func _licenses() -> void:
	var l: Control = preload("res://scripts/licenses.gd").new()
	l.credits = [
		"해솔국 이야기 — 심심풀이",
		"게임 엔진: Godot Engine (MIT 라이선스) — godotengine.org/license",
		"글꼴: 갈무리 Galmuri (SIL Open Font License 1.1) — github.com/quiple/galmuri",
		"도트 그림·지도·효과음·곡: 코드로 새로 만듦",
	]
	l.font_size = 12
	l.font = Game.font
	l.closed.connect(func(): lic_until = Time.get_ticks_msec() + 200)
	add_child(l)

func _go() -> void:
	var nm := name_edit.text.strip_edges()
	if nm == "": nm = NAMES[0]
	set_process(false)
	var c := Rules.new_character(nm, look.g, look.hair, look.hc)
	Sound.play("chest", 0.0)
	get_tree().call_group("main", "start", c, true)

func _draw() -> void:
	# 밤하늘·달·기와 지붕 실루엣
	for y in range(0, 480, 4):
		var k := y / 480.0
		draw_rect(Rect2(0, y, 640, 4), Color("141224").lerp(Color("4a2f55"), k * k))
	for i in 60:
		var x := fmod(i * 97.0, 640.0); var y := fmod(i * 53.0, 260.0)
		draw_rect(Rect2(x, y, 1, 1), Color(1, 1, 0.9, 0.4 + 0.5 * absf(sin(t + i))))
	draw_circle(Vector2(500, 90), 34, Color(1, 0.95, 0.7, 0.08))
	draw_circle(Vector2(500, 90), 24, Color("fff0b0"))
	var pts := PackedVector2Array([Vector2(0, 480)])
	for x in range(0, 648, 8): pts.append(Vector2(x, 380 - sin(x * 0.01) * 30 - sin(x * 0.033) * 10))
	pts.append(Vector2(640, 480))
	draw_colored_polygon(pts, Color("2a1f38"))
	var roof := Fx.tex("hanok_big")
	for i in 4:
		draw_texture(roof, Vector2(20 + i * 160, 340 + (i % 2) * 14), Color(0.25, 0.2, 0.32))
	if mode == "create":
		var lk := look.duplicate(); lk.outfit = "commoner"
		var tex := Doll.texture(lk)
		var f := int(t * 4) % 4
		var col: int = [0, 1, 0, 2][f]
		var dir := int(t / 2) % 3
		draw_texture_rect_region(tex, Rect2(395, 150, 64, 96), Rect2(col * 32, dir * 48, 32, 48))
		var face := Fx.tex("portrait_p_%s_%s_%s" % [look.g, look.hair, look.hc])
		draw_texture(face, Vector2(400, 250))
