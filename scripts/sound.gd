extends Node
## 효과음·배경음 (자동 로드: Sound). 소리는 tools/sound/gen.py 가 코드로 만든 것.

const SFX := ["swing", "hit", "enemy_die", "coin", "hurt", "roll", "talk", "chest", "shard", "roar", "stomp",
	"warp", "select", "heal", "cut", "fire", "hop"]
var streams := {}
var pool: Array[AudioStreamPlayer] = []
var music_player: AudioStreamPlayer
var current := ""
var muted := false

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for n in SFX:
		streams[n] = load("res://assets/sfx/%s.wav" % n)
	for i in 10:
		var p := AudioStreamPlayer.new()
		add_child(p)
		pool.append(p)
	music_player = AudioStreamPlayer.new()
	music_player.volume_db = -8
	add_child(music_player)

func play(n: String, pitch_var := 0.08, vol := 0.0) -> void:
	if muted or not streams.has(n):
		return
	for p in pool:
		if not p.playing:
			p.stream = streams[n]
			p.pitch_scale = 1.0 + randf_range(-pitch_var, pitch_var)
			p.volume_db = vol
			p.play()
			return

func music(n: String, loop := true) -> void:
	if n == current:
		return
	current = n
	var s: AudioStreamWAV = load("res://assets/music/%s.wav" % n)
	if loop:
		s.loop_mode = AudioStreamWAV.LOOP_FORWARD
		s.loop_begin = 0
		s.loop_end = int(s.get_length() * s.mix_rate)
	var tw := create_tween()
	if music_player.playing:
		tw.tween_property(music_player, "volume_db", -40.0, 0.4)
	tw.tween_callback(func():
		music_player.stream = s
		music_player.volume_db = -8
		if not muted: music_player.play())

func stop_music() -> void:
	current = ""
	music_player.stop()

func toggle_mute() -> void:
	muted = not muted
	music_player.stream_paused = muted
