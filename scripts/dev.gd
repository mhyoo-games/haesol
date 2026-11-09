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
		"maps":
			for k in ["field", "forest", "cave1", "cave2", "camp"]:
				main().go_map(k, Vector2i(-1, -1)); await wait(1.3)
				await shot("map_" + k)
	await wait(0.2)
	get_tree().quit()
