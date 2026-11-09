class_name Doll
extends RefCounted
## 몸·옷·머리 층을 겹쳐 한 장으로 (캐시). 칸 32×48, 7칸 × 3줄.

const FW := 32
const FH := 48
static var _cache := {}

static func _img(n: String) -> Image:
	var t: Texture2D = load("res://assets/sprites/%s.png" % n)
	var im := t.get_image()
	if im.is_compressed(): im.decompress()
	im.convert(Image.FORMAT_RGBA8)
	return im

## look = {g, hair, hc, outfit}
static func texture(look: Dictionary) -> Texture2D:
	var key := "%s_%s_%s_%s" % [look.get("g", "m"), look.get("hair", "short"), look.get("hc", "black"), look.get("outfit", "commoner")]
	if _cache.has(key): return _cache[key]
	var base := _img("body_" + look.get("g", "m"))
	for n in ["cloth_%s_%s" % [look.get("outfit", "commoner"), look.get("g", "m")], "hair_%s_%s" % [look.get("hair", "short"), look.get("hc", "black")]]:
		var layer := _img(n)
		base.blend_rect(layer, Rect2i(Vector2i.ZERO, layer.get_size()), Vector2i.ZERO)
	var tex := ImageTexture.create_from_image(base)
	_cache[key] = tex
	return tex

static func row_of(dir: Vector2i) -> int:
	if dir.y < 0: return 1
	if dir.x != 0: return 2
	return 0
