extends "res://scripts/actor.gd"
## 주인공: 칸 이동, 앞 칸 치기, 기술·물건 단축키, 말 걸기, 출구.

var cam: Camera2D
var wpn: Sprite2D
var target: Node = null
var cooldowns := {}
var atk_ready := 0.0
var regen_t := 0.0
var combat_t := 0.0
var look_key := ""

func _ready() -> void:
	add_to_group("player")
	step_time = 0.24
	add_child(Fx.shadow(18, 6))
	make_sprite(null)
	wpn = Sprite2D.new()
	wpn.hframes = 7; wpn.vframes = 3
	wpn.offset = Vector2(0, -22)
	add_child(wpn)
	add_name(Game.c.name, Color(1, 1, 1))
	refresh_look()
	Game.changed.connect(refresh_look)

func look() -> Dictionary:
	var c: Dictionary = Game.c
	return {"g": c.g, "hair": c.hair, "hc": c.hc, "outfit": Rules.job(c).outfit}

func refresh_look() -> void:
	var lk := look()
	var w: String = DB.items.get(Game.c.equip.get("weapon", ""), {}).get("look", "")
	var k := str(lk) + w
	if k == look_key: return
	look_key = k
	spr.texture = Doll.texture(lk)
	wpn.texture = Fx.tex("weapon_" + w) if w != "" else null

func _now() -> float:
	return Time.get_ticks_msec() / 1000.0

func _process(delta: float) -> void:
	update_frame()
	wpn.frame = spr.frame
	wpn.flip_h = spr.flip_h
	wpn.z_index = -1 if facing.y < 0 else 1
	var c: Dictionary = Game.c
	# 버프 끝내기
	for k in c.buffs.keys():
		if c.buffs[k].until < _now(): c.buffs.erase(k); Game.say("기운이 가라앉았다.", UI.DIM)
	# 천천히 회복 (싸우지 않을 때 더 빨리)
	regen_t += delta
	combat_t = maxf(0.0, combat_t - delta)
	if regen_t > 2.0:
		regen_t = 0.0
		var k := 0.04 if combat_t <= 0 else 0.01
		c.hp = mini(Rules.max_hp(c), c.hp + maxi(1, int(Rules.max_hp(c) * k)))
		c.mp = mini(Rules.max_mp(c), c.mp + maxi(1, int(Rules.max_mp(c) * k * 1.5)))
		Game.touch()
	if Game.busy or c.hp <= 0: return
	var d := Vector2i.ZERO
	if Input.is_action_pressed("left"): d = Vector2i(-1, 0)
	elif Input.is_action_pressed("right"): d = Vector2i(1, 0)
	elif Input.is_action_pressed("up"): d = Vector2i(0, -1)
	elif Input.is_action_pressed("down"): d = Vector2i(0, 1)
	if d != Vector2i.ZERO and not moving and _now() >= act_until:
		try_step(d)
	if Input.is_action_pressed("attack") and _now() >= atk_ready and not moving:
		_attack()
	if Input.is_action_just_pressed("talk"):
		_talk()
	if Input.is_action_just_pressed("target"):
		target = find_target(9, target)
	for i in 8:
		if Input.is_action_just_pressed("hot%d" % (i + 1)):
			use_hot(i)

func use_hot(i: int) -> void:
	var id: String = Game.c.hot[i]
	if id == "": return
	if DB.skills.has(id):
		var why := Combat.cast(self, id)
		if why != "": Game.say(why, UI.DIM)
	elif DB.items.has(id):
		for k in Game.c.inv.size():
			if Game.c.inv[k].id == id:
				Rules.use_item(Game.c, k)
				Sound.play("heal", 0.05)
				Fx.number(world.ysort, position, DB.items[id].name, Color(0.7, 1, 0.7))
				Game.touch()
				return
		Game.say("%s이(가) 없습니다." % DB.items[id].name, UI.DIM)

func _attack() -> void:
	var spd: float = Rules.job(Game.c).speed
	atk_ready = _now() + spd
	pose(3, spd * 0.3)
	get_tree().create_timer(spd * 0.3).timeout.connect(func():
		pose(4, spd * 0.4)
		var m = world.actor_at(cell + facing)
		if m and m.is_in_group("monster") and not m.dead:
			Combat.hit_monster(self, m, 1.0)
			target = m
			Sound.play("hit", 0.1)
		else:
			Sound.play("swing", 0.1, -6))

func _talk() -> void:
	var a = world.actor_at(cell + facing)
	if a and a.is_in_group("npc"):
		a.face_to(cell)
		Talk.npc(get_tree(), a.npc_id)
		return
	var s = world.signs.get(cell + facing)
	if s: get_tree().call_group("main", "dialog", s)

func find_target(r: int, after: Node = null) -> Node:
	var list := []
	for m in get_tree().get_nodes_in_group("monster"):
		if not m.dead and m.dist_to(cell) <= r: list.append(m)
	if list.is_empty(): return null
	list.sort_custom(func(a, b): return a.dist_to(cell) < b.dist_to(cell))
	if after and after in list:
		return list[(list.find(after) + 1) % list.size()]
	return list[0]

func on_arrive() -> void:
	check_portal()

func check_portal() -> void:
	var p = world.portals.get(cell)
	if p == null: return
	var need: String = p.get("need", "")
	if need.begins_with("done:") and Rules.quest_state(Game.c, need.substr(5)) != "done":
		Game.say("길이 무너진 바위로 막혀 있다. 아직은 지나갈 수 없다.", UI.DIM)
		return
	get_tree().call_group("main", "go_map", p.to, Vector2i(p.tx, p.ty))

func hurt(dmg: int, from: Node) -> void:
	var c: Dictionary = Game.c
	if c.hp <= 0: return
	c.hp = maxi(0, c.hp - dmg)
	combat_t = 6.0
	flash(Color(1, 0.4, 0.4))
	Fx.number(world.ysort, position, str(dmg), Color(1, 0.45, 0.4))
	Sound.play("hurt", 0.1, -4)
	pose(6, 0.15)
	Game.touch()
	if c.hp <= 0:
		get_tree().call_group("main", "player_died")
