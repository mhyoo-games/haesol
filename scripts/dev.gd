extends Node
## 개발용 자동 조작: godot -- --dev=<장면> --out=<폴더>. 평소에는 아무것도 안 함.

var plan := ""
var out := "/tmp/haesol"

func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--dev="): plan = a.substr(6)
		if a.begins_with("--out="): out = a.substr(6)
	if plan == "": queue_free(); return
	DirAccess.make_dir_recursive_absolute(out)
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run()

func shot(n: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [out, n])
	print("shot ", n)

func wait(s: float) -> void:
	await get_tree().create_timer(s, true, false, true).timeout

func send(a: String, on: bool) -> void:
	var e := InputEventAction.new(); e.action = a; e.pressed = on; e.strength = 1.0
	Input.parse_input_event(e)

func hold(a: String, s: float) -> void:
	send(a, true); await wait(s); send(a, false)

func tap(a: String) -> void:
	send(a, true)
	await get_tree().process_frame; await get_tree().process_frame
	send(a, false)
	await get_tree().process_frame

func close_dialogs() -> void:
	var hud = main().hud
	for i in 40:
		if not hud.talking: return
		await tap("talk"); await wait(0.06)

func main() -> Node: return get_tree().get_first_node_in_group("main")
func player() -> Node: return get_tree().get_first_node_in_group("player")

func _run() -> void:
	await wait(0.8)
	await shot("title")
	var c := Rules.new_character("바람결", "m", "topknot", "black")
	if plan == "licenses":
		get_tree().get_first_node_in_group("main").title._licenses(); await wait(0.5); await shot("licenses")
		get_tree().quit(); return
	if plan == "create":
		var t = get_tree().get_first_node_in_group("main").title
		t._create(); await wait(0.6); await shot("create")
		t.look = {"g": "f", "hair": "long", "hc": "brown"}; t._create_labels(); await wait(0.4); await shot("create_f")
		get_tree().quit(); return
	main().start(c, true)
	await wait(1.6)
	await shot("intro")
	await close_dialogs()
	await wait(0.3)
	await shot("town")
	match plan:
		"town":
			await hold("up", 1.2); await shot("town_walk")
			main().world.release(player())
			player().place(Vector2i(44, 19)); main().world.occ[player().cell] = player()
			player().facing = Vector2i(0, -1)
			await wait(0.3); await tap("talk"); await wait(1.2); await shot("talk_captain")
			await tap("talk"); await wait(0.3); await tap("talk"); await wait(0.3); await tap("talk"); await wait(0.5); await shot("quest_offer")
			await close_dialogs(); await wait(0.3)
			await tap("inv"); await wait(0.3); await shot("win_inv"); await tap("cancel")
			await tap("quests"); await wait(0.3); await shot("win_quests"); await tap("cancel")
		"field":
			Game.c.lv = 6; Rules.set_job(Game.c, "warrior"); Game.c.hot[0] = "whirl"
			main().go_map("field", Vector2i(10, 30)); await wait(1.2)
			await shot("field")
			var t = player().find_target(12)
			if t:
				for i in 30:
					if not is_instance_valid(t) or t.dead: break
					var d: Vector2i = t.cell - player().cell
					if absi(d.x) + absi(d.y) == 1:
						player().facing = d
						send("attack", true); await wait(0.5); send("attack", false)
					else:
						var dd := Vector2i(signi(d.x), 0) if absi(d.x) > absi(d.y) else Vector2i(0, signi(d.y))
						player().try_step(dd); await wait(0.3)
					if i == 6: await shot("field_fight")
			await wait(0.3); await shot("field_after")
			await tap("hot1"); await wait(0.1); await shot("skill")
		"story":
			var p = player()
			var talk := func(id: String):
				Talk.npc(get_tree(), id)
				await wait(0.3)
				await close_dialogs()
				await wait(0.3)
				await close_dialogs()
			await talk.call("captain")
			print("q_rabbit: ", Rules.quest_state(c, "q_rabbit"))
			# 토끼를 바로 앞에 놓고 쳐서 잡기
			main().go_map("field", Vector2i(8, 26)); await wait(1.2)
			p = player()
			var w = main().world
			for k in 5:
				var m = preload("res://scripts/monster.gd").new()
				m.mon = "rabbit"; m.world = w; w.ysort.add_child(m)
				var cc: Vector2i = p.cell + Vector2i(1, 0)
				if not w.is_free(cc): cc = w.nearest_free(cc)
				p.facing = cc - p.cell if (cc - p.cell).length() == 1 else Vector2i(1, 0)
				m.place(cc); w.occ[cc] = m
				for t in 20:
					if m.dead: break
					if (m.cell - p.cell).length_squared() == 1: p.facing = m.cell - p.cell
					send("attack", true); await wait(0.25); send("attack", false); await wait(0.15)
				if k == 0: await shot("story_fight")
			print("rabbits: ", c.quests.q_rabbit.kills, " lv ", c.lv, " gold ", c.gold)
			main().go_map("town", Vector2i(44, 19)); await wait(1.2)
			await talk.call("captain")
			print("q_rabbit: ", Rules.quest_state(c, "q_rabbit"), " cap ", Rules.count(c, "cap"))
			await talk.call("hana"); print("q_tail: ", Rules.quest_state(c, "q_tail"))
			Rules.add_item(c, "tail", 5); await talk.call("hana"); print("q_tail: ", Rules.quest_state(c, "q_tail"))
			while c.lv < 5: Rules.gain_exp(c, Rules.exp_need(c.lv))
			await talk.call("elder"); print("q_job: ", Rules.quest_state(c, "q_job"))
			await talk.call("m_mage"); print("job: ", c.job, " hot ", c.hot)
			await talk.call("elder"); print("q_job: ", Rules.quest_state(c, "q_job"))
			await talk.call("captain"); print("q_dogs: ", Rules.quest_state(c, "q_dogs"))
			# 술사 불꽃
			main().go_map("field", Vector2i(40, 8)); await wait(1.2)
			p = player()
			p.target = p.find_target(9)
			await tap("hot1"); await wait(0.15); await shot("story_fire"); await wait(0.5)
			print("fire target hp: ", p.target.hp if p.target and is_instance_valid(p.target) else "none", " mp ", c.mp)
			# 가게
			main().go_map("town", Vector2i(8, 15)); await wait(1.2)
			c.gold = 100
			await talk.call("hana")
			await wait(0.3); await shot("story_shop")
			await tap("talk"); await wait(0.2)
			print("shop win: ", main().hud.win_kind, " gold ", c.gold, " riceball ", Rules.count(c, "riceball"))
			await tap("cancel")
		"maps":
			for k in ["field", "forest", "cave1", "cave2", "camp"]:
				main().go_map(k, Vector2i(-1, -1)); await wait(1.3)
				await shot("map_" + k)
	await wait(0.2)
	get_tree().quit()
