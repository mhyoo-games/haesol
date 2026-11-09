extends CanvasLayer
## 화면 아래 고정 패널(글창·체력·기력·경험치), 단축칸, 창(가방·능력치·기술·퀘스트·가게), 대화창.

var root: Control
var map_lbl: Label
var tgt_lbl: Label
var logs: Array = []
var log_lbls: Array = []
var info_lbl: Label
var bars := {}
var hot_slots: Array = []
var win: Control
var win_kind := ""
var cursor := 0
var shop_id := ""
var shop_mode := "buy"
# 대화
var dlg: Control
var dlg_face: TextureRect
var dlg_name: Label
var dlg_text: Label
var dlg_choices: VBoxContainer
var lines: Array = []
var line_i := 0
var shown := 0.0
var choices: Array = []
var choice_i := 0
var on_done := Callable()
var talking := false

func _ready() -> void:
	layer = 10
	process_mode = Node.PROCESS_MODE_ALWAYS
	root = Control.new()
	root.size = Vector2(640, 480)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	map_lbl = UI.label("", 10, UI.PAPER, true, true)
	map_lbl.position = Vector2(6, 4)
	root.add_child(map_lbl)
	tgt_lbl = UI.label("", 10, Color(1, 0.8, 0.6), true, true)
	tgt_lbl.size = Vector2(640, 12); tgt_lbl.position = Vector2(0, 4)
	tgt_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	root.add_child(tgt_lbl)
	# 아래 패널
	var panel := UI.box()
	panel.position = Vector2(0, 400); panel.size = Vector2(640, 80)
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(panel)
	var logbg := UI.slot()
	logbg.position = Vector2(6, 6); logbg.size = Vector2(380, 68)
	panel.add_child(logbg)
	for i in 6:
		var l := UI.label("", 10, UI.PAPER, false, true)
		l.position = Vector2(12, 8 + i * 11)
		l.size = Vector2(370, 11)
		l.clip_text = true
		panel.add_child(l)
		log_lbls.append(l)
	info_lbl = UI.label("", 10, UI.GOLD, true, true)
	info_lbl.position = Vector2(394, 6)
	panel.add_child(info_lbl)
	var y := 22
	for k in ["hp", "mp", "exp"]:
		var bg := ColorRect.new(); bg.color = Color(0.05, 0.03, 0.06); bg.position = Vector2(394, y); bg.size = Vector2(240, 11)
		panel.add_child(bg)
		var fg := ColorRect.new(); fg.color = {"hp": Color("b33a35"), "mp": Color("3b62a8"), "exp": Color("c9a23a")}[k]
		fg.position = Vector2(395, y + 1); fg.size = Vector2(238, 9)
		panel.add_child(fg)
		var tl := UI.label("", 10, Color.WHITE, true, true)
		tl.position = Vector2(398, y - 1); tl.size = Vector2(234, 11)
		panel.add_child(tl)
		bars[k] = [fg, tl]
		y += 16
	# 단축칸
	for i in 8:
		var s := UI.slot()
		s.position = Vector2(208 + i * 28, 368); s.size = Vector2(26, 26)
		root.add_child(s)
		var ic := TextureRect.new(); ic.position = Vector2(3, 3); ic.size = Vector2(20, 20)
		s.add_child(ic)
		var num := UI.label(str(i + 1), 10, Color(1, 1, 1, 0.8), true, true); num.position = Vector2(2, -2)
		s.add_child(num)
		var cnt := UI.label("", 10, Color.WHITE, true, true); cnt.position = Vector2(12, 13)
		s.add_child(cnt)
		var cd := ColorRect.new(); cd.color = Color(0, 0, 0, 0.55); cd.position = Vector2(2, 2); cd.size = Vector2(22, 0)
		s.add_child(cd)
		s.gui_input.connect(func(e): if e is InputEventMouseButton and e.pressed: _hot_click(i))
		hot_slots.append([s, ic, cnt, cd])
	_build_dialog()
	Game.changed.connect(refresh)
	Game.log.connect(add_log)

func add_log(text: String, col: Color) -> void:
	logs.append([text, col])
	while logs.size() > 6: logs.pop_front()
	for i in 6:
		var l: Label = log_lbls[i]
		if i < logs.size():
			l.text = logs[i][0]
			l.add_theme_color_override("font_color", logs[i][1])
		else:
			l.text = ""

func refresh() -> void:
	var c: Dictionary = Game.c
	if c.is_empty(): return
	info_lbl.text = "%s  %s  레벨 %d     전 %d" % [c.name, Rules.job(c).name, c.lv, c.gold]
	var vals := {"hp": [c.hp, Rules.max_hp(c), "체력"], "mp": [c.mp, Rules.max_mp(c), "기력"], "exp": [c.exp, Rules.exp_need(c.lv), "경험치"]}
	for k in vals:
		var v: Array = vals[k]
		bars[k][0].size.x = 238.0 * clampf(float(v[0]) / maxf(1.0, float(v[1])), 0, 1)
		bars[k][1].text = "%s %d / %d" % [v[2], v[0], v[1]] if k != "exp" else "%s %.1f%%" % [v[2], 100.0 * v[0] / maxf(1, v[1])]
	for i in 8:
		var id: String = c.hot[i]
		var ic: TextureRect = hot_slots[i][1]
		var cnt: Label = hot_slots[i][2]
		ic.texture = null; cnt.text = ""
		if DB.skills.has(id): ic.texture = Fx.tex("skill_" + id)
		elif DB.items.has(id):
			ic.texture = UI.icon_of_item(id)
			cnt.text = str(Rules.count(c, id))
	if win and win_kind != "": _draw_window()

func _process(_d: float) -> void:
	var w = get_tree().get_first_node_in_group("world")
	if w and w.player:
		var p = w.player
		map_lbl.text = "%s (%d, %d)" % [w.data.name, p.cell.x, p.cell.y]
		var tg = p.target
		if tg and is_instance_valid(tg) and not tg.dead:
			tgt_lbl.text = "%s  레벨 %d  [%d/%d]" % [tg.info.name, int(tg.info.lv), tg.hp, int(tg.info.hp)]
		else:
			tgt_lbl.text = ""
		var now := Time.get_ticks_msec() / 1000.0
		for i in 8:
			var id: String = Game.c.hot[i]
			var cd: ColorRect = hot_slots[i][3]
			if DB.skills.has(id):
				var left: float = p.cooldowns.get(id, 0.0) - now
				cd.size.y = 22.0 * clampf(left / float(DB.skills[id].cd), 0, 1)
			else:
				cd.size.y = 0
	if talking:
		_dialog_tick(_d)
		return
	if win_kind != "":
		_window_input()
		return
	if Game.c.is_empty() or w == null: return
	for k in ["inv", "status", "skills", "quests"]:
		if Input.is_action_just_pressed(k): open_window(k)
	if Input.is_action_just_pressed("cancel"): open_window("menu")

func _hot_click(i: int) -> void:
	var w = get_tree().get_first_node_in_group("world")
	if w and w.player and not Game.busy: w.player.use_hot(i)

# ── 창 ──
func open_window(kind: String) -> void:
	close_window()
	win_kind = kind
	cursor = 0
	Game.busy = true
	win = UI.box()
	root.add_child(win)
	Sound.play("select", 0.0, -6)
	_draw_window()

func close_window() -> void:
	if win: win.queue_free()
	win = null
	win_kind = ""
	if not talking: Game.busy = false

func _clear(n: Node) -> void:
	for ch in n.get_children(): ch.queue_free()

func _txt(text: String, pos: Vector2, col := UI.PAPER, size := 12, small := false) -> Label:
	var l := UI.label(text, size, col, true, small)
	l.position = pos
	win.add_child(l)
	return l

func _items_list() -> Array:
	if win_kind == "shop" and shop_mode == "buy": return DB.shops[shop_id].items
	var out := []
	for s in Game.c.inv: out.append(s.id)
	return out

func _draw_window() -> void:
	_clear(win)
	var c: Dictionary = Game.c
	match win_kind:
		"inv", "shop":
			win.position = Vector2(120, 40); win.size = Vector2(400, 300)
			var title := "가방" if win_kind == "inv" else "%s — %s (←→ 사기/팔기)" % [DB.shops[shop_id].name, "사기" if shop_mode == "buy" else "팔기"]
			_txt(title, Vector2(12, 8), UI.GOLD)
			_txt("전 %d" % c.gold, Vector2(320, 8), UI.GOLD, 12)
			var list := _items_list()
			cursor = clampi(cursor, 0, maxi(0, list.size() - 1))
			var cols := 8
			for i in maxi(list.size(), 24 if win_kind == "inv" or shop_mode == "sell" else 0):
				var s := UI.slot()
				s.position = Vector2(12 + (i % cols) * 30, 30 + (i / cols) * 30); s.size = Vector2(28, 28)
				if i == cursor: s.modulate = Color(1.4, 1.3, 0.8)
				win.add_child(s)
				if i < list.size():
					var ic := TextureRect.new(); ic.texture = UI.icon_of_item(list[i]); ic.position = Vector2(4, 4); ic.size = Vector2(20, 20)
					s.add_child(ic)
					if win_kind == "inv" or shop_mode == "sell":
						var n := int(c.inv[i].n)
						if n > 1:
							var cl := UI.label(str(n), 10, Color.WHITE, true, true); cl.position = Vector2(14, 15); s.add_child(cl)
					var idx := i
					s.gui_input.connect(func(e):
						if e is InputEventMouseButton and e.pressed:
							if cursor == idx or e.double_click: _window_act()
							cursor = idx; _draw_window())
			# 장비 칸
			if win_kind == "inv":
				var sl := ["weapon", "head", "body", "acc"]
				var nm := {"weapon": "무기", "head": "머리", "body": "몸", "acc": "장신구"}
				for k in 4:
					var s := UI.slot()
					s.position = Vector2(270 + (k % 2) * 60, 40 + (k / 2) * 52); s.size = Vector2(28, 28)
					win.add_child(s)
					var id = c.equip.get(sl[k], "")
					if id != "" and id != null:
						var ic := TextureRect.new(); ic.texture = UI.icon_of_item(id); ic.position = Vector2(4, 4); ic.size = Vector2(20, 20); s.add_child(ic)
					var l := _txt(nm[sl[k]], Vector2(270 + (k % 2) * 60, 70 + (k / 2) * 52), UI.DIM, 10, true)
					var slot_name: String = sl[k]
					s.gui_input.connect(func(e):
						if e is InputEventMouseButton and e.pressed:
							var why := Rules.unequip(c, slot_name)
							if why != "": Game.say(why, UI.DIM)
							Game.touch())
			# 설명
			if cursor < list.size():
				var id: String = list[cursor]
				var it: Dictionary = DB.items[id]
				var desc: String = it.get("desc", "")
				var stat := []
				for k in ["atk", "matk", "def", "hp", "mp"]:
					if it.has(k): stat.append({"atk": "공격", "matk": "술력", "def": "방어", "hp": "체력", "mp": "기력"}[k] + " +" + str(int(it[k])))
				if it.has("job"): stat.append(DB.jobs[it.job].name + " 전용")
				if it.has("lv"): stat.append("레벨 %d" % int(it.lv))
				var price := ("값 %d전" % int(it.price)) if win_kind == "shop" and shop_mode == "buy" else ("팔면 %d전" % Rules.sell_price(id))
				_txt(it.name, Vector2(12, 160), UI.GOLD)
				_txt(("%s  %s" % [desc, " · ".join(stat)]).strip_edges(), Vector2(12, 178), UI.PAPER, 10, true)
				_txt(price, Vector2(12, 194), UI.DIM, 10, true)
			var help := "Enter 쓰기·입기 · 장비 칸 누르면 벗기 · Esc 닫기" if win_kind == "inv" else ("Enter 사기 · Esc 닫기" if shop_mode == "buy" else "Enter 팔기 · Esc 닫기")
			_txt(help, Vector2(12, 276), UI.DIM, 10, true)
		"status":
			win.position = Vector2(170, 60); win.size = Vector2(300, 220)
			_txt("능력치", Vector2(12, 8), UI.GOLD)
			var rows := [["이름", c.name], ["직업", Rules.job(c).name], ["레벨", str(c.lv)], ["체력", "%d / %d" % [c.hp, Rules.max_hp(c)]], ["기력", "%d / %d" % [c.mp, Rules.max_mp(c)]],
				["공격", str(Rules.atk(c))], ["술력", str(Rules.matk(c))], ["방어", str(Rules.defense(c))], ["경험치", "%d / %d" % [c.exp, Rules.exp_need(c.lv)]], ["전", str(c.gold)]]
			for i in rows.size():
				_txt(rows[i][0], Vector2(20, 32 + i * 17), UI.DIM, 12)
				_txt(rows[i][1], Vector2(110, 32 + i * 17), UI.PAPER, 12)
		"skills":
			win.position = Vector2(110, 50); win.size = Vector2(420, 250)
			_txt("기술 (%s)" % Rules.job(c).name, Vector2(12, 8), UI.GOLD)
			var i := 0
			for sid in DB.skills:
				var s: Dictionary = DB.skills[sid]
				if s.job != c.job: continue
				var ok: bool = c.lv >= int(s.lv)
				var ic := TextureRect.new(); ic.texture = Fx.tex("skill_" + sid); ic.position = Vector2(14, 34 + i * 44); ic.modulate = Color.WHITE if ok else Color(0.4, 0.4, 0.4)
				win.add_child(ic)
				_txt("%s   레벨 %d · 기력 %d · 다시 쓰기 %.1f초" % [s.name, int(s.lv), int(s.mp), float(s.cd)], Vector2(42, 30 + i * 44), UI.PAPER if ok else UI.DIM)
				_txt(s.desc + ("" if ok else " (아직 못 씀)"), Vector2(42, 46 + i * 44), UI.DIM, 10, true)
				i += 1
			if i == 0: _txt("레벨 5가 되면 수련관에서 직업을 얻을 수 있다.", Vector2(14, 40), UI.DIM)
			_txt("기술은 직업을 얻거나 레벨이 오르면 빈 단축칸에 저절로 들어간다.", Vector2(12, 226), UI.DIM, 10, true)
		"quests":
			win.position = Vector2(90, 40); win.size = Vector2(460, 300)
			_txt("퀘스트", Vector2(12, 8), UI.GOLD)
			var i := 0
			for q in DB.quests:
				var st := Rules.quest_state(c, q.id)
				if st == "": continue
				var giver: String = DB.npcs[q.giver].name
				_txt(("✔ " if st == "done" else "▶ ") + q.name, Vector2(14, 30 + i * 30), UI.PAPER if st == "active" else UI.DIM)
				_txt(("완료" if st == "done" else Rules.progress_text(c, q.id) + "  (" + giver + ")"), Vector2(30, 45 + i * 30), Color(1, 0.9, 0.5) if st == "active" else UI.DIM, 10, true)
				i += 1
			if i == 0: _txt("아직 받은 퀘스트가 없다. 머리 위에 !가 뜬 사람에게 말을 걸어 보자.", Vector2(14, 34), UI.DIM, 10, true)
		"menu":
			win.position = Vector2(220, 120); win.size = Vector2(200, 140)
			_txt("메뉴", Vector2(12, 8), UI.GOLD)
			var items := ["계속하기", "저장하기", "소리 " + ("켜기" if Sound.muted else "끄기"), "처음 화면으로"]
			for i in items.size():
				_txt(("▶ " if i == cursor else "   ") + items[i], Vector2(20, 34 + i * 22), UI.PAPER if i == cursor else UI.DIM)
			_txt("I 가방 · C 능력치 · K 기술 · Q 퀘스트", Vector2(12, 120), UI.DIM, 10, true)

func _window_input() -> void:
	if Input.is_action_just_pressed("cancel") or (win_kind != "menu" and win_kind != "shop" and Input.is_action_just_pressed(win_kind)):
		close_window(); return
	var n := _items_list().size() if win_kind in ["inv", "shop"] else (4 if win_kind == "menu" else 0)
	if n == 0: return
	var step := 8 if win_kind in ["inv", "shop"] else 1
	if Input.is_action_just_pressed("right"):
		if win_kind == "shop" and cursor % 8 == 7 or win_kind == "shop" and n == 0: pass
		cursor = mini(n - 1, cursor + 1) if win_kind != "menu" else cursor
	if Input.is_action_just_pressed("left"): cursor = maxi(0, cursor - 1) if win_kind != "menu" else cursor
	if Input.is_action_just_pressed("down"): cursor = mini(n - 1, cursor + step)
	if Input.is_action_just_pressed("up"): cursor = maxi(0, cursor - step)
	if win_kind == "shop" and Input.is_action_just_pressed("target"):
		shop_mode = "sell" if shop_mode == "buy" else "buy"; cursor = 0
	if Input.is_action_just_pressed("talk") or Input.is_action_just_pressed("attack"): _window_act()
	if Input.is_anything_pressed(): _draw_window()

func _window_act() -> void:
	var c: Dictionary = Game.c
	var why := ""
	match win_kind:
		"inv":
			if cursor >= c.inv.size(): return
			var id: String = c.inv[cursor].id
			var t: String = DB.items[id].type
			if t == "use":
				why = Rules.use_item(c, cursor); Sound.play("heal", 0.05)
			elif t in ["weapon", "head", "body", "acc"]:
				why = Rules.equip(c, cursor)
				if why == "": Game.say("%s을(를) 입었다." % DB.items[id].name); Sound.play("select", 0.0)
			else:
				why = DB.items[id].get("desc", "쓸 데가 있을 것 같다.")
		"shop":
			var list := _items_list()
			if cursor >= list.size(): return
			if shop_mode == "buy":
				why = Rules.buy(c, list[cursor])
				if why == "": Game.say("%s을(를) 샀다." % DB.items[list[cursor]].name); Sound.play("coin", 0.0)
			else:
				var id: String = list[cursor]
				why = Rules.sell(c, cursor)
				if why == "": Game.say("%s을(를) %d전에 팔았다." % [DB.items[id].name, Rules.sell_price(id)]); Sound.play("coin", 0.0)
		"menu":
			match cursor:
				0: close_window()
				1: Game.save(); Game.say("저장했다.", UI.GOLD); close_window()
				2: Sound.toggle_mute(); _draw_window()
				3: close_window(); get_tree().call_group("main", "show_title")
			return
	if why != "": Game.say(why, UI.DIM)
	Game.touch()
	_draw_window()

func open_shop(id: String) -> void:
	shop_id = id
	shop_mode = "buy"
	open_window("shop")

# ── 대화 ──
func _build_dialog() -> void:
	dlg = UI.box()
	dlg.position = Vector2(20, 300); dlg.size = Vector2(600, 96)
	dlg.visible = false
	root.add_child(dlg)
	var fb := UI.slot(); fb.position = Vector2(10, 10); fb.size = Vector2(54, 54)
	dlg.add_child(fb)
	dlg_face = TextureRect.new(); dlg_face.position = Vector2(3, 3); dlg_face.size = Vector2(48, 48)
	fb.add_child(dlg_face)
	dlg_name = UI.label("", 12, UI.GOLD)
	dlg_name.position = Vector2(76, 8)
	dlg.add_child(dlg_name)
	dlg_text = UI.label("", 12, UI.PAPER)
	dlg_text.position = Vector2(76, 26); dlg_text.size = Vector2(510, 60)
	dlg_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dlg.add_child(dlg_text)
	dlg_choices = VBoxContainer.new()
	dlg_choices.position = Vector2(420, 40)
	dlg.add_child(dlg_choices)

func _speaker(id: String) -> Array:
	if id == "": return ["", null]
	if id == "me":
		var c: Dictionary = Game.c
		return [c.name, Fx.tex("portrait_p_%s_%s_%s" % [c.g, c.hair, c.hc])]
	if DB.npcs.has(id): return [DB.npcs[id].name, Fx.tex("portrait_" + id)]
	return [id, null]

func open_dialog(l: Array, cb := Callable(), ch: Array = []) -> void:
	if win_kind != "": close_window()
	lines = l; line_i = 0; on_done = cb; choices = ch; choice_i = 0
	talking = true
	for h in hot_slots: h[0].visible = false
	Game.busy = true
	dlg.visible = true
	_show_line()

func _show_line() -> void:
	var sp := _speaker(lines[line_i][0])
	dlg_name.text = sp[0]
	dlg_face.texture = sp[1]
	dlg_face.get_parent().visible = sp[1] != null
	var x := 76 if sp[1] != null else 14
	dlg_name.position.x = x; dlg_text.position.x = x
	dlg_text.text = lines[line_i][1]
	dlg_text.visible_characters = 0
	shown = 0.0
	_clear(dlg_choices)
	dlg_choices.visible = false

func _show_choices() -> void:
	_clear(dlg_choices)
	dlg_choices.visible = true
	for i in choices.size():
		var l := UI.label(("▶ " if i == choice_i else "   ") + choices[i], 12, UI.GOLD if i == choice_i else UI.DIM)
		l.mouse_filter = Control.MOUSE_FILTER_STOP
		var idx := i
		l.gui_input.connect(func(e): if e is InputEventMouseButton and e.pressed: choice_i = idx; _close(idx))
		dlg_choices.add_child(l)
	dlg_choices.position = Vector2(440, 76 - choices.size() * 16)

func _dialog_tick(delta: float) -> void:
	var full := dlg_text.text.length()
	if dlg_text.visible_characters < full:
		shown += delta * 45.0
		var n := mini(full, int(shown))
		if n > dlg_text.visible_characters and n % 3 == 0: Sound.play("talk", 0.05, -14)
		dlg_text.visible_characters = n
	var go := Input.is_action_just_pressed("talk") or Input.is_action_just_pressed("attack") or (Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT) and false)
	if dlg_choices.visible:
		if Input.is_action_just_pressed("up"): choice_i = posmod(choice_i - 1, choices.size()); _show_choices()
		elif Input.is_action_just_pressed("down"): choice_i = posmod(choice_i + 1, choices.size()); _show_choices()
		elif go: _close(choice_i)
		elif Input.is_action_just_pressed("cancel"): _close(choices.size() - 1)
		return
	if go:
		if dlg_text.visible_characters < full:
			dlg_text.visible_characters = full; shown = 9999
		elif line_i < lines.size() - 1:
			line_i += 1; _show_line()
		elif not choices.is_empty():
			_show_choices()
		else:
			_close(-1)

func _input(e: InputEvent) -> void:
	if talking and e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT and not dlg_choices.visible:
		var ev := InputEventAction.new(); ev.action = "talk"; ev.pressed = true
		Input.parse_input_event(ev)
		var ev2 := InputEventAction.new(); ev2.action = "talk"; ev2.pressed = false
		Input.parse_input_event.call_deferred(ev2)

func _close(pick: int) -> void:
	talking = false
	dlg.visible = false
	for h in hot_slots: h[0].visible = true
	await get_tree().create_timer(0.1).timeout
	if win_kind == "": Game.busy = false
	var cb := on_done
	on_done = Callable()
	if cb.is_valid():
		if pick >= 0: cb.call(pick)
		else: cb.call()
