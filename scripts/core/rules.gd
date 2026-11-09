class_name Rules
extends RefCounted
## 게임 규칙 계산. 화면과 상관없이 숫자만 다룬다 (나중에 서버로 옮길 수 있게).
## 캐릭터 상태 c = {job, lv, exp, hp, mp, gold, inv:[{id,n}], equip:{weapon,head,body,acc}, quests:{}, buffs:{}}

const MAX_LV := 30
const INV_SIZE := 24
const JOB_LV := 5

static func exp_need(lv: int) -> int:
	return int(round(30.0 * pow(lv, 1.75)))

static func job(c: Dictionary) -> Dictionary:
	return DB.jobs.get(c.get("job", "none"), DB.jobs["none"])

static func equip_sum(c: Dictionary, key: String) -> float:
	var t := 0.0
	for slot in c.get("equip", {}):
		var id = c.equip[slot]
		if id != null and id != "" and DB.items.has(id):
			t += float(DB.items[id].get(key, 0))
	return t

static func max_hp(c: Dictionary) -> int:
	var j := job(c)
	return int(j.hp + j.hp_lv * (c.lv - 1) + equip_sum(c, "hp"))

static func max_mp(c: Dictionary) -> int:
	var j := job(c)
	return int(j.mp + j.mp_lv * (c.lv - 1) + equip_sum(c, "mp"))

static func buff(c: Dictionary, stat: String) -> float:
	var b: Dictionary = c.get("buffs", {})
	return 1.0 + (float(b[stat].amount) if b.has(stat) else 0.0)

static func atk(c: Dictionary) -> int:
	var j := job(c)
	return int((j.atk + j.atk_lv * (c.lv - 1) + equip_sum(c, "atk")) * buff(c, "atk"))

static func matk(c: Dictionary) -> int:
	var j := job(c)
	return int(float(j.get("matk", 0)) + float(j.get("matk_lv", 0)) * (c.lv - 1) + equip_sum(c, "matk"))

static func defense(c: Dictionary) -> int:
	var j := job(c)
	return int((j.def + j.def_lv * (c.lv - 1) + equip_sum(c, "def")) * buff(c, "def"))

## 피해: (공격 × 배율) - 방어/2, 최소 1. r = 0~1 흔들림
static func damage(attack: float, power: float, def: float, r: float) -> int:
	var raw := attack * power * (0.9 + r * 0.2) - def * 0.5
	return maxi(1, int(round(raw)))

## 몬스터의 공격력·방어
static func mon_damage(mon_id: String, c: Dictionary, r: float) -> int:
	var m: Dictionary = DB.monsters[mon_id]
	return damage(float(m.atk), 1.0, float(defense(c)), r)

## 경험치를 더하고 오른 레벨 수를 돌려준다
static func gain_exp(c: Dictionary, n: int) -> int:
	c.exp += n
	var ups := 0
	while c.lv < MAX_LV and c.exp >= exp_need(c.lv):
		c.exp -= exp_need(c.lv)
		c.lv += 1
		ups += 1
	if ups > 0:
		c.hp = max_hp(c)
		c.mp = max_mp(c)
	return ups

## 몬스터 레벨 차이에 따른 경험치 (너무 약한 적은 덜 줌)
static func exp_for(mon_id: String, lv: int) -> int:
	var m: Dictionary = DB.monsters[mon_id]
	var diff: int = lv - int(m.lv)
	var k := 1.0
	if diff > 4: k = maxf(0.1, 1.0 - (diff - 4) * 0.2)
	return maxi(1, int(round(m.exp * k)))

# ── 가방 ──
static func count(c: Dictionary, id: String) -> int:
	var n := 0
	for s in c.inv:
		if s.id == id: n += int(s.n)
	return n

static func stackable(id: String) -> bool:
	return DB.items[id].type in ["use", "etc", "quest"]

## 넣기. 자리가 없으면 false
static func add_item(c: Dictionary, id: String, n := 1) -> bool:
	if stackable(id):
		for s in c.inv:
			if s.id == id:
				s.n += n
				return true
		if c.inv.size() >= INV_SIZE: return false
		c.inv.append({"id": id, "n": n})
		return true
	if c.inv.size() + n > INV_SIZE: return false
	for i in n:
		c.inv.append({"id": id, "n": 1})
	return true

static func remove_item(c: Dictionary, id: String, n := 1) -> bool:
	if count(c, id) < n: return false
	var left := n
	for i in range(c.inv.size() - 1, -1, -1):
		var s = c.inv[i]
		if s.id != id: continue
		var take := mini(left, int(s.n))
		s.n -= take
		left -= take
		if s.n <= 0: c.inv.remove_at(i)
		if left == 0: break
	return true

static func can_equip(c: Dictionary, id: String) -> String:
	var it: Dictionary = DB.items[id]
	if not it.type in ["weapon", "head", "body", "acc"]: return "입을 수 없는 물건입니다."
	if it.has("job") and it.job != c.job: return "%s만 쓸 수 있습니다." % DB.jobs[it.job].name
	if c.lv < int(it.get("lv", 1)): return "레벨 %d부터 쓸 수 있습니다." % int(it.lv)
	return ""

## 입기: 가방 칸 i의 물건을 입고, 입던 것은 가방으로
static func equip(c: Dictionary, i: int) -> String:
	var id: String = c.inv[i].id
	var why := can_equip(c, id)
	if why != "": return why
	var slot: String = DB.items[id].type
	var old = c.equip.get(slot, "")
	c.inv.remove_at(i)
	c.equip[slot] = id
	if old != null and old != "":
		add_item(c, old)
	c.hp = mini(c.hp, max_hp(c))
	c.mp = mini(c.mp, max_mp(c))
	return ""

static func unequip(c: Dictionary, slot: String) -> String:
	var old = c.equip.get(slot, "")
	if old == null or old == "": return ""
	if c.inv.size() >= INV_SIZE: return "가방이 가득 찼습니다."
	c.equip[slot] = ""
	add_item(c, old)
	c.hp = mini(c.hp, max_hp(c))
	return ""

static func use_item(c: Dictionary, i: int) -> String:
	var id: String = c.inv[i].id
	var it: Dictionary = DB.items[id]
	if it.type != "use": return "쓸 수 없는 물건입니다."
	c.hp = mini(max_hp(c), c.hp + int(it.get("hp", 0)))
	c.mp = mini(max_mp(c), c.mp + int(it.get("mp", 0)))
	remove_item(c, id, 1)
	return ""

static func buy(c: Dictionary, id: String, n := 1) -> String:
	var cost: int = int(DB.items[id].price) * n
	if c.gold < cost: return "돈이 모자랍니다."
	if not add_item(c, id, n): return "가방이 가득 찼습니다."
	c.gold -= cost
	return ""

static func sell_price(id: String) -> int:
	return int(DB.items[id].price) / 2 if DB.items[id].type != "quest" else 0

static func sell(c: Dictionary, i: int) -> String:
	var id: String = c.inv[i].id
	if DB.items[id].type == "quest": return "퀘스트 물건은 팔 수 없습니다."
	c.gold += sell_price(id)
	remove_item(c, id, 1)
	return ""

# ── 기술 ──
static func skills_of(c: Dictionary) -> Array:
	var out := []
	for sid in DB.skills:
		var s: Dictionary = DB.skills[sid]
		if s.job == c.job and c.lv >= int(s.lv): out.append(sid)
	return out

# ── 퀘스트 ──  c.quests[id] = {"state": "active"|"done", "kills": {mon: n}}
static func quest_state(c: Dictionary, id: String) -> String:
	return c.quests[id].state if c.quests.has(id) else ""

static func can_offer(c: Dictionary, q: Dictionary) -> bool:
	if c.quests.has(q.id): return false
	if q.has("after") and quest_state(c, q.after) != "done": return false
	return c.lv >= int(q.get("lv", 1))

static func accept(c: Dictionary, q: Dictionary) -> void:
	c.quests[q.id] = {"state": "active", "kills": {}}

static func on_kill(c: Dictionary, mon_id: String) -> Array:
	var touched := []
	for id in c.quests:
		var st: Dictionary = c.quests[id]
		if st.state != "active": continue
		var q := DB.quest(id)
		var need: Dictionary = q.goal.get("kill", {})
		if need.has(mon_id):
			st.kills[mon_id] = mini(int(need[mon_id]), int(st.kills.get(mon_id, 0)) + 1)
			touched.append(id)
	return touched

static func goal_met(c: Dictionary, id: String) -> bool:
	var st: Dictionary = c.quests.get(id, {})
	if st.is_empty() or st.state != "active": return false
	var g: Dictionary = DB.quest(id).goal
	for m in g.get("kill", {}):
		if int(st.kills.get(m, 0)) < int(g.kill[m]): return false
	for it in g.get("item", {}):
		if count(c, it) < int(g.item[it]): return false
	if g.get("job", false) and c.job == "none": return false
	if g.has("talk") and not st.get("talked", false): return false
	return true

## 퀘스트 물건이 떨어질 때: 그 퀘스트가 진행 중이고 아직 덜 모았을 때만
static func quest_drop_ok(c: Dictionary, qid: String, item: String) -> bool:
	if quest_state(c, qid) != "active": return false
	var need := int(DB.quest(qid).goal.get("item", {}).get(item, 0))
	return count(c, item) < need

static func complete(c: Dictionary, id: String) -> Dictionary:
	var q := DB.quest(id)
	for it in q.goal.get("item", {}):
		remove_item(c, it, int(q.goal.item[it]))
	c.quests[id].state = "done"
	var r: Dictionary = q.reward
	var ups := gain_exp(c, int(r.get("exp", 0)))
	c.gold += int(r.get("gold", 0))
	for pair in r.get("items", []):
		add_item(c, pair[0], int(pair[1]))
	return {"ups": ups}

static func progress_text(c: Dictionary, id: String) -> String:
	var q := DB.quest(id)
	var st: Dictionary = c.quests.get(id, {"kills": {}})
	var parts := []
	for m in q.goal.get("kill", {}):
		parts.append("%s %d/%d" % [DB.monsters[m].name, int(st.kills.get(m, 0)), int(q.goal.kill[m])])
	for it in q.goal.get("item", {}):
		parts.append("%s %d/%d" % [DB.items[it].name, mini(count(c, it), int(q.goal.item[it])), int(q.goal.item[it])])
	if q.goal.get("job", false): parts.append("직업 얻기" + (" ✔" if c.job != "none" else ""))
	if q.goal.has("talk"): parts.append("%s 찾기" % DB.npcs[q.goal.talk].name)
	return ", ".join(parts)

static func new_character(name: String, g: String, hair: String, hc: String) -> Dictionary:
	var c := {"name": name, "g": g, "hair": hair, "hc": hc, "job": "none", "lv": 1, "exp": 0, "hp": 0, "mp": 0, "gold": 30,
		"inv": [{"id": "riceball", "n": 5}], "equip": {"weapon": "club0", "head": "", "body": "", "acc": ""},
		"quests": {}, "flags": {}, "buffs": {}, "map": "town", "x": -1, "y": -1, "hot": ["", "", "", "", "", "riceball", "tea", "pill"]}
	c.hp = max_hp(c)
	c.mp = max_mp(c)
	return c

static func set_job(c: Dictionary, j: String) -> void:
	c.job = j
	var w: String = {"warrior": "sword1", "rogue": "dagger1", "mage": "staff1", "priest": "bell1"}[j]
	var old = c.equip.weapon
	c.equip.weapon = w
	if old != "" and old != null: add_item(c, old)
	c.hp = max_hp(c)
	c.mp = max_mp(c)
