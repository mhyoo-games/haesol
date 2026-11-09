extends Node
## 한 구역에 몬스터 수를 맞춰 두고, 잡히면 잠시 뒤 다시 나오게 한다.

var world: Node2D
var mon := ""
var area := Rect2i()
var count := 5
var respawn := 8.0
var alive := 0

func _ready() -> void:
	for i in count: _spawn()

func _spawn() -> void:
	for tries in 40:
		var c := Vector2i(randi_range(area.position.x, area.end.x), randi_range(area.position.y, area.end.y))
		if world.is_free(c) and (world.player == null or world.player.dist_to(c) > 4):
			var m := preload("res://scripts/monster.gd").new()
			m.mon = mon
			m.world = world
			world.ysort.add_child(m)
			m.place(c)
			m.home = c
			m.spawner = self
			world.occ[c] = m
			alive += 1
			m.died.connect(func():
				alive -= 1
				get_tree().create_timer(respawn).timeout.connect(func(): if is_inside_tree(): _spawn()))
			return
