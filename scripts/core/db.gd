extends Node
## 데이터 묶음 (자동 로드: DB). data/game.json, data/story.json, data/maps.json

var jobs := {}
var skills := {}
var items := {}
var monsters := {}
var shops := {}
var npcs := {}
var quests := []
var maps := {}

func _ready() -> void:
	load_all()

func load_all() -> void:
	var g = JSON.parse_string(FileAccess.get_file_as_string("res://data/game.json"))
	var s = JSON.parse_string(FileAccess.get_file_as_string("res://data/story.json"))
	jobs = g.jobs; skills = g.skills; items = g.items; monsters = g.monsters; shops = g.shops
	npcs = s.npcs; quests = s.quests
	maps = JSON.parse_string(FileAccess.get_file_as_string("res://data/maps.json"))

func quest(id: String) -> Dictionary:
	for q in quests:
		if q.id == id: return q
	return {}
