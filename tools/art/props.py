"""32칸 세상의 소품·아이콘·효과: 성벽·성문·장터 가판·천막·목책·모닥불·횃불·밭·굴벽, 아이템·기술 아이콘."""
import math, random
from common import *
from objects import shade_blob
from doll import _line, _disc

def wall():
    """성벽 한 칸 (32×48: 위 16은 성가퀴)."""
    im = img(32, 48)
    for y in range(8, 48):
        for x in range(32):
            row = (y - 8) // 8; bx = (x + (8 if row % 2 else 0)) % 16
            c = 's2'
            if (y - 8) % 8 == 7 or bx == 15: c = 's0'
            elif (y - 8) % 8 == 0 or bx == 0: c = 's3'
            if y > 40: c = 's1' if c == 's2' else c
            put(im, x, y, c)
    for x in range(32):
        for y in range(0, 8):
            if (x // 8) % 2 == 0: put(im, x, y, 's3' if y < 2 else ('s2' if x % 8 < 6 else 's1'))
        put(im, x, 8, 'r1'); put(im, x, 9, 'r2')
    return outline(im)

def gate():
    """성문 (96×96): 기와지붕 문루 + 나무 문짝."""
    W, H = 96, 96; im = img(W, H)
    for y in range(40, 96):
        for x in range(8, 88):
            row = (y - 40) // 8; bx = (x + (8 if row % 2 else 0)) % 16
            c = 's2' if not ((y - 40) % 8 == 7 or bx == 15) else 's0'
            put(im, x, y, c)
    for y in range(52, 96):  # 문 구멍
        for x in range(32, 64):
            if ((x - 48) / 16) ** 2 + ((y - 64) / 14) ** 2 < 1 or y >= 64:
                put(im, x, y, 'ink2' if y < 70 else 'b0')
    for y in range(66, 96):
        for x in range(33, 63):
            c = 'b2' if (x - 33) % 6 else 'b1'
            if x in (47, 48): c = 'b0'
            put(im, x, y, c)
    for (x, y) in ((44, 80), (51, 80)): _disc(im, (x, y), 1.5, 'y1')
    # 문루 지붕
    for y in range(6, 42):
        t = (y - 6) / 36; half = 20 + 28 * min(1, t * 1.2)
        for x in range(W):
            dx = abs(x + 0.5 - 48); lift = (dx / 48) ** 4 * 6
            if dx <= half and 6 <= y - lift <= 34:
                c = 'r2' if ((x + (2 if (y // 3) % 2 else 0)) % 4) else 'r1'
                if (y - int(lift)) % 3 == 0: c = 'r1'
                if y - lift > 32: c = 'r0'
                put(im, x, y, c)
    for y in range(30, 42):
        for x in range(20, 76):
            put(im, x, y, 'red1' if (x // 8) % 2 else 'red0')
    for x in range(28, 68): put(im, x, 5, 'r3'); put(im, x, 6, 'r3')
    # 현판
    for y in range(32, 40):
        for x in range(40, 56): put(im, x, y, 'b1' if y in (32, 39) or x in (40, 55) else 'ink2')
    for x in (43, 45, 48, 50, 52): put(im, x, 35, 'y1'); put(im, x, 36, 'y1')
    return outline(im)

def stall(color='red'):
    """장터 가판 (64×56): 차양 + 물건."""
    W, H = 64, 56; im = img(W, H)
    for x in range(4, 60): put(im, x, 54, 'shadow'); put(im, x, 55, 'shadow')
    for y in range(36, 54):
        for x in range(6, 58): put(im, x, y, 'b2' if y > 38 else 'b3')
    for x in (8, 54):
        for y in range(10, 54): put(im, x, y, 'b1'); put(im, x + 1, y, 'b1')
    stripe = ('red1', 'p3') if color == 'red' else ('n2', 'p3')
    for y in range(6, 18):
        for x in range(2 + (17 - y) // 3, 62 - (17 - y) // 3):
            put(im, x, y, stripe[(x // 6) % 2])
        if y == 17:
            for x in range(4, 60, 6): put(im, x + 3, 18, stripe[0]); put(im, x + 2, 19, stripe[0])
    r = random.Random(7 if color == 'red' else 9)
    for i in range(7):
        x = 10 + i * 6; c = r.choice(['red2', 'y1', 'g3', 'or2', 'p2'])
        _disc(im, (x + 2, 34), 2.5, c)
    return outline(im)

def tent():
    W, H = 64, 56; im = img(W, H)
    for x in range(4, 60): put(im, x, 54, 'shadow')
    for y in range(8, 54):
        t = (y - 8) / 46; half = 4 + 26 * t
        for x in range(W):
            dx = x + 0.5 - 32
            if abs(dx) <= half:
                c = 'b2' if dx < 0 else 'b1'
                if abs(dx) < 6 * t and y > 30: c = 'ink2'
                if int(abs(dx)) % 9 == 0: c = 'b0'
                put(im, x, y, c)
    _line(im, (32, 2), (32, 10), 2, 'b0')
    for k in range(6): put(im, 33 + k, 3 + k // 3, 'ink'); put(im, 33 + k, 4 + k // 3, 'r0')
    return outline(im)

def palisade():
    im = img(32, 48)
    for i in range(4):
        x0 = 1 + i * 8
        for y in range(8, 46):
            for x in range(x0, x0 + 7): put(im, x, y, 'b2' if x < x0 + 3 else 'b1')
        for k in range(4): put(im, x0 + 3, 8 - k, 'b2'); put(im, x0 + 2 + (k > 1), 8 - k + 1, 'b2')
    for x in range(32): put(im, x, 20, 'b0'); put(im, x, 34, 'b0')
    return outline(im)

def campfire(f):
    im = img(32, 32)
    for (a, b) in (((8, 26), (24, 22)), ((8, 22), (24, 26))): _line(im, a, b, 3, 'b1')
    for i in range(5): _disc(im, (6 + i * 5, 27), 2, 's1')
    t = f * 1.7
    for y in range(8, 25):
        for x in range(32):
            u = (x + 0.5 - 16) / 6; v = (y - 24) / 15
            w = (1 + v) * (1 + 0.25 * math.sin(y * 0.8 + t))
            if abs(u - math.sin(y * 0.5 + t) * 0.2 * (-v)) < w * 0.9 and v > -1:
                d = abs(u) / max(0.1, w)
                put(im, x, y, 'y2' if d < 0.35 and y > 15 else ('y1' if d < 0.6 else ('or2' if d < 0.85 else 'red2')))
    return im

def torch(f):
    im = img(16, 40)
    for y in range(14, 40): put(im, 7, y, 'b1'); put(im, 8, y, 'b0')
    for x in range(5, 11): put(im, x, 14, 's2'); put(im, x, 15, 's1')
    t = f * 2
    for y in range(2, 14):
        for x in range(16):
            u = (x + 0.5 - 8) / 3.5; v = (y - 13) / 11
            if abs(u - 0.2 * math.sin(y + t)) < (1 + v) * 1.1 and v > -1:
                put(im, x, y, 'y2' if abs(u) < 0.4 and y > 7 else ('y1' if abs(u) < 0.8 else 'or1'))
    return outline(im)

def crop():
    im = img(32, 32)
    for y in range(18, 30):
        for x in range(2, 30): put(im, x, y, 'd1' if (y // 4) % 2 else 'd2')
    for x in range(5, 30, 6):
        for k in range(8): put(im, x + (k % 3 == 0), 22 - k, 'g3' if k > 3 else 'g2')
        put(im, x - 1, 15, 'g4'); put(im, x + 2, 16, 'g4'); put(im, x, 14, 'y1')
    return outline(im)

def cave_rock(seed):
    im = img(32, 48)
    b = shade_blob(32, 48, [(16, 30, 15), (10, 20, 9), (22, 18, 10), (16, 12, 8)], ['ink2', 's0', 's1', 's2'], seed)
    im.alpha_composite(outline(b)); return im

# ── 아이콘 (20×20) ──
def icon(kind):
    im = img(20, 20)
    if kind == 'riceball':
        for y in range(4, 17):
            for x in range(3, 17):
                if abs(x - 9.5) < (y - 3) * 0.6 + 1 and y < 17: put(im, x, y, 'wht' if (x + y) % 5 else 's4')
        for y in range(12, 17):
            for x in range(5, 15): put(im, x, y, 'ink2')
    elif kind == 'pill':
        _disc(im, (7, 11), 4, 'g2'); _disc(im, (13, 11), 4, 'g3'); put(im, 6, 9, 'g5'); put(im, 12, 9, 'g5')
    elif kind == 'tea':
        for y in range(6, 16):
            for x in range(4, 14): put(im, x, y, 'p2' if x < 12 else 'p1')
        for x in range(5, 13): put(im, x, 7, 'b2')
        _line(im, (14, 9), (16, 12), 2, 'p1')
    elif kind in ('sword', 'dagger'):
        ln = 14 if kind == 'sword' else 9
        _line(im, (4, 16), (4 + ln * 0.75, 16 - ln * 0.75), 2, 's3'); _line(im, (2, 15), (6, 19), 2, 'y1'); _line(im, (2, 18), (4, 16), 2, 'b1')
    elif kind == 'staff':
        _line(im, (4, 17), (14, 5), 2, 'b2'); _disc(im, (15, 4), 2.5, 'f2')
    elif kind == 'bell':
        _line(im, (4, 17), (12, 7), 2, 'b3'); _disc(im, (13, 5), 2, 'y1'); _disc(im, (16, 8), 2, 'y1')
    elif kind == 'club':
        _line(im, (4, 17), (13, 7), 3, 'b2'); _disc(im, (14, 6), 3, 'b2')
    elif kind == 'cap':
        for y in range(6, 14):
            for x in range(3, 17):
                if ((x - 10) / 7) ** 2 + ((y - 13) / 7) ** 2 < 1: put(im, x, y, 'b2')
        for x in range(3, 17): put(im, x, 13, 'b1')
    elif kind in ('vest', 'armor'):
        c = ('b2', 'b1') if kind == 'vest' else ('s2', 's1')
        for y in range(4, 17):
            for x in range(4, 16): put(im, x, y, c[0] if (x + y) % 3 else c[1])
        for y in range(4, 9): put(im, 9, y, 'ink2'); put(im, 10, y, 'ink2')
    elif kind == 'ring':
        _disc(im, (10, 11), 5, 'y1'); _disc(im, (10, 11), 3, (0, 0, 0, 0)) if False else None
        for y in range(8, 15):
            for x in range(7, 14):
                if ((x - 10) / 3) ** 2 + ((y - 11) / 3) ** 2 < 1: im.putpixel((x, y), (0, 0, 0, 0))
        _disc(im, (10, 5), 2, 'g4')
    elif kind == 'tail':
        for k in range(12): _disc(im, (5 + k, 15 - k * 0.8 + math.sin(k * 0.6) * 2), 2.2, 'b2' if k % 3 else 'b3')
    elif kind == 'pelt':
        for y in range(4, 17):
            for x in range(3, 17):
                if abs(x - 10) < 6 + math.sin(y) * 1.5: put(im, x, y, 'b1' if (x + y) % 4 else 'b2')
    elif kind == 'fang':
        for k in range(10): 
            for t in range(4 - k // 3): put(im, 8 + t, 4 + k, 'wht')
    elif kind == 'ratfur':
        for k in range(8): _line(im, (4 + k, 16), (6 + k, 5 + (k % 3)), 1, 's2')
    elif kind == 'blackcloth':
        for y in range(4, 16):
            for x in range(4, 16): put(im, x, y, 'ink' if (x * y) % 7 else 'r1')
        _line(im, (6, 12), (13, 7), 1, 's3')
    elif kind == 'map':
        for y in range(4, 16):
            for x in range(3, 17): put(im, x, y, 'p2')
        _line(im, (5, 13), (14, 7), 1, 'red1'); put(im, 14, 7, 'ink')
    elif kind == 'blackjade':
        _disc(im, (10, 10), 5, 'ink2'); put(im, 8, 8, 'v2'); put(im, 9, 7, 'v3')
    return outline(im)

ITEM_ICON = {'riceball': 'riceball', 'pill': 'pill', 'tea': 'tea', 'club0': 'club', 'sword1': 'sword', 'sword2': 'sword', 'dagger1': 'dagger', 'dagger2': 'dagger',
             'staff1': 'staff', 'staff2': 'staff', 'bell1': 'bell', 'bell2': 'bell', 'cap': 'cap', 'vest': 'vest', 'armor': 'armor', 'ring': 'ring',
             'tail': 'tail', 'pelt': 'pelt', 'fang': 'fang', 'ratfur': 'ratfur', 'blackcloth': 'blackcloth', 'map': 'map', 'blackjade': 'blackjade'}

def skill_icon(sid):
    im = img(20, 20)
    bg = {'whirl': 'red1', 'rush': 'red0', 'roar': 'or1', 'triple': 'r1', 'star': 'r2', 'shadow': 'v0', 'fire': 'red2', 'ice': 'n2', 'thunder': 'y1', 'heal': 'g3', 'orb': 'f1', 'guard': 'n3'}[sid]
    for y in range(1, 19):
        for x in range(1, 19): put(im, x, y, bg)
    c = 'wht'
    if sid == 'whirl':
        for a in range(0, 300, 20): put(im, int(10 + math.cos(math.radians(a)) * 6), int(10 + math.sin(math.radians(a)) * 6), c)
    elif sid == 'rush': _line(im, (3, 10), (15, 10), 2, c); _line(im, (12, 6), (16, 10), 2, c); _line(im, (12, 14), (16, 10), 2, c)
    elif sid == 'roar': _disc(im, (10, 10), 4, 'y2'); _line(im, (10, 2), (10, 5), 1, c); _line(im, (10, 15), (10, 18), 1, c)
    elif sid == 'triple':
        for k in range(3): _line(im, (4 + k * 4, 15), (8 + k * 4, 5), 1, c)
    elif sid == 'star':
        for a in range(0, 360, 90): _line(im, (10, 10), (10 + math.cos(math.radians(a + 45)) * 6, 10 + math.sin(math.radians(a + 45)) * 6), 2, 's4')
    elif sid == 'shadow': _disc(im, (10, 9), 4, 'ink'); put(im, 8, 8, 'y1'); put(im, 12, 8, 'y1')
    elif sid == 'fire': _disc(im, (10, 12), 4, 'y1'); _disc(im, (10, 9), 2.5, 'y2')
    elif sid == 'ice':
        for k in range(3): _line(im, (5 + k * 5, 16), (6 + k * 4, 4), 2, 'f3')
    elif sid == 'thunder': _line(im, (12, 2), (7, 10), 2, c); _line(im, (7, 10), (13, 10), 2, c); _line(im, (13, 10), (8, 18), 2, c)
    elif sid == 'heal': _line(im, (10, 4), (10, 16), 3, c); _line(im, (4, 10), (16, 10), 3, c)
    elif sid == 'orb': _disc(im, (10, 10), 5, 'f3'); _disc(im, (9, 9), 2, c)
    elif sid == 'guard':
        for y in range(4, 16):
            for x in range(5, 15):
                if abs(x - 9.5) < 5 - max(0, y - 10) * 0.8: put(im, x, y, c)
    return outline(im)

def coin(f):
    im = img(12, 12); w = [4, 3, 1, 3][f]
    for y in range(2, 10):
        for x in range(6 - w, 6 + w):
            put(im, x, y, 'y1' if x < 6 else 'or2')
    if w >= 3:
        for (x, y) in ((5, 5), (6, 5), (5, 6), (6, 6)): put(im, x, y, 'b1')
    return outline(im)

def spark(f):
    im = img(24, 24); L = [3, 8, 6, 2][f]
    for k in range(-L, L + 1):
        c = 'wht' if abs(k) < 3 else 'y2'
        put(im, 12 + k, 12, c); put(im, 12, 12 + k, c)
        if abs(k) < L - 2 and k % 2: put(im, 12 + k, 12 + k, 'y1'); put(im, 12 + k, 12 - k, 'y1')
    return im

def puff(f):
    im = img(32, 32); r = [4, 8, 11, 13, 12][f]
    for y in range(32):
        for x in range(32):
            d = math.hypot(x + 0.5 - 16, y + 0.5 - 16)
            if r - 3.5 < d < r and (x * 3 + y * 5 + f) % (2 + f) != 0: put(im, x, y, 's4' if d < r - 1.5 else 's3')
    return im

def ui_box():
    im = img(24, 24)
    for y in range(24):
        for x in range(24):
            e = min(x, y, 23 - x, 23 - y)
            if e == 0 and x in (0, 23) and y in (0, 23): continue
            c = 'ink' if e == 0 else ('b3' if e == 1 else ('b1' if e == 2 else (25, 20, 30, 225)))
            put(im, x, y, c)
    for (x, y) in ((2, 2), (21, 2), (2, 21), (21, 21)): put(im, x, y, 'y1')
    return im

def ui_slot():
    im = img(24, 24)
    for y in range(24):
        for x in range(24):
            e = min(x, y, 23 - x, 23 - y)
            put(im, x, y, 'ink' if e == 0 else ('s0' if e == 1 else (40, 34, 50, 230)))
    return im
