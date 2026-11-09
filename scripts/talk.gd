class_name Talk
extends RefCounted
## 사람과의 대화: 퀘스트 주고받기, 가게, 직업 스승.

static func _main(tree: SceneTree) -> Node:
	return tree.get_first_node_in_group("main")

static func offers(id: String) -> Array:
	var out := []
	for q in DB.quests:
		if q.giver == id and Rules.can_offer(Game.c, q): out.append(q)
	return out

static func turn_ins(id: String) -> Array:
	var out := []
	for q in DB.quests:
		var st := Rules.quest_state(Game.c, q.id)
		if st != "active": continue
		var finisher: String = q.goal.get("talk", q.giver)
		if finisher == id and (Rules.goal_met(Game.c, q.id) or q.goal.has("talk")): out.append(q)
	return out

static func has_turn_in(id: String) -> bool:
	return not turn_ins(id).is_empty()

static func has_news(id: String) -> bool:
	return has_turn_in(id) or not offers(id).is_empty() or _master_ready(id)

static func _master_ready(id: String) -> bool:
	var n: Dictionary = DB.npcs.get(id, {})
	return n.has("master") and Game.c.job == "none" and Rules.quest_state(Game.c, "q_job") == "active"

static func npc(tree: SceneTree, id: String) -> void:
	var c: Dictionary = Game.c
	var n: Dictionary = DB.npcs[id]
	var m := _main(tree)
	# 1) 끝낼 퀘스트
	for q in turn_ins(id):
		if q.goal.has("talk"): c.quests[q.id].talked = true
		if Rules.goal_met(c, q.id):
			m.dialog(q.done, func():
				var r := Rules.complete(c, q.id)
				Game.say("[%s] 완료! 경험치 +%d, 전 +%d" % [q.name, int(q.reward.get("exp", 0)), int(q.reward.get("gold", 0))], Color(1, 0.85, 0.4))
				for pair in q.reward.get("items", []):
					Game.say("%s ×%d을(를) 받았다." % [DB.items[pair[0]].name, int(pair[1])], Color(0.7, 0.9, 1))
				if r.ups > 0:
					Game.say("레벨이 올랐다! (레벨 %d)" % c.lv, Color(1, 0.85, 0.3))
					m.level_up()
				Sound.play("chest", 0.0)
				Game.touch()
				Game.save())
			return
	# 2) 새 퀘스트
	var off := offers(id)
	if not off.is_empty():
		var q: Dictionary = off[0]
		m.dialog(q.offer, func(i: int):
			if i == 0:
				Rules.accept(c, q)
				Game.say("[%s] 퀘스트를 받았다: %s" % [q.name, Rules.progress_text(c, q.id)], Color(1, 0.9, 0.5))
				Sound.play("select", 0.0)
				Game.touch()
			else:
				m.dialog([[id, "마음이 바뀌면 다시 오게."]]), ["맡겠습니다", "나중에"])
		return
	# 3) 직업 스승
	if _master_ready(id):
		var j: String = n.master
		var jd: Dictionary = DB.jobs[j]
		m.dialog([[id, DB.npcs[id].idle[0]], [id, "%s의 길: %s" % [jd.name, jd.desc]], [id, "이 길을 걷겠느냐? 한 번 고르면 되돌릴 수 없다."]], func(i: int):
			if i == 0:
				Rules.set_job(c, j)
				Game.say("%s이(가) 되었다! 무기를 받았다: %s" % [jd.name, DB.items[c.equip.weapon].name], Color(1, 0.85, 0.3))
				var sk := Rules.skills_of(c)
				for k in sk.size(): c.hot[k] = sk[k]
				Sound.play("chest", 0.0)
				Game.touch()
				Game.save()
				m.dialog([[id, "좋다. 1번 단축키에 첫 기술을 넣어 두었다. 수련을 게을리하지 마라."]])
			else:
				m.dialog([[id, "천천히 생각해 보거라."]]), ["이 길을 걷겠습니다", "다시 생각하겠습니다"])
		return
	# 4) 진행 중 퀘스트 한마디
	for q in DB.quests:
		if q.giver == id and Rules.quest_state(c, q.id) == "active":
			m.dialog(q.progress + [["", "[%s] %s" % [q.name, Rules.progress_text(c, q.id)]]])
			return
	# 5) 가게
	if n.has("shop"):
		m.dialog([[id, n.idle[randi() % n.idle.size()]]], func(): m.open_shop(n.shop))
		return
	m.dialog([[id, n.idle[randi() % n.idle.size()]]])
