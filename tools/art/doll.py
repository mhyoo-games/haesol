"""캐릭터 층(몸·옷·머리·무기)을 따로 그린다. 게임에서 겹쳐 한 사람으로 만든다.

한 칸 32×48, 줄: 0 아래(앞) 1 위(뒤) 2 옆(오른쪽, 왼쪽은 뒤집음)
칸: 0 서기 1 걷기A 2 걷기B 3 휘두르기 준비 4 휘두르기 5 주문 6 맞음
"""
import math
from common import *

FW, FH = 32, 48
DIRS = ['down', 'up', 'side']
NF = 7

def pose(d, f):
    """몸의 주요 점: 머리 중심, 몸통, 손, 발."""
    bob = -1 if f in (1, 2) else (1 if f == 6 else 0)
    lean = {3: -1, 4: 2, 6: -1}.get(f, 0)
    P = {'bob': bob, 'lean': lean}
    if d == 'side':
        hx = 16 + lean
        P['head'] = (hx, 14 + bob)
        P['torso'] = (hx - 1, 22 + bob, 34 + bob)
        sw = {1: 3, 2: -3}.get(f, 0)
        P['legs'] = [((hx - 1, 34 + bob), (hx - 1 - sw, 45)), ((hx, 34 + bob), (hx + sw, 45))]
        hand = {0: (hx + 1, 31), 1: (hx - 2, 30), 2: (hx + 3, 30), 3: (hx - 4, 24), 4: (hx + 8, 28), 5: (hx + 4, 19), 6: (hx - 3, 29)}[f]
        P['hands'] = [(hand[0], hand[1] + bob)]
        P['back_hand'] = (hx - 1 - sw // 2, 30 + bob)
    else:
        P['head'] = (16, 14 + bob)
        P['torso'] = (16, 22 + bob, 34 + bob)
        la = {1: -2, 2: 0}.get(f, 0); ra = {1: 0, 2: -2}.get(f, 0)
        P['legs'] = [((13, 34 + bob), (13, 45 + la)), ((19, 34 + bob), (19, 45 + ra))]
        if d == 'down':
            right = {0: (23, 31), 1: (23, 30), 2: (23, 32), 3: (25, 23), 4: (20, 36), 5: (24, 18), 6: (24, 29)}[f]
            left = {5: (8, 18)}.get(f, (9, 31 if f != 1 else 32))
        else:
            right = {0: (9, 31), 1: (9, 32), 2: (9, 30), 3: (7, 23), 4: (12, 20), 5: (8, 18), 6: (8, 29)}[f]
            left = {5: (24, 18)}.get(f, (23, 31))
        P['hands'] = [(right[0], right[1] + bob), (left[0], left[1] + bob)]
    return P

def _line(im, a, b, w, col):
    n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
    for i in range(n + 1):
        t = i / max(1, n)
        x = a[0] + (b[0] - a[0]) * t; y = a[1] + (b[1] - a[1]) * t
        for dx in range(-(w // 2), w - w // 2):
            for dy in range(-(w // 2), w - w // 2):
                put(im, int(round(x + dx)), int(round(y + dy)), col)

def _disc(im, c, r, col, sy=1.0):
    for y in range(int(c[1] - r * sy) - 1, int(c[1] + r * sy) + 2):
        for x in range(int(c[0] - r) - 1, int(c[0] + r) + 2):
            if ((x + 0.5 - c[0]) / r) ** 2 + ((y + 0.5 - c[1]) / (r * sy)) ** 2 <= 1: put(im, x, y, col)

def shade(im, lo, hi):
    """밝은 왼쪽 위, 어두운 오른쪽 아래 가장자리."""
    out = im.copy(); px = im.load(); po = out.load()
    for y in range(im.height):
        for x in range(im.width):
            c = px[x, y]
            if not c[3]: continue
            right = x + 1 >= im.width or px[x + 1, y][3] == 0 or px[x + 1, y][:3] != c[:3]
            down = y + 1 >= im.height or px[x, y + 1][3] == 0 or px[x, y + 1][:3] != c[:3]
            up = y == 0 or px[x, y - 1][3] == 0
            left = x == 0 or px[x - 1, y][3] == 0
            if c[:3] in lo and (right or down): po[x, y] = lo[c[:3]]
            elif c[:3] in hi and (up or left): po[x, y] = hi[c[:3]]
    return out

def sheet_of(fn):
    s = img(FW * NF, FH * 3)
    for r, d in enumerate(DIRS):
        for f in range(NF):
            s.alpha_composite(fn(d, f), (f * FW, r * FH))
    return s

# ── 몸 ──
SKIN = {'m': ('sk1', 'sk2', 'sk3'), 'f': ('sk1', 'sk2', 'sk3')}
def body(g):
    s0, s1, s2 = SKIN[g]
    def fr(d, f):
        im = img(FW, FH); P = pose(d, f)
        for (a, b) in P['legs']:
            _line(im, a, b, 4, s1)
            _line(im, (b[0] - (1 if d != 'side' else 0), b[1] - 1), (b[0] + (2 if d == 'side' else 1), b[1]), 3, 'b0')  # 신발
        hx, hy = P['head']
        _line(im, (hx, hy + 6), (hx, hy + 9), 4, s1)  # 목
        for h in P['hands']: _disc(im, h, 1.8, s1)
        if d == 'side': _disc(im, P['back_hand'], 1.6, s0)
        _disc(im, (hx, hy), 7.4, s1, 0.95)
        if d == 'side': put(im, hx + 7, hy + 1, s1); put(im, hx + 7, hy + 2, s1)
        # 얼굴
        if d == 'down':
            for ex in (hx - 3, hx + 2):
                for dy in range(0, 3): put(im, ex, hy + 1 + dy, 'ink'); put(im, ex + 1, hy + 1 + dy, 'ink')
                put(im, ex, hy + 1, 'wht')
            put(im, hx - 5, hy + 4, 'pk1'); put(im, hx + 5, hy + 4, 'pk1')
            put(im, hx - 1, hy + 5, 'sk0'); put(im, hx, hy + 5, 'sk0')
            if g == 'f': put(im, hx - 1, hy + 5, 'red2'); put(im, hx, hy + 5, 'red2')
        elif d == 'side':
            for dy in range(0, 3): put(im, hx + 4, hy + 1 + dy, 'ink')
            put(im, hx + 5, hy + 1, 'ink'); put(im, hx + 4, hy + 1, 'wht')
            put(im, hx + 3, hy + 4, 'pk1'); put(im, hx + 6, hy + 5, 'sk0')
        im = shade(im, {PAL[s1][:3]: PAL[s0]}, {PAL[s1][:3]: PAL[s2]})
        return outline(im)
    return sheet_of(fr)

# ── 옷: 저고리(윗옷)·소매와 바지 또는 치마 ──
OUTFITS = {
    'commoner': {'top': ('p0', 'p1', 'p2'), 'low': ('d1', 'd2', 'd3'), 'belt': 'b1', 'trim': 'p3'},
    'warrior': {'top': ('red0', 'red1', 'red2'), 'low': ('r0', 'r1', 'r2'), 'belt': 'y1', 'trim': 's3', 'armor': ('s1', 's2', 's3')},
    'rogue': {'top': ('r0', 'r1', 'r2'), 'low': ('ink', 'r0', 'r1'), 'belt': 'red1', 'trim': 's2'},
    'mage': {'top': ('v0', 'v1', 'v2'), 'low': ('v0', 'v1', 'v2'), 'belt': 'y1', 'trim': 'y2', 'robe': True},
    'priest': {'top': ('p1', 'p2', 'p3'), 'low': ('p1', 'p2', 'p3'), 'belt': 'n2', 'trim': 'n3', 'robe': True},
}

def cloth(oid, g):
    o = OUTFITS[oid]; t0, t1, t2 = o['top']; l0, l1, l2 = o['low']
    robe = o.get('robe') or g == 'f'
    def fr(d, f):
        im = img(FW, FH); P = pose(d, f)
        cx, y0, y1 = P['torso']
        if robe:
            # 도포·치마: 아래로 넓어짐
            for y in range(y0 + 8, 44):
                k = (y - y0 - 8) / (44 - y0 - 8)
                hw = 5 + k * (4 if d != 'side' else 3)
                sw = {1: 1, 2: -1}.get(f, 0) * k * 2
                for x in range(int(cx - hw + sw), int(cx + hw + sw) + 1): put(im, x, y, l1)
            put(im, int(cx), 43, l0)
        else:
            for (a, b) in P['legs']:
                _line(im, a, (b[0], b[1] - 3), 5, l1)
        # 윗옷
        for y in range(y0, y1 + 1):
            k = (y - y0) / max(1, y1 - y0)
            hw = (5.5 - k * 0.8) if d != 'side' else (4 - k * 0.5)
            for x in range(int(cx - hw), int(cx + hw) + 1): put(im, x, y, t1)
        # 소매: 어깨에서 손 앞까지
        sh = [(cx + 5, y0 + 2), (cx - 5, y0 + 2)] if d == 'down' else [(cx - 5, y0 + 2), (cx + 5, y0 + 2)]
        if d == 'side': sh = [(cx + 1, y0 + 2)]
        for i, h in enumerate(P['hands']):
            s = sh[i] if i < len(sh) else sh[0]
            hand = h
            mid = ((s[0] + hand[0]) / 2, (s[1] + hand[1]) / 2)
            end = (hand[0] - (hand[0] - s[0]) * 0.22, hand[1] - (hand[1] - s[1]) * 0.22)
            _line(im, s, end, 4, t1)
            _line(im, (end[0], end[1]), (end[0], end[1]), 4, t2 if False else t1)
        if d == 'side':
            _line(im, (cx - 1, y0 + 2), (P['back_hand'][0], P['back_hand'][1] - 2), 3, t0)
        # 깃(동정)·고름·띠
        if d == 'down':
            for k in range(4): put(im, int(cx) - 2 + k, y0 + k, o['trim']); put(im, int(cx) + 2 - k, y0 + k, o['trim'])
            put(im, int(cx) + 1, y0 + 5, o['belt']); put(im, int(cx) + 2, y0 + 6, o['belt']); put(im, int(cx) + 1, y0 + 7, o['belt'])
        elif d == 'side':
            for k in range(3): put(im, int(cx) + 2 + k // 2, y0 + k, o['trim'])
        for x in range(int(cx - 5), int(cx + 6)):
            if im.getpixel((x, y1 - 1))[3]: put(im, x, y1 - 1, o['belt'])
        if 'armor' in o:
            a0, a1, a2 = o['armor']
            for y in range(y0 + 1, y0 + 7):
                for x in range(int(cx - 4), int(cx + 5)):
                    if (x + y) % 3 != 0 and d != 'up': put(im, x, y, a1)
                    elif d == 'up': put(im, x, y, a1)
            for s in (sh if d != 'side' else sh):
                _disc(im, (s[0], s[1]), 2.6, a1)
        lo = {PAL[t1][:3]: PAL[t0], PAL[l1][:3]: PAL[l0]}; hi = {PAL[t1][:3]: PAL[t2], PAL[l1][:3]: PAL[l2]}
        if 'armor' in o: lo[PAL[o['armor'][1]][:3]] = PAL[o['armor'][0]]; hi[PAL[o['armor'][1]][:3]] = PAL[o['armor'][2]]
        return outline(shade(im, lo, hi))
    return sheet_of(fr)

# ── 머리 모양 ──
HAIRS = ['short', 'topknot', 'long', 'bun']
HAIR_COLORS = {'black': ('hr0', 'hr1', 'hr2'), 'brown': ('hr1', 'hr2', 'b2'), 'chestnut': ('b1', 'b2', 'b3'), 'ash': ('r1', 'r2', 'r3')}

def hair(style, color):
    c0, c1, c2 = HAIR_COLORS[color]
    def fr(d, f):
        im = img(FW, FH); P = pose(d, f)
        hx, hy = P['head']
        # 머리 덮개 (정수리)
        for y in range(hy - 9, hy + 8):
            for x in range(hx - 9, hx + 10):
                dx, dy = x + 0.5 - hx, y + 0.5 - (hy - 1)
                if dx * dx / 64 + dy * dy / 56 > 1: continue
                if d == 'down':
                    # 이마는 비움 (앞머리는 아래에)
                    if y > hy - 3 and abs(dx) < 6.5: continue
                    if y > hy + 1: continue
                elif d == 'side':
                    if x > hx + 2 and y > hy - 3: continue
                    if y > hy + 3 and x > hx - 3: continue
                put(im, x, y, c1)
        if d == 'down':  # 앞머리
            for x in range(hx - 6, hx + 7):
                k = 1 + (x % 3 == 0) + (x % 5 == 0)
                for y in range(hy - 4, hy - 4 + k): put(im, x, y, c1)
        if style == 'short' and d != 'up':
            for x in (hx - 4, hx, hx + 4): put(im, x, hy - 9, c1); put(im, x + 1, hy - 10, c1)
        if style == 'topknot':  # 상투
            _disc(im, (hx, hy - 9), 2.6, c1); put(im, hx, hy - 12, c1)
            for x in range(hx - 2, hx + 3): put(im, x, hy - 7, 'red1')
        if style == 'bun':
            bx = hx if d != 'side' else hx - 5
            _disc(im, (bx, hy - 7 if d != 'up' else hy - 6), 3.4, c1)
            if d != 'down': put(im, bx + 3, hy - 9, 'y1'); put(im, bx + 4, hy - 10, 'y1')
        if style == 'long':  # 댕기 땋은 머리
            if d == 'up':
                for y in range(hy + 4, hy + 20): put(im, hx - 1, y, c1); put(im, hx, y, c1); put(im, hx + 1, y, c0 if y % 3 == 0 else c1)
                for x in range(hx - 2, hx + 3): put(im, x, hy + 20, 'red2'); put(im, x, hy + 21, 'red1')
            elif d == 'side':
                for y in range(hy + 2, hy + 16): put(im, hx - 6 - (y - hy) // 6, y, c1); put(im, hx - 5 - (y - hy) // 6, y, c1)
                put(im, hx - 8, hy + 16, 'red2'); put(im, hx - 7, hy + 16, 'red2')
            else:
                for y in range(hy, hy + 8): put(im, hx - 8, y, c1); put(im, hx + 8, y, c1)
        return outline(shade(im, {PAL[c1][:3]: PAL[c0]}, {PAL[c1][:3]: PAL[c2]}))
    return sheet_of(fr)

# ── 무기 ──
def weapon(kind):
    def fr(d, f):
        im = img(FW, FH); P = pose(d, f)
        hand = P['hands'][0]
        ang = {0: 100, 1: 95, 2: 105, 3: -120, 4: 20, 5: -80, 6: 120}[f]
        if d == 'up': ang = {0: 80, 1: 85, 2: 75, 3: -60, 4: -100, 5: -100, 6: 60}[f]
        if d == 'down' and f == 4: ang = 75
        if d == 'side' and f in (0, 1, 2): ang = 110
        a = math.radians(ang)
        ln = {'sword': 15, 'dagger': 8, 'staff': 20, 'bell': 14, 'club': 12}[kind]
        tip = (hand[0] + math.cos(a) * ln, hand[1] + math.sin(a) * ln)
        back = (hand[0] - math.cos(a) * (3 if kind != 'staff' else 6), hand[1] - math.sin(a) * (3 if kind != 'staff' else 6))
        if kind in ('sword', 'dagger'):
            _line(im, back, hand, 2, 'b1')
            gx, gy = -math.sin(a) * 2.5, math.cos(a) * 2.5
            _line(im, (hand[0] - gx, hand[1] - gy), (hand[0] + gx, hand[1] + gy), 2, 'y1')
            _line(im, hand, tip, 2, 's3')
            _line(im, (hand[0] + math.cos(a) * 2, hand[1] + math.sin(a) * 2), tip, 1, 's4')
        elif kind == 'staff':
            _line(im, back, tip, 2, 'b2')
            _disc(im, tip, 2.6, 'f2'); put(im, int(tip[0]) - 1, int(tip[1]) - 1, 'f3')
        elif kind == 'bell':  # 방울 지팡이
            _line(im, back, tip, 2, 'b3')
            for k in (-2, 0, 2):
                _disc(im, (tip[0] + k, tip[1] + abs(k) * 0.5), 1.4, 'y1')
        elif kind == 'club':
            _line(im, back, tip, 3, 'b2'); _disc(im, tip, 3, 'b2')
        return outline(im)
    return sheet_of(fr)

# ── 대화 얼굴 그림 (48×48) ──
def portrait(skin=('sk1', 'sk2', 'sk3'), hair_c=('hr0', 'hr1', 'hr2'), cloth_c=('n1', 'n2', 'n3'), style='short', g='m', beard=False, age=0, expr=0):
    """expr 0 보통 1 웃음 2 놀람 3 화남"""
    W = 48; im = img(W, W)
    s0, s1, s2 = skin; c0, c1, c2 = hair_c; o0, o1, o2 = cloth_c
    # 어깨와 옷
    for y in range(36, 48):
        for x in range(4, 44):
            if ((x - 24) / 20) ** 2 + ((y - 50) / 15) ** 2 < 1: put(im, x, y, o1)
    for k in range(10): put(im, 24 - k, 37 + k, 'p3'); put(im, 24 + k, 37 + k, 'p3'); put(im, 24 - k, 38 + k, 'p3'); put(im, 24 + k, 38 + k, 'p3')
    # 목·얼굴
    for y in range(30, 39):
        for x in range(20, 29): put(im, x, y, s1)
    _disc(im, (24, 22), 12, s1, 1.1)
    put(im, 11, 23, s1); put(im, 11, 24, s1); put(im, 37, 23, s1); put(im, 37, 24, s1)
    # 머리카락
    for y in range(4, 20):
        for x in range(10, 39):
            dx, dy = x + 0.5 - 24, y + 0.5 - 18
            if dx * dx / 196 + dy * dy / 170 <= 1 and (y < 13 or abs(dx) > 9 - (y - 13) * 0.3 and y < 17):
                put(im, x, y, c1)
    for x in range(13, 36, 3): put(im, x, 13, c1); put(im, x + 1, 14, c1)
    if style == 'topknot': _disc(im, (24, 4), 3.5, c1)
    if style == 'bun': _disc(im, (24, 4), 5, c1)
    if style == 'long':
        for y in range(16, 40): put(im, 10, y, c1); put(im, 11, y, c1); put(im, 37, y, c1); put(im, 38, y, c1)
    if age:  # 흰 머리
        c1 = 's3'
    # 눈썹·눈
    ey = 22
    for (ex, s) in ((18, -1), (29, 1)):
        bw = 4
        for k in range(bw): put(im, ex - 1 + k, ey - 4 + (1 if (expr == 3 and (k < 2 if s > 0 else k > 1)) else 0) - (1 if expr == 2 else 0), c0)
        h = 4 if expr != 1 else 1
        for dy in range(h):
            for dx in range(3): put(im, ex - 1 + dx + (0 if s < 0 else 0), ey + dy - (0 if expr != 1 else -1), 'ink')
        if expr != 1: put(im, ex - 1, ey, 'wht'); put(im, ex, ey + 1, 'wht') if expr == 2 else None
    put(im, 14, 28, 'pk1'); put(im, 15, 28, 'pk1'); put(im, 33, 28, 'pk1'); put(im, 34, 28, 'pk1')
    put(im, 24, 26, s0); put(im, 24, 27, s0)
    # 입
    if expr == 1:
        for x in range(21, 28): put(im, x, 30, 'ink')
        for x in range(22, 27): put(im, x, 31, 'red1')
    elif expr == 2:
        _disc(im, (24, 31), 1.8, 'ink')
    elif expr == 3:
        for x in range(21, 28): put(im, x, 31, 'ink')
        put(im, 21, 30, 'ink'); put(im, 27, 30, 'ink')
    else:
        for x in range(22, 27): put(im, x, 30, 'sk0' if g == 'm' else 'red1')
    if beard:
        for y in range(30, 38):
            for x in range(18, 31):
                if ((x - 24) / 7) ** 2 + ((y - 31) / 7) ** 2 < 1 and y > 31: put(im, x, y, c1 if not age else 's3')
    if age:
        for (x, y) in ((16, 24), (31, 24), (20, 33)): put(im, x, y, s0)
    im = shade(im, {PAL[s1][:3]: PAL[s0], PAL[o1][:3]: PAL[o0], PAL[c1][:3]: PAL[c0]}, {PAL[s1][:3]: PAL[s2], PAL[o1][:3]: PAL[o2], PAL[c1][:3]: PAL[c2]})
    return outline(im)
