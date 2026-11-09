extends "res://scripts/actor.gd"
## 몬스터: 어슬렁거리다 (사나운 놈은 보이면) 쫓아와 문다. 맞으면 쫓아온다.

signal died

var mon := "rabbit"
var info := {}
var hp := 10
var dead := false
var home := Vector2i.ZERO
var angry := false
var think_t := 0.0
var bite_t := 0.0
var slow_until := 0.0
var bar: Node2D
var human := false
var spawner: Node
var big := false
var slam_t := 4.0

func _ready() -> void:
	add_to_group("monster")
	info = DB.monsters[mon]
	hp = int(info.hp)
	human = info.get("human", false)
	big = info.get("big", false)
	step_time = float(info.speed)
	home = cell
	angry = info.ai == "aggro" and false
	add_child(Fx.shadow(30 if big else 18, 6))
	if human:
		make_sprite(Fx.tex("mon_" + mon), 7, 3)
	else:
		var tex := Fx.tex("mon_" + mon)
		make_sprite(tex, 4, 1, Vector2(0, -tex.get_height() / 2.0 + 2))
	if info.get("boss", false):
		spr.scale = Vector2(1.25, 1.25) if human else Vector2.ONE
		add_name(info.name, Color(1, 0.55, 0.45), -70 if big else -60)
	else:
		add_name(info.name, Color(0.95, 0.85, 0.55), -40 if not human else -52)
		name_lbl.visible = false
	bar = Node2D.new()
	bar.z_index = 41
	bar.visible = false
	add_child(bar)
	bar.draw.connect(_draw_bar)
	think_t = randf() * 2.0

func _draw_bar() -> void:
	var w := 26.0 if not big else 40.0
	var y := -36.0 if not human else -50.0
	if big: y = -58.0
	bar.draw_rect(Rect2(-w / 2 - 1, y - 1, w + 2, 5), Color(0.05, 0.03, 0.06))
	bar.draw_rect(Rect2(-w / 2, y, w * hp / float(info.hp), 3), Color(0.85, 0.25, 0.2))

func update_frame() -> void:
	if human:
		super.update_frame()
		return
	spr.flip_h = facing.x < 0
	var now := Time.get_ticks_msec() / 1000.0
	if now < act_until: spr.frame = act_frame
	elif moving: spr.frame = int(walk_dist / 8.0) % 2
	else: spr.frame = 0

func _player() -> Node:
	return world.player

func _process(delta: float) -> void:
	if dead: return
	move_tick(delta)
	update_frame()
	if Game.busy: return
	var p := _player()
	if p == null or not is_instance_valid(p): return
	var now := Time.get_ticks_msec() / 1000.0
	step_time = float(info.speed) * (1.8 if now < slow_until else 1.0)
	var d: int = p.dist_to(cell)
	if info.ai == "aggro" and d <= int(info.get("sight", 4)) and Game.c.hp > 0: angry = true
	if d > 14: angry = false
	think_t -= delta
	bite_t -= delta
	if info.get("boss", false) and angry:
		slam_t -= delta
		if slam_t <= 0 and d <= 2:
			slam_t = 4.5
			_slam(p)
			return
	if moving or think_t > 0: return
	if angry and Game.c.hp > 0:
		if d == 1:
			facing = p.cell - cell
			if bite_t <= 0:
				bite_t = 1.3
				pose(2 if not human else 4, 0.25)
				get_tree().create_timer(0.15).timeout.connect(func():
					if not dead and is_instance_valid(p) and p.dist_to(cell) == 1:
						p.hurt(Rules.mon_damage(mon, Game.c, randf()), self))
			think_t = 0.2
		else:
			_chase(p.cell)
			think_t = 0.05
	else:
		think_t = randf_range(1.0, 2.6)
		var dirs := [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]
		var dd: Vector2i = dirs[randi() % 4]
		if (cell + dd - home).length() < 6: try_step(dd)

func _chase(goal: Vector2i) -> void:
	# 가까운 칸 BFS (12칸 안), 없으면 가로세로로 다가감
	var start := cell
	var prev := {start: start}
	var q := [start]
	var found := false
	while not q.is_empty() and prev.size() < 400:
		var c: Vector2i = q.pop_front()
		if (c - goal).length_squared() == 1:
			goal = c; found = true; break
		for dd in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var n: Vector2i = c + dd
			if prev.has(n) or not world.is_free(n, self) or (n - start).length() > 12: continue
			prev[n] = c
			q.append(n)
	if found and goal != start:
		var c := goal
		while prev[c] != start: c = prev[c]
		try_step(c - start)
	else:
		var diff := goal - cell
		var dd := Vector2i(signi(diff.x), 0) if absi(diff.x) > absi(diff.y) else Vector2i(0, signi(diff.y))
		try_step(dd)

func _slam(p: Node) -> void:
	# 대왕 내려찍기: 둘레 두 칸
	pose(2 if not human else 5, 0.6)
	flash(Color(1, 0.8, 0.3))
	Game.say("%s이(가) 크게 몸을 들어 올린다!" % info.name, Color(1, 0.6, 0.5))
	get_tree().create_timer(0.6).timeout.connect(func():
		if dead: return
		Sound.play("stomp", 0.0)
		Fx.anim(world.ysort, "puff", 5, position + Vector2(0, -10), 14, 6)
		if is_instance_valid(p) and maxi(absi(p.cell.x - cell.x), absi(p.cell.y - cell.y)) <= 2:
			p.hurt(int(Rules.mon_damage(mon, Game.c, randf()) * 1.6), self))

func hurt(dmg: int, from: Node) -> void:
	if dead: return
	hp -= dmg
	angry = true
	bar.visible = true
	bar.queue_redraw()
	flash()
	Fx.number(world.ysort, position, str(dmg))
	if from: from.combat_t = 6.0
	if hp <= 0: _die(from)

func _die(killer: Node) -> void:
	dead = true
	remove_from_group("monster")
	world.release(self)
	Sound.play("enemy_die", 0.1)
	Fx.anim(world.ysort, "puff", 5, position + Vector2(0, -14), 16, 6)
	var c: Dictionary = Game.c
	var ex := Rules.exp_for(mon, c.lv)
	var ups := Rules.gain_exp(c, ex)
	var g := randi_range(int(info.gold[0]), int(info.gold[1]))
	c.gold += g
	Game.say("%s을(를) 잡았다. 경험치 +%d%s" % [info.name, ex, (", 전 +%d" % g) if g > 0 else ""], Color(0.85, 0.85, 0.75))
	for d in info.drops:
		var id: String = d[0]
		if d.size() > 2 and not Rules.quest_drop_ok(c, d[2], id): continue
		if randf() < float(d[1]):
			if Rules.add_item(c, id):
				Game.say("%s을(를) 얻었다." % DB.items[id].name, Color(0.7, 0.9, 1))
				Sound.play("coin", 0.05, -4)
			else:
				Game.say("가방이 가득 차서 %s을(를) 줍지 못했다." % DB.items[id].name, UI.DIM)
	for qid in Rules.on_kill(c, mon):
		Game.say("[%s] %s" % [DB.quest(qid).name, Rules.progress_text(c, qid)], Color(1, 0.9, 0.5))
	if ups > 0:
		Game.say("레벨이 올랐다! (레벨 %d)" % c.lv, Color(1, 0.85, 0.3))
		Sound.play("chest", 0.0)
		get_tree().call_group("main", "level_up")
	Game.touch()
	died.emit()
	var tw := create_tween()
	tw.tween_property(self, "modulate:a", 0.0, 0.3)
	tw.tween_callback(queue_free)
