class_name UI
extends RefCounted
## 화면 글자·창 꾸미기 도우미 (나무 테 + 어두운 바탕의 옛 온라인 게임 창)

const INK := Color("2b1e2f")
const PAPER := Color("efe3c6")
const GOLD := Color("f6cf57")
const DIM := Color(0.7, 0.66, 0.58)

static func label(text: String, size := 12, col := PAPER, outline := true, small := false) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", Game.font_small if small else Game.font)
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", col)
	if outline:
		l.add_theme_color_override("font_outline_color", Color(0.06, 0.04, 0.08))
		l.add_theme_constant_override("outline_size", 3)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l

static func box() -> NinePatchRect:
	var n := NinePatchRect.new()
	n.texture = Fx.tex("ui_box")
	n.patch_margin_left = 6; n.patch_margin_right = 6; n.patch_margin_top = 6; n.patch_margin_bottom = 6
	n.mouse_filter = Control.MOUSE_FILTER_STOP
	return n

static func slot() -> NinePatchRect:
	var n := NinePatchRect.new()
	n.texture = Fx.tex("ui_slot")
	n.patch_margin_left = 3; n.patch_margin_right = 3; n.patch_margin_top = 3; n.patch_margin_bottom = 3
	return n

static func icon_of_item(id: String) -> Texture2D:
	return Fx.tex("icon_" + id)
