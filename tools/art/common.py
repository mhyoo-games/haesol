"""해솔국 이야기 도트 그림 공용 도구.

그림은 전부 코드로 만든다: 팔레트 + 글자 그림(ASCII) + 절차적 타일.
`python3 tools/art/gen.py` 로 assets/sprites/*.png 를 다시 만든다.
"""
from PIL import Image
import random, math

def hx(s, a=255):
    s = s.lstrip('#')
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)

# 따뜻한 저녁빛 팔레트 (직접 고른 색)
PAL = {
    'ink': hx('2b1e2f'), 'ink2': hx('45304a'),
    # 풀
    'g0': hx('223322'), 'g1': hx('2e4a2b'), 'g2': hx('3e6133'), 'g3': hx('557a3f'), 'g4': hx('77964f'), 'g5': hx('a3b56c'),
    # 흙길
    'd0': hx('4f3a2c'), 'd1': hx('6e5236'), 'd2': hx('8f6c47'), 'd3': hx('ae8a5c'), 'd4': hx('cbaa78'),
    # 물
    'w0': hx('1b2d40'), 'w1': hx('23455a'), 'w2': hx('2d5f70'), 'w3': hx('4a878a'), 'w4': hx('8ebfae'), 'foam': hx('d9eadb'),
    # 나무·목재
    'b0': hx('3b2420'), 'b1': hx('5e3a2c'), 'b2': hx('8a5a3b'), 'b3': hx('b07f4f'), 'b4': hx('d6aa6e'),
    # 돌
    's0': hx('3d3b4f'), 's1': hx('5b5a70'), 's2': hx('80809a'), 's3': hx('a9abc0'), 's4': hx('d5d8e3'),
    # 기와·지붕
    'r0': hx('262a3f'), 'r1': hx('343a55'), 'r2': hx('47506f'), 'r3': hx('63708f'),
    # 벽(한지·흙벽)
    'p0': hx('a88a6a'), 'p1': hx('cfb48e'), 'p2': hx('ead6b0'), 'p3': hx('f8edd5'),
    # 빨강·주황·노랑
    'red0': hx('6e1f2c'), 'red1': hx('a8323a'), 'red2': hx('d8524a'), 'red3': hx('f08a6a'),
    'or1': hx('e0782f'), 'or2': hx('f3a64a'), 'y1': hx('f6cf57'), 'y2': hx('fff0a0'),
    # 보라·분홍
    'v0': hx('3a2552'), 'v1': hx('5c3b7d'), 'v2': hx('8a5cb0'), 'v3': hx('b98be0'),
    'pk1': hx('e8869a'), 'pk2': hx('f7b8c2'),
    # 남색 옷
    'n0': hx('1f2a4a'), 'n1': hx('2d4476'), 'n2': hx('3f63a3'), 'n3': hx('6b92cf'),
    # 피부·머리
    'sk0': hx('b9725a'), 'sk1': hx('e3a07c'), 'sk2': hx('f6c9a0'), 'sk3': hx('ffe2c4'),
    'hr0': hx('2a1a1c'), 'hr1': hx('46282a'), 'hr2': hx('6b3c34'),
    # 늪 (올리브 풀, 탁한 물)
    'o0': hx('263321'), 'o1': hx('384a2c'), 'o2': hx('4d6236'), 'o3': hx('6c7f42'), 'o4': hx('94a259'), 'o5': hx('bcc47a'),
    'm0': hx('1a302f'), 'm1': hx('264b47'), 'm2': hx('356a62'), 'm3': hx('5b968a'), 'm4': hx('a6d2bf'),
    'wht': hx('fbf7ee'), 'shadow': (20, 14, 30, 90),
    # 도깨비불
    'f0': hx('2c6f8f'), 'f1': hx('3fb7c9'), 'f2': hx('8ef0e4'), 'f3': hx('e6fff8'),
}

def img(w, h):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))

def put(im, x, y, c):
    if 0 <= x < im.width and 0 <= y < im.height and c is not None:
        if isinstance(c, str): c = PAL[c]
        if len(c) == 4 and c[3] < 255:
            base = im.getpixel((x, y))
            a = c[3] / 255
            if base[3] == 0:
                im.putpixel((x, y), c); return
            c = tuple(int(base[i] * (1 - a) + c[i] * a) for i in range(3)) + (255,)
        im.putpixel((x, y), c)

def ascii_sprite(rows, keys, mirror=False):
    """글자 그림 → 이미지. mirror=True면 왼쪽 반을 오른쪽에 거울처럼 붙인다."""
    if mirror:
        rows = [r + r[::-1] for r in rows]
    w = max(len(r) for r in rows); h = len(rows)
    im = img(w, h)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in ('.', ' '): continue
            put(im, x, y, keys[ch])
    return im

def outline(im, col='ink', diag=False):
    """투명 칸 중 그림과 맞닿은 곳에 테두리를 그린다."""
    out = im.copy()
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            if px[x, y][3]: continue
            nb = [(1,0),(-1,0),(0,1),(0,-1)] + ([(1,1),(-1,-1),(1,-1),(-1,1)] if diag else [])
            for dx, dy in nb:
                xx, yy = x+dx, y+dy
                if 0 <= xx < im.width and 0 <= yy < im.height and px[xx, yy][3] > 128:
                    put(out, x, y, col); break
    return out

def flip(im):
    return im.transpose(Image.FLIP_LEFT_RIGHT)

def sheet(frames, fw, fh, cols=None):
    cols = cols or len(frames)
    rows = (len(frames) + cols - 1) // cols
    s = img(fw * cols, fh * rows)
    for i, f in enumerate(frames):
        if f is None: continue
        s.alpha_composite(f, ((i % cols) * fw, (i // cols) * fh))
    return s

def pad(im, w, h, ox=None, oy=None):
    """w×h 칸 가운데-아래에 맞춰 놓는다."""
    c = img(w, h)
    ox = (w - im.width) // 2 if ox is None else ox
    oy = (h - im.height) if oy is None else oy
    c.alpha_composite(im, (ox, oy))
    return c

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
def dither(x, y, t):
    return t * 16 > BAYER[y % 4][x % 4] + 0.5

class Noise:
    def __init__(self, seed):
        r = random.Random(seed)
        self.g = [[r.random() for _ in range(64)] for _ in range(64)]
    def v(self, x, y, sc=4.0):
        x /= sc; y /= sc
        x0, y0 = int(math.floor(x)), int(math.floor(y))
        fx, fy = x - x0, y - y0
        fx = fx*fx*(3-2*fx); fy = fy*fy*(3-2*fy)
        g = self.g
        a = g[y0 % 64][x0 % 64]; b = g[y0 % 64][(x0+1) % 64]
        c = g[(y0+1) % 64][x0 % 64]; d = g[(y0+1) % 64][(x0+1) % 64]
        return (a*(1-fx)+b*fx)*(1-fy) + (c*(1-fx)+d*fx)*fy
