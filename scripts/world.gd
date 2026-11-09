extends Node2D
## data/maps.json 의 지도 하나를 짓는다. 칸 단위로 막힘·자리 차지를 관리한다.

const T := 32
const OBJ := {
	"T": "tree_round", "t": "tree_round2", "M": "tree_maple", "N": "tree_pine", "K": "tree_dark",
	"r": "rock", "R": "rock_big", "b": "bush", "B": "bush_berry", "f": "fence_h", "F": "fence_post",
	"l": "lantern", "j": "jar", "J": "jar_red", "c": "crate", "H": "wall", "X": "cave_rock", "k": "palisade", "C": "crop",
}
const PASSABLE := "C "

static var _tilesets := {}
static var _light: Texture2D

var key := ""
var data := {}
var W := 0
var H := 0
var blocked := {}
var occ := {}            # 칸 → 움직이는 것
var portals := {}        # 칸 → 출구 정보
var ysort: Node2D
var player: Node2D
var spawners: Array = []

static func tileset(th: String) -> TileSet:
	if _tilesets.has(th): return _tilesets[th]
	var ts := TileSet.new()
	ts.tile_size = Vector2i(T, T)
	var src := TileSetAtlasSource.new()
	src.texture = Fx.tex("tiles" if th == "" else "tiles_" + th)
	src.texture_region_size = Vector2i(T, T)
	for x in 8:
		src.create_tile(Vector2i(x, 0)); src.create_tile(Vector2i(x, 1))
	for m in range(1, 16):
		src.create_tile(Vector2i(m, 2)); src.create_tile(Vector2i(m, 6))
		var w := Vector2i(m, 3)
		src.create_tile(w)
		src.set_tile_animation_columns(w, 1)
		src.set_tile_animation_frames_count(w, 3)
		for f in 3: src.set_tile_animation_frame_duration(w, f, 0.35)
	ts.add_source(src, 0)
	_tilesets[th] = ts
	return ts

static func light_tex() -> Texture2D:
	if _light: return _light
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 1)); g.set_color(1, Color(1, 1, 1, 0))
	var t := GradientTexture2D.new()
	t.gradient = g; t.fill = GradientTexture2D.FILL_RADIAL
	t.fill_from = Vector2(0.5, 0.5); t.fill_to = Vector2(1, 0.5)
	t.width = 256; t.height = 256
	_light = t
	return t

static func cell_of(c: String, rows: Array, x: int, y: int) -> String:
	y = clampi(y, 0, rows.size() - 1)
	var r: String = rows[y]
	return r[clampi(x, 0, r.length() - 1)]

static func dual(rows: Array, x: int, y: int, ch: String) -> int:
	var m := 0
	if cell_of(ch, rows, x - 1, y - 1) == ch: m |= 8
	if cell_of(ch, rows, x, y - 1) == ch: m |= 4
	if cell_of(ch, rows, x - 1, y) == ch: m |= 2
	if cell_of(ch, rows, x, y) == ch: m |= 1
	return m

func build(map_key: String) -> void:
	key = map_key
	data = DB.maps[map_key]
	W = data.w; H = data.h
	var th: String = data.get("theme", "")
	var ground: Array = data.ground
	var objs: Array = data.objects
	var base := _layer(th, Vector2.ZERO, -30)
	var decal := _layer(th, Vector2.ZERO, -29)
	var water := _layer(th, Vector2(-16, -16), -28)
	var path := _layer(th, Vector2(-16, -16), -27)
	var plaza := _layer(th, Vector2(-16, -16), -26)
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(map_key)
	var wet := []
	for r in ground: wet.append((r as String).replace("D", "W"))
	for y in H:
		for x in W:
			base.set_cell(Vector2i(x, y), 0, Vector2i(rng.randi_range(0, 7), 0))
			if cell_of("", ground, x, y) == "." and cell_of("", objs, x, y) == " " and rng.randf() < 0.12:
				decal.set_cell(Vector2i(x, y), 0, Vector2i(rng.randi_range(0, 7), 1))
	for y in H + 1:
		for x in W + 1:
			var c := Vector2i(x, y)
			var m := dual(ground, x, y, "P"); if m: path.set_cell(c, 0, Vector2i(m, 2))
			m = dual(wet, x, y, "W"); if m: water.set_cell(c, 0, Vector2i(m, 3))
			m = dual(ground, x, y, "S"); if m: plaza.set_cell(c, 0, Vector2i(m, 6))
	for y in H:
		for x in W:
			if cell_of("", ground, x, y) == "W": blocked[Vector2i(x, y)] = true
			if cell_of("", ground, x, y) == "D":
				var b := Sprite2D.new()
				b.texture = Fx.tex("bridge")
				b.centered = false
				b.position = Vector2(x * T, y * T)
				b.z_index = -25
				add_child(b)
	ysort = Node2D.new()
	ysort.y_sort_enabled = true
	add_child(ysort)
	for y in H:
		for x in W:
			var o := cell_of("", objs, x, y)
			if o == " ": continue
			if not PASSABLE.contains(o): blocked[Vector2i(x, y)] = true
			_object(o, x, y, rng)
	for e in data.entities:
		_entity(e)
	var cm := CanvasModulate.new()
	var tint: Array = data.tint
	cm.color = Color(tint[0], tint[1], tint[2])
	add_child(cm)

func _layer(th: String, off: Vector2, z: int) -> TileMapLayer:
	var l := TileMapLayer.new()
	l.tile_set = tileset(th)
	l.position = off
	l.z_index = z
	add_child(l)
	return l

func feet(x: int, y: int) -> Vector2:
	return Vector2(x * T + T / 2.0, y * T + T - 2)

func _sprite(tex: Texture2D, pos: Vector2, bottom := 2.0, flip := false) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = tex
	s.offset = Vector2(0, -tex.get_height() / 2.0 + bottom)
	s.position = pos
	s.flip_h = flip
	ysort.add_child(s)
	return s

func _object(o: String, x: int, y: int, rng: RandomNumberGenerator) -> void:
	var n: String = OBJ.get(o, "")
	if n == "": return
	if o == "X": n = "cave_rock%d" % rng.randi_range(0, 2)
	var tex := Fx.tex(n)
	var p := feet(x, y)
	if o == "C" or o == "H" or o == "k":
		var s := _sprite(tex, p, 2)
		if o == "C": s.z_index = -20
		return
	var s := _sprite(tex, p + Vector2(rng.randi_range(-3, 3) if o in "TtMNK" else 0, 0), 4 if o in "TtMNK" else 2, o in "TtMNK" and rng.randf() < 0.5)
	if o == "l":
		_light_at(s, Vector2(0, -36), Color(1, 0.78, 0.45), 0.7, 0.9)

func _light_at(parent: Node2D, off: Vector2, col: Color, energy: float, scale: float) -> PointLight2D:
	var lt := PointLight2D.new()
	lt.texture = light_tex()
	lt.color = col
	lt.energy = energy
	lt.texture_scale = scale
	lt.position = off
	parent.add_child(lt)
	return lt

func _footprint(x: int, y: int, fw: int, fh: int) -> void:
	for yy in range(y - fh + 1, y + 1):
		for xx in range(x, x + fw):
			blocked[Vector2i(xx, yy)] = true

func _entity(e: Dictionary) -> void:
	var x: int = e.get("x", 0)
	var y: int = e.get("y", 0)
	match e.type:
		"house", "stall", "tent":
			var fw: int = e.fw
			var fh: int = e.fh
			var s := _sprite(Fx.tex(e.get("sprite", e.type)), Vector2(x * T + fw * T / 2.0, (y + 1) * T), 4)
			_footprint(x, y, fw, fh)
			if e.type == "house" and key == "town":
				_light_at(s, Vector2(0, -40), Color(1, 0.8, 0.5), 0.45, 1.2)
				_sign_at(Vector2i(x + fw / 2, y + 1), [["", "%s — 안에는 아직 들어갈 수 없다." % e.name]], false)
		"gate":
			var horizontal: bool = e.face == "south"
			var s := _sprite(Fx.tex("gate"), Vector2(x * T + (2 * T if horizontal else T), (y + 1) * T + (0 if horizontal else 0)), 4)
			if not horizontal:
				s.rotation = 0
				s.position = Vector2((x + 1) * T, (y + 1) * T - 8)
				s.scale = Vector2(0.75, 0.75)
				s.visible = false   # 동문은 성벽 틈으로만 (지도 끝)
		"well":
			_sprite(Fx.tex("well"), Vector2(x * T + T, (y + 1) * T), 4)
			_footprint(x, y, 2, 2)
		"campfire":
			var s := _sprite(Fx.tex("campfire"), feet(x, y), 2)
			s.hframes = 4
			var tw := s.create_tween().set_loops()
			tw.tween_method(func(v): s.frame = int(v) % 4, 0.0, 4.0, 0.5)
			_light_at(s, Vector2(0, -12), Color(1, 0.6, 0.3), 0.45, 1.1)
			blocked[Vector2i(x, y)] = true
		"torch":
			var s := _sprite(Fx.tex("torch"), feet(x, y), 2)
			s.hframes = 3
			var tw := s.create_tween().set_loops()
			tw.tween_method(func(v): s.frame = int(v) % 3, 0.0, 3.0, 0.4)
			_light_at(s, Vector2(0, -30), Color(1, 0.65, 0.35), 1.1, 1.3)
			blocked[Vector2i(x, y)] = true
		"sign":
			_sprite(Fx.tex("sign"), feet(x, y), 2)
			_sign_at(Vector2i(x, y), [["표지판", e.text]], true)
		"portal":
			for yy in range(y, y + int(e.get("h", 1))):
				for xx in range(x, x + int(e.get("w", 1))):
					portals[Vector2i(xx, yy)] = e
			if e.has("kind"):
				var s := _sprite(Fx.tex("cave_rock0"), feet(x, y + 1), 2)
				s.modulate = Color(0.3, 0.3, 0.35)
				s.scale = Vector2(0.8, 0.6)
		"npc":
			var n := preload("res://scripts/npc.gd").new()
			n.npc_id = e.id
			n.world = self
			ysort.add_child(n)
			n.place(Vector2i(x, y))
			occ[n.cell] = n
		"spawn":
			var sp := preload("res://scripts/spawner.gd").new()
			sp.world = self
			sp.mon = e.mon
			sp.area = Rect2i(e.area[0], e.area[1], e.area[2] - e.area[0], e.area[3] - e.area[1])
			sp.count = e.n
			add_child(sp)
			spawners.append(sp)
		"boss":
			var sp := preload("res://scripts/spawner.gd").new()
			sp.world = self
			sp.mon = e.mon
			sp.area = Rect2i(x - 1, y - 1, 3, 3)
			sp.count = 1
			sp.respawn = 90.0
			add_child(sp)
			spawners.append(sp)

var signs := {}
func _sign_at(c: Vector2i, lines: Array, solid: bool) -> void:
	signs[c] = lines
	if solid: blocked[c] = true

func is_free(c: Vector2i, who: Node = null) -> bool:
	if c.x < 0 or c.y < 0 or c.x >= W or c.y >= H: return false
	if blocked.has(c): return false
	var o = occ.get(c)
	return o == null or o == who or not is_instance_valid(o)

func walkable(c: Vector2i) -> bool:
	return c.x >= 0 and c.y >= 0 and c.x < W and c.y < H and not blocked.has(c)

func move_actor(a: Node, from: Vector2i, to: Vector2i) -> void:
	if occ.get(from) == a: occ.erase(from)
	occ[to] = a

func release(a: Node) -> void:
	if occ.get(a.cell) == a: occ.erase(a.cell)

func actor_at(c: Vector2i) -> Node:
	var o = occ.get(c)
	return o if o != null and is_instance_valid(o) else null

func spawn_player(c: Vector2i) -> Node2D:
	player = preload("res://scripts/player.gd").new()
	player.world = self
	ysort.add_child(player)
	if not is_free(c):
		c = nearest_free(c)
	player.place(c)
	occ[c] = player
	var cam := Camera2D.new()
	cam.limit_left = 0; cam.limit_top = 0
	cam.limit_right = W * T; cam.limit_bottom = H * T + 80
	cam.offset = Vector2(0, 30)
	cam.position_smoothing_enabled = true
	cam.position_smoothing_speed = 9.0
	player.add_child(cam)
	player.cam = cam
	if data.get("dark", false):
		_light_at(player, Vector2(0, -20), Color(1, 0.9, 0.75), 0.9, 1.6)
	return player

func nearest_free(c: Vector2i) -> Vector2i:
	for r in range(1, 12):
		for dy in range(-r, r + 1):
			for dx in range(-r, r + 1):
				var n := c + Vector2i(dx, dy)
				if is_free(n): return n
	return c

func entry_for(from_key: String) -> Vector2i:
	for e in data.entities:
		if e.type == "start": return Vector2i(e.x, e.y)
	return Vector2i(W / 2, H / 2)
