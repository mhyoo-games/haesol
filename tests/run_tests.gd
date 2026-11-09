extends SceneTree
## godot --headless -s tests/run_tests.gd  (규칙·데이터·지도가 서로 맞는지)

var fails := 0
var passes := 0

func ok(cond: bool, what: String) -> void:
	if cond: passes += 1
	else:
		fails += 1
		printerr("실패: ", what)

func _init() -> void:
	var db = load("res://scripts/core/db.gd").new()
	db.name = "DB"
	root.add_child(db)
	db.load_all()
	await process_frame
	_rules(db)
	_data(db)
	_maps(db)
	print("통과 %d, 실패 %d" % [passes, fails])
	quit(1 if fails > 0 else 0)

func _rules(db) -> void:
	var c := Rules.new_character("시험", "m", "short", "black")
	ok(c.hp == Rules.max_hp(c) and c.lv == 1, "새 캐릭터 체력이 가득")
	ok(Rules.exp_need(1) < Rules.exp_need(2) and Rules.exp_need(10) > 600, "경험치 곡선")
	var ups := Rules.gain_exp(c, Rules.exp_need(1) + Rules.exp_need(2) + 1)
	ok(ups == 2 and c.lv == 3 and c.exp == 1, "두 번 레벨업")
	ok(Rules.damage(10, 1, 100, 0.5) == 1, "피해는 최소 1")
	ok(Rules.damage(20, 1.5, 4, 0.5) == 28, "피해 계산")
	ok(Rules.add_item(c, "riceball", 3) and Rules.count(c, "riceball") == 8, "겹치는 물건")
	ok(Rules.add_item(c, "cap") and Rules.count(c, "cap") == 1, "장비 넣기")
	var i := -1
	for k in c.inv.size():
		if c.inv[k].id == "cap": i = k
	ok(Rules.equip(c, i) == "" and c.equip.head == "cap" and Rules.defense(c) > 1, "두건 쓰기")
	ok(Rules.can_equip(c, "sword1") != "", "직업 없이는 검을 못 씀")
	Rules.set_job(c, "warrior")
	ok(c.equip.weapon == "sword1" and Rules.count(c, "club0") == 1, "검사가 되면 무쇠검, 몽둥이는 가방으로")
	ok(Rules.skills_of(c).is_empty(), "레벨 3 검사는 기술 없음")
	c.lv = 9
	ok(Rules.skills_of(c).size() == 2, "레벨 9 검사 기술 둘")
	c.gold = 5
	ok(Rules.buy(c, "pill") != "" and c.gold == 5, "돈이 모자라면 못 삼")
	c.gold = 100
	ok(Rules.buy(c, "pill") == "" and c.gold == 75, "약초환 사기")
	var before: int = c.gold
	var pi := -1
	for k in c.inv.size():
		if c.inv[k].id == "pill": pi = k
	ok(Rules.sell(c, pi) == "" and c.gold == before + 12, "반값에 팔기")
	ok(Rules.exp_for("rabbit", 1) == 6 and Rules.exp_for("rabbit", 20) < 6, "약한 적은 경험치 덜 줌")
	# 퀘스트 흐름
	var q2 := Rules.new_character("퀘", "f", "bun", "brown")
	var q: Dictionary = db.quest("q_rabbit")
	ok(Rules.can_offer(q2, q), "첫 퀘스트를 받을 수 있음")
	ok(not Rules.can_offer(q2, db.quest("q_tail")), "앞 퀘스트를 끝내야 다음")
	Rules.accept(q2, q)
	for k in 4: Rules.on_kill(q2, "rabbit")
	ok(not Rules.goal_met(q2, "q_rabbit"), "토끼 넷은 모자람")
	Rules.on_kill(q2, "rabbit"); Rules.on_kill(q2, "rabbit")
	ok(Rules.goal_met(q2, "q_rabbit") and q2.quests.q_rabbit.kills.rabbit == 5, "다섯에서 멈춤")
	Rules.complete(q2, "q_rabbit")
	ok(Rules.quest_state(q2, "q_rabbit") == "done" and Rules.count(q2, "cap") == 1, "보상 받기")
	ok(Rules.can_offer(q2, db.quest("q_tail")), "다음 퀘스트 열림")
	Rules.accept(q2, db.quest("q_tail"))
	Rules.add_item(q2, "tail", 5)
	ok(Rules.goal_met(q2, "q_tail"), "꼬리 다섯")
	Rules.complete(q2, "q_tail")
	ok(Rules.count(q2, "tail") == 0, "꼬리는 가져감")
	ok(not Rules.quest_drop_ok(q2, "q_dogs", "blackcloth"), "받지 않은 퀘스트 물건은 안 떨어짐")

func _data(db) -> void:
	for sid in db.skills:
		var s: Dictionary = db.skills[sid]
		ok(db.jobs.has(s.job), "기술의 직업: " + sid)
		ok(ResourceLoader.exists("res://assets/sprites/skill_%s.png" % sid), "기술 아이콘: " + sid)
	for iid in db.items:
		ok(ResourceLoader.exists("res://assets/sprites/icon_%s.png" % iid), "물건 아이콘: " + iid)
	for mid in db.monsters:
		var m: Dictionary = db.monsters[mid]
		ok(ResourceLoader.exists("res://assets/sprites/mon_%s.png" % mid), "몬스터 그림: " + mid)
		for d in m.drops:
			ok(db.items.has(d[0]), "%s가 떨어뜨리는 물건 %s" % [mid, d[0]])
			if d.size() > 2: ok(not db.quest(d[2]).is_empty(), "퀘스트 떨굼 %s" % d[2])
	for sh in db.shops:
		for it in db.shops[sh].items: ok(db.items.has(it), "가게 물건 " + it)
	var seen := {}
	for q in db.quests:
		ok(db.npcs.has(q.giver), "퀘스트 주는 사람 " + q.giver)
		if q.has("after"): ok(seen.has(q.after), "%s 앞 퀘스트가 먼저 나옴" % q.id)
		seen[q.id] = true
		for m in q.goal.get("kill", {}): ok(db.monsters.has(m), "퀘스트 몬스터 " + m)
		for it in q.goal.get("item", {}):
			ok(db.items.has(it), "퀘스트 물건 " + it)
			var from := false
			for mid in db.monsters:
				for d in db.monsters[mid].drops:
					if d[0] == it: from = true
			ok(from or it == "tail", "%s를 얻을 곳이 있음" % it)
		for line in q.offer + q.done + q.progress:
			ok(line[0] == "" or line[0] == "me" or db.npcs.has(line[0]), "말하는 사람 " + str(line[0]))
		for pair in q.reward.get("items", []): ok(db.items.has(pair[0]), "보상 " + pair[0])
	for nid in db.npcs:
		ok(ResourceLoader.exists("res://assets/sprites/portrait_%s.png" % nid), "얼굴 그림 " + nid)

func _maps(db) -> void:
	var W = load("res://scripts/world.gd")
	var placed := {}
	for k in db.maps:
		var m: Dictionary = db.maps[k]
		ok(m.ground.size() == m.h and m.objects.size() == m.h, k + " 줄 수")
		# 막힌 칸
		var blocked := {}
		for y in m.h:
			for x in m.w:
				var g: String = m.ground[y][x]
				var o: String = m.objects[y][x]
				if g == "W" or (o != " " and not W.PASSABLE.contains(o)): blocked[Vector2i(x, y)] = true
		for e in m.entities:
			if e.type in ["house", "stall", "tent"]:
				for yy in range(e.y - e.fh + 1, e.y + 1):
					for xx in range(e.x, e.x + e.fw): blocked[Vector2i(xx, yy)] = true
			if e.type == "well":
				for yy in range(e.y - 1, e.y + 1):
					for xx in range(e.x, e.x + 2): blocked[Vector2i(xx, yy)] = true
			if e.type in ["campfire", "torch", "sign"]: blocked[Vector2i(e.x, e.y)] = true
		# 들어오는 칸들
		var starts := []
		for kk in db.maps:
			for e in db.maps[kk].entities:
				if e.type == "portal" and e.to == k: starts.append(Vector2i(e.tx, e.ty))
		for e in m.entities:
			if e.type == "start": starts.append(Vector2i(e.x, e.y))
		ok(not starts.is_empty(), k + " 들어오는 자리")
		for s in starts:
			ok(not blocked.has(s), "%s 도착 칸 %s 이 비어 있음" % [k, s])
			var seen := {s: true}
			var q := [s]
			while not q.is_empty():
				var c: Vector2i = q.pop_back()
				for d in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
					var n: Vector2i = c + d
					if n.x < 0 or n.y < 0 or n.x >= m.w or n.y >= m.h or seen.has(n) or blocked.has(n): continue
					seen[n] = true; q.append(n)
			for e in m.entities:
				var targets := []
				match e.type:
					"npc": targets = [Vector2i(e.x, e.y) + Vector2i(1, 0), Vector2i(e.x, e.y) + Vector2i(-1, 0), Vector2i(e.x, e.y) + Vector2i(0, 1), Vector2i(e.x, e.y) + Vector2i(0, -1)]
					"portal":
						for yy in range(e.y, e.y + e.get("h", 1)):
							for xx in range(e.x, e.x + e.get("w", 1)): targets.append(Vector2i(xx, yy))
					"boss": targets = [Vector2i(e.x, e.y)]
				if targets.is_empty(): continue
				var any := false
				for t in targets:
					if seen.has(t): any = true
				ok(any, "%s: %s에서 %s(%s)에 닿음" % [k, s, e.type, e.get("id", e.get("to", e.get("mon", "")))])
		for e in m.entities:
			if e.type == "npc":
				ok(db.npcs.has(e.id), "지도 위 사람 " + e.id)
				placed[e.id] = true
			if e.type in ["spawn", "boss"]: ok(db.monsters.has(e.mon), "지도 위 몬스터 " + e.mon)
	for q in db.quests:
		ok(placed.has(q.giver), "퀘스트 주는 사람이 지도에 있음 " + q.giver)
		for m in q.goal.get("kill", {}):
			var found := false
			for k in db.maps:
				for e in db.maps[k].entities:
					if e.type in ["spawn", "boss"] and e.mon == m: found = true
			ok(found, "잡을 몬스터가 지도에 있음 " + m)
