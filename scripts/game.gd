extends Node
## 캐릭터 상태·저장·입력·글꼴 (자동 로드: Game). 규칙 계산은 core/rules.gd.

signal changed
signal log(text: String, col: Color)

const SAVE_PATH := "user://haesol_save.json"

var c := {}          # 캐릭터
var busy := false    # 대화·창이 열려 있으면 못 움직임
var font: Font
var font_small: Font
var font_bold: Font
var theme: Theme

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_setup_input()
	font = _pixel_font("res://assets/fonts/Galmuri11.ttf")
	font_small = _pixel_font("res://assets/fonts/Galmuri9.ttf")
	font_bold = _pixel_font("res://assets/fonts/Galmuri11-Bold.ttf")
	theme = Theme.new()
	theme.default_font = font
	theme.default_font_size = 12
	get_tree().root.theme = theme

func say(text: String, col := Color(0.92, 0.9, 0.82)) -> void:
	log.emit(text, col)

func touch() -> void:
	changed.emit()

func has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH)

func save() -> void:
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f: f.store_string(JSON.stringify(c))

func load_save() -> bool:
	if not has_save(): return false
	var d = JSON.parse_string(FileAccess.get_file_as_string(SAVE_PATH))
	if typeof(d) != TYPE_DICTIONARY or not d.has("lv"): return false
	c = d
	c.lv = int(c.lv); c.exp = int(c.exp); c.hp = int(c.hp); c.mp = int(c.mp); c.gold = int(c.gold)
	c.buffs = {}
	return true

func _key(action: String, keys: Array, pads: Array = []) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action, 0.3)
	for k in keys:
		var e := InputEventKey.new()
		e.physical_keycode = k
		InputMap.action_add_event(action, e)
	for b in pads:
		var j := InputEventJoypadButton.new()
		j.button_index = b
		InputMap.action_add_event(action, j)

func _setup_input() -> void:
	_key("left", [KEY_LEFT, KEY_A], [JOY_BUTTON_DPAD_LEFT])
	_key("right", [KEY_RIGHT, KEY_D], [JOY_BUTTON_DPAD_RIGHT])
	_key("up", [KEY_UP, KEY_W], [JOY_BUTTON_DPAD_UP])
	_key("down", [KEY_DOWN, KEY_S], [JOY_BUTTON_DPAD_DOWN])
	_key("attack", [KEY_SPACE, KEY_Z], [JOY_BUTTON_A])
	_key("talk", [KEY_ENTER, KEY_X, KEY_KP_ENTER], [JOY_BUTTON_B])
	_key("cancel", [KEY_ESCAPE], [JOY_BUTTON_START])
	_key("inv", [KEY_I], [])
	_key("status", [KEY_C], [])
	_key("skills", [KEY_K], [])
	_key("quests", [KEY_Q], [])
	_key("target", [KEY_TAB], [JOY_BUTTON_RIGHT_SHOULDER])
	for i in 8:
		_key("hot%d" % (i + 1), [KEY_1 + i], [])

func _pixel_font(path: String) -> Font:
	var f: FontFile = load(path)
	f.antialiasing = TextServer.FONT_ANTIALIASING_NONE
	f.hinting = TextServer.HINTING_NONE
	f.subpixel_positioning = TextServer.SUBPIXEL_POSITIONING_DISABLED
	f.generate_mipmaps = false
	return f
