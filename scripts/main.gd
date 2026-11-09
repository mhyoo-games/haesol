extends Node
## 화면 전환: 처음 화면 → 캐릭터 만들기 → 지도. 지도 이동, 쓰러짐, 레벨업.

var world: Node2D
var hud: CanvasLayer
var title: Control
var fade: ColorRect
var moving := false

func _ready() -> void:
	add_to_group("main")
	hud = preload("res://scripts/hud.gd").new()
	add_child(hud)
	var fl := CanvasLayer.new(); fl.layer = 30; add_child(fl)
	fade = ColorRect.new(); fade.color = Color(0.05, 0.03, 0.07); fade.size = Vector2(640, 480)
	fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	fl.add_child(fade)
	show_title()
	_fade(0.0, 0.6)

func _fade(a: float, sec := 0.3) -> void:
	var tw := create_tween()
	tw.tween_property(fade, "modulate:a", a, sec)
	await tw.finished

func show_title() -> void:
	Game.busy = false
	if world: world.queue_free(); world = null
	hud.visible = false
	title = preload("res://scripts/title.gd").new()
	add_child(title)
	Sound.music("title")

func start(c: Dictionary, is_new: bool) -> void:
	Game.c = c
	await _fade(1.0, 0.4)
	if title: title.queue_free(); title = null
	hud.visible = true
	_load(c.map, Vector2i(int(c.x), int(c.y)))
	hud.refresh()
	await _fade(0.0, 0.5)
	if is_new:
		dialog([["me", "…여기가 해솔성. 불타 버린 우리 마을에서 사흘을 걸어왔다."],
			["me", "살아남으려면 여기서 뭐든 해야 해. 성문 쪽 갑옷 입은 사람한테 먼저 가 보자."],
			["", "방향키 이동 · 스페이스 공격 · Enter 말 걸기 · 1~8 단축칸 · I 가방 · C 능력치 · K 기술 · Q 퀘스트 · Esc 메뉴"]])
		Game.say("해솔성에 왔다. 머리 위에 !가 뜬 사람에게 말을 걸어 보자.", UI.GOLD)

func _load(key: String, at: Vector2i) -> void:
	if world: world.queue_free()
	world = preload("res://scripts/world.gd").new()
	world.add_to_group("world")
	add_child(world)
	move_child(world, 0)
	world.build(key)
	if at.x < 0: at = world.entry_for("")
	world.spawn_player(at)
	Game.c.map = key
	Game.c.x = at.x; Game.c.y = at.y
	Sound.music(world.data.music)
	Game.say("— %s —" % world.data.name, UI.GOLD)
	Game.save()

func go_map(key: String, at: Vector2i) -> void:
	if moving: return
	moving = true
	Game.busy = true
	Sound.play("warp", 0.0, -10)
	await _fade(1.0, 0.25)
	_load.call_deferred(key, at)
	await get_tree().process_frame
	await get_tree().process_frame
	Game.busy = false
	await _fade(0.0, 0.3)
	moving = false

func _process(_d: float) -> void:
	if world and world.player and not moving:
		Game.c.x = world.player.cell.x; Game.c.y = world.player.cell.y

func dialog(lines: Array, cb := Callable(), choices: Array = []) -> void:
	hud.open_dialog(lines, cb, choices)

func open_shop(id: String) -> void:
	hud.open_shop(id)

func level_up() -> void:
	var c: Dictionary = Game.c
	if world and world.player:
		Fx.anim(world.ysort, "spark", 4, world.player.position + Vector2(0, -30), 10, 30)
	# 새로 배운 기술은 빈 단축칸에
	for sid in Rules.skills_of(c):
		if not sid in c.hot:
			for i in 5:
				if c.hot[i] == "":
					c.hot[i] = sid
					Game.say("새 기술을 익혔다: %s (단축칸 %d)" % [DB.skills[sid].name, i + 1], Color(0.7, 1, 0.8))
					break
	if c.lv == Rules.JOB_LV and c.job == "none":
		Game.say("레벨 5! 수련관 송학 노인을 찾아가면 직업을 얻을 수 있다.", UI.GOLD)
	Game.touch()
	Game.save()

func player_died() -> void:
	Game.busy = true
	Game.say("정신을 잃었다…", Color(1, 0.5, 0.5))
	await get_tree().create_timer(1.0).timeout
	var c: Dictionary = Game.c
	var lost := int(c.exp * 0.1)
	c.exp -= lost
	c.hp = Rules.max_hp(c); c.mp = Rules.max_mp(c)
	moving = false
	Game.busy = false
	await go_map("town", Vector2i(23, 22))
	Game.say("주막에서 눈을 떴다. 경험치를 조금 잃었다. (-%d)" % lost, Color(1, 0.7, 0.6))
