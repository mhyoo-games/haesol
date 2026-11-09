"""짐승 몬스터 (32칸 기준, 오른쪽을 봄). 칸: 0 서기 1 걷기 2 공격 3 맞음"""
import math
from common import *
from objects import shade_blob

def _legs(b, xs, top, bot, f, cols, step=2):
    for i, lx in enumerate(xs):
        off = (step if (i + f) % 2 else -step) if f == 1 else 0
        for y in range(top, bot):
            for x in range(lx + off * (y - top) // max(1, bot - top), lx + off * (y - top) // max(1, bot - top) + 3):
                put(b, x, y, cols[i % 2])

def _eye(b, x, y, big=False):
    put(b, x, y, 'ink'); put(b, x, y + 1, 'ink'); put(b, x - 1, y, 'wht') if big else None
    if big: put(b, x + 1, y, 'ink'); put(b, x + 1, y + 1, 'ink')

def _shadow(im, cx, w, y):
    for x in range(int(cx - w), int(cx + w)):
        for dy in range(2): put(im, x, y + dy, 'shadow')

def rabbit(f, pal=('s2', 's3', 's4', 'wht')):
    W, H = 32, 32; im = img(W, H); _shadow(im, 16, 9, 29)
    hop = -3 if f == 1 else (-1 if f == 2 else 0)
    b = shade_blob(W, H, [(15, 22 + hop, 7), (21, 17 + hop, 5)], list(pal), 3)
    for k in range(7):  # 귀
        put(b, 19 + k // 4, 11 + hop - k, pal[2]); put(b, 20 + k // 4, 11 + hop - k, pal[1]); put(b, 22 + k // 3, 12 + hop - k, pal[1])
    put(b, 20, 6 + hop, 'pk2'); put(b, 23, 8 + hop, 'pk2')
    _eye(b, 23, 16 + hop); put(b, 26, 19 + hop, 'pk1')
    _disc_tail(b, 8, 21 + hop, 'wht')
    for x in (13, 18): 
        for y in range(27 + (hop if f != 1 else 0), 29): put(b, x, y, pal[1]); put(b, x + 1, y, pal[1])
    if f == 3: _flash(b)
    im.alpha_composite(outline(b)); return im

def _disc_tail(b, x, y, c):
    for dx in range(-2, 2):
        for dy in range(-2, 2):
            if dx * dx + dy * dy < 4: put(b, x + dx, y + dy, c)

def _flash(b):
    px = b.load()
    for y in range(b.height):
        for x in range(b.width):
            if px[x, y][3]: px[x, y] = PAL['wht']

def squirrel(f):
    W, H = 32, 32; im = img(W, H); _shadow(im, 15, 8, 29)
    bob = -1 if f == 1 else 0
    tail = shade_blob(W, H, [(9, 15 + bob, 5), (7, 10 + bob, 4), (10, 20, 4)], ['b0', 'b1', 'b2', 'b3'], 2)
    b = img(W, H); b.alpha_composite(tail)
    body = shade_blob(W, H, [(16, 21 + bob, 5.5), (21, 16 + bob, 4.5)], ['b1', 'b2', 'b3', 'b4'], 5)
    b.alpha_composite(body)
    put(b, 21, 11 + bob, 'b1'); put(b, 22, 10 + bob, 'b1'); put(b, 23, 11 + bob, 'b2')
    _eye(b, 23, 15 + bob); put(b, 25, 17 + bob, 'ink')
    for y in range(19 + bob, 24 + bob): put(b, 18, y, 'p3'); put(b, 19, y, 'p3')
    _legs(b, [13, 18], 25, 29, f, ['b1', 'b0'], 1)
    if f == 2:
        put(b, 25, 20, 'b2'); put(b, 26, 20, 'b2')
    if f == 3: _flash(b)
    im.alpha_composite(outline(b)); return im

def canine(f, pal, ears='point', tailc=None, size=1.0, mark=None):
    """들개·불여우·너구리 공용 몸."""
    W, H = 32, 32; im = img(W, H); _shadow(im, 16, 11, 29)
    s = size; bob = -1 if f == 1 else 0; lunge = 3 if f == 2 else 0
    b = img(W, H)
    _legs(b, [9, 13, 19, 23], 22, 29, f, [pal[0], pal[1]], 2)
    tail = tailc or pal[1]
    for k in range(8): put(b, 6 - k // 2, 18 + bob - k // 3, tail); put(b, 7 - k // 2, 19 + bob - k // 3, tail)
    body = shade_blob(W, H, [(14, 19 + bob, 7.5), (20, 19 + bob, 6.5)], list(pal), 6)
    b.alpha_composite(body)
    head = shade_blob(W, H, [(24 + lunge, 14 + bob, 5), (28 + lunge, 16 + bob, 3)], list(pal[1:]) + [pal[-1]], 9)
    b.alpha_composite(head)
    if ears == 'point':
        for k in range(4): put(b, 22 + lunge, 9 + bob - k, pal[1]); put(b, 23 + lunge, 9 + bob - k + 1, pal[2]); put(b, 25 + lunge, 9 + bob - k + 1, pal[1])
    else:
        put(b, 21 + lunge, 9 + bob, pal[0]); put(b, 22 + lunge, 9 + bob, pal[0]); put(b, 26 + lunge, 9 + bob, pal[0])
    _eye(b, 25 + lunge, 13 + bob); put(b, 31 if lunge else 30, 16 + bob, 'ink')
    if f == 2:
        for x in range(27 + lunge, 31): put(b, x, 18 + bob, 'red1')
        put(b, 28 + lunge, 17 + bob, 'wht'); put(b, 30, 17 + bob, 'wht')
    if mark == 'mask':  # 너구리 눈가 무늬
        for x in range(23, 28): put(b, x, 13 + bob, 'ink2')
        _eye(b, 25, 13 + bob)
        for k in range(0, 8, 2): put(b, 5 - k // 2, 17 + bob - k // 3, 'ink2')
    if mark == 'fire':  # 불여우 꼬리 끝 불꽃
        for (x, y, c) in ((2, 13, 'y1'), (3, 12, 'or2'), (1, 12, 'or1'), (2, 11, 'y2')): put(b, x, y + bob, c)
    if mark == 'cloth':  # 들개 목의 검은 천
        for y in range(15 + bob, 20 + bob): put(b, 20, y, 'ink'); put(b, 21, y, 'r0')
    if f == 3: _flash(b)
    im.alpha_composite(outline(b)); return im

def rat(f, big=False):
    W, H = (64, 56) if big else (32, 32)
    im = img(W, H); s = 2 if big else 1
    _shadow(im, W / 2, 11 * s, H - 3)
    bob = -s if f == 1 else 0; lunge = 3 * s if f == 2 else 0
    b = img(W, H)
    pal = ['s0', 's1', 's2', 's3'] if not big else ['ink2', 's0', 's1', 's2']
    for k in range(12 * s): put(b, 6 * s - k // 2, int(H * 0.7) + k // 4 - k // 8, 'pk1')
    body = shade_blob(W, H, [(14 * s, H * 0.64 + bob, 7.5 * s), (20 * s, H * 0.66 + bob, 6 * s)], pal, 4)
    b.alpha_composite(body)
    head = shade_blob(W, H, [(24 * s + lunge, H * 0.6 + bob, 4.5 * s), (28 * s + lunge, H * 0.66 + bob, 2.5 * s)], pal[1:] + [pal[-1]], 7)
    b.alpha_composite(head)
    ex, ey = int(25 * s + lunge), int(H * 0.56 + bob)
    _disc_tail(b, int(22 * s + lunge), int(H * 0.46 + bob), 'pk1')
    put(b, ex, ey, 'red2'); put(b, ex, ey + 1, 'red0')
    if big:
        put(b, ex + 1, ey, 'red2'); put(b, ex + 1, ey + 1, 'red0')
        for k in range(4): put(b, 30 * s + lunge - k, int(H * 0.72) + bob, 'wht')
        for x in range(10 * s, 22 * s, 4):
            for k in range(4): put(b, x + k // 2, int(H * 0.42) + bob - k, 's3')  # 등 가시털
        for (x, y) in ((22, 14), (24, 13), (26, 14)): put(b, x * s, y * s // 2 + 2 + bob, 'y1')  # 왕관 무늬
    put(b, int(31 * s + lunge - 1), int(H * 0.66 + bob), 'pk2')
    _legs(b, [10 * s, 20 * s], int(H * 0.8), H - 3, f, [pal[0], pal[1]], s)
    if f == 3: _flash(b)
    im.alpha_composite(outline(b)); return im

def bat(f):
    W, H = 32, 32; im = img(W, H); _shadow(im, 16, 5, 29)
    up = [0, -4, 2, 0][f]; fl = [-2, 2, 0, 0][f]
    b = img(W, H)
    for side in (-1, 1):
        for k in range(12):
            y = 14 + fl * side * 0 + (k * k) // 24 + (up if k > 4 else 0) - (fl if k > 8 else 0)
            for t in range(3 + (k % 4 == 0)):
                put(b, 16 + side * (3 + k), y + t, 'v1' if t else 'v0')
    body = shade_blob(W, H, [(16, 15, 4.5)], ['v0', 'v1', 'v2'], 3)
    b.alpha_composite(body)
    put(b, 14, 10, 'v1'); put(b, 18, 10, 'v1'); put(b, 13, 9, 'v1'); put(b, 19, 9, 'v1')
    put(b, 14, 14, 'y1'); put(b, 18, 14, 'y1'); put(b, 15, 17, 'wht'); put(b, 17, 17, 'wht')
    if f == 3: _flash(b)
    im.alpha_composite(outline(b)); return im

def strip(frames):
    w = max(x.width for x in frames); h = max(x.height for x in frames)
    s = img(w * len(frames), h)
    for i, fr in enumerate(frames): s.alpha_composite(fr, (i * w + (w - fr.width) // 2, h - fr.height))
    return s

def build():
    out = {
        'mon_rabbit': strip([rabbit(i) for i in range(4)]),
        'mon_squirrel': strip([squirrel(i) for i in range(4)]),
        'mon_dog': strip([canine(i, ['b0', 'b1', 'b2', 'b3'], mark='cloth') for i in range(4)]),
        'mon_raccoon': strip([canine(i, ['s0', 's1', 'b2', 'b3'], ears='round', mark='mask') for i in range(4)]),
        'mon_fox': strip([canine(i, ['red0', 'or1', 'or2', 'y1'], tailc='or1', mark='fire') for i in range(4)]),
        'mon_rat': strip([rat(i) for i in range(4)]),
        'mon_ratking': strip([rat(i, True) for i in range(4)]),
        'mon_bat': strip([bat(i) for i in range(4)]),
    }
    return out
