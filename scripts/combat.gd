class_name Combat
extends RefCounted
## 공격·기술을 실제 화면의 적에게 적용 (계산은 Rules)

static func hit_monster(p: Node, m: Node, power: float, magic := false) -> void:
	if m == null or not is_instance_valid(m) or m.dead: return
	var c: Dictionary = Game.c
	var a := float(Rules.matk(c) if magic else Rules.atk(c))
	var dmg := Rules.damage(a, power, float(DB.monsters[m.mon].def), randf())
	m.hurt(dmg, p)

static func monsters_near(world: Node, center: Vector2i, r: int) -> Array:
	var out := []
	for dy in range(-r, r + 1):
		for dx in range(-r, r + 1):
			var a = world.actor_at(center + Vector2i(dx, dy))
			if a and a.is_in_group("monster") and not a.dead: out.append(a)
	return out

## 기술 쓰기. 실패하면 까닭을 돌려준다.
static func cast(p: Node, sid: String) -> String:
	var c: Dictionary = Game.c
	var s: Dictionary = DB.skills[sid]
	if not sid in Rules.skills_of(c): return "아직 쓸 수 없는 기술입니다."
	var now := Time.get_ticks_msec() / 1000.0
	if p.cooldowns.get(sid, 0.0) > now: return ""
	if c.mp < int(s.mp): return "기력이 모자랍니다."
	var tgt: Node = p.target if p.target and is_instance_valid(p.target) and not p.target.dead else null
	var w: Node = p.world
	match s.kind:
		"target", "area":
			if tgt == null or tgt.dist_to(p.cell) > int(s.range): tgt = p.find_target(int(s.range))
			if tgt == null: return "가까이에 적이 없습니다."
			p.target = tgt
			var bolt := preload("res://scripts/bolt.gd").new()
			bolt.kind = sid
			bolt.from = p.position + Vector2(0, -24)
			bolt.to_node = tgt
			w.ysort.add_child(bolt)
			bolt.landed.connect(func():
				if s.kind == "area":
					for m in monsters_near(w, tgt.cell, int(s.radius)): hit_monster(p, m, float(s.power), true)
				else:
					hit_monster(p, tgt, float(s.power), s.get("magic", false))
					if s.has("slow") and is_instance_valid(tgt): tgt.slow_until = Time.get_ticks_msec() / 1000.0 + float(s.slow))
		"around":
			for m in monsters_near(w, p.cell, 1): hit_monster(p, m, float(s.power))
			Fx.anim(w.ysort, "puff", 5, p.position + Vector2(0, -14), 20, 6)
		"front":
			var m = w.actor_at(p.cell + p.facing)
			if m == null or not m.is_in_group("monster"): return "앞에 적이 없습니다."
			for i in int(s.hits):
				p.get_tree().create_timer(0.1 * i).timeout.connect(func(): hit_monster(p, m, float(s.power)))
		"line":
			var m: Node = null
			for k in range(1, int(s.range) + 1):
				var a = w.actor_at(p.cell + p.facing * k)
				if a and a.is_in_group("monster"): m = a; break
				if not w.walkable(p.cell + p.facing * k): break
			if m == null: return "보는 쪽에 적이 없습니다."
			var bolt := preload("res://scripts/bolt.gd").new()
			bolt.kind = sid
			bolt.from = p.position + Vector2(0, -24)
			bolt.to_node = m
			w.ysort.add_child(bolt)
			bolt.landed.connect(func(): hit_monster(p, m, float(s.power)))
		"dash":
			var hit: Node = null
			for k in int(s.range):
				var nxt: Vector2i = p.cell + p.facing
				var a = w.actor_at(nxt)
				if a and a.is_in_group("monster"): hit = a; break
				if not w.is_free(nxt, p): break
				w.move_actor(p, p.cell, nxt)
				p.cell = nxt
			p.position = Actor.cell_pos(p.cell)
			Fx.anim(w.ysort, "puff", 5, p.position + Vector2(0, -10), 22, 6)
			if hit: hit_monster(p, hit, float(s.power))
			p.check_portal()
		"blink":
			var m: Node = p.find_target(int(s.range))
			if m == null: return "가까이에 적이 없습니다."
			var behind: Vector2i = m.cell + (m.cell - p.cell).sign()
			for cand in [behind, m.cell + Vector2i(1, 0), m.cell + Vector2i(-1, 0), m.cell + Vector2i(0, 1), m.cell + Vector2i(0, -1)]:
				if w.is_free(cand, p):
					Fx.anim(w.ysort, "puff", 5, p.position + Vector2(0, -16), 20, 6)
					w.move_actor(p, p.cell, cand)
					p.cell = cand
					p.position = Actor.cell_pos(cand)
					p.facing = (m.cell - cand).sign()
					break
			hit_monster(p, m, float(s.power))
		"heal":
			var n := int(Rules.matk(c) * float(s.power)) + 10
			c.hp = mini(Rules.max_hp(c), c.hp + n)
			Fx.number(w.ysort, p.position, "+%d" % n, Color(0.6, 1, 0.6))
			Fx.anim(w.ysort, "spark", 4, p.position + Vector2(0, -24), 14, 6)
		"buff":
			c.buffs[s.stat] = {"amount": s.amount, "until": now + float(s.time)}
			Game.say("%s! (%d초)" % [s.name, int(s.time)], Color(1, 0.85, 0.5))
			Fx.anim(w.ysort, "spark", 4, p.position + Vector2(0, -28), 12, 6)
	c.mp -= int(s.mp)
	p.cooldowns[sid] = now + float(s.cd)
	p.pose(5 if s.get("magic", false) or s.kind in ["heal", "buff"] else 4, 0.25)
	Sound.play("fire" if s.get("magic", false) else "swing", 0.1)
	Game.touch()
	return ""
