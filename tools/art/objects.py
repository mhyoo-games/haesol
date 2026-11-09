"""소품: 나무, 한옥, 울타리, 바위, 덤불, 표지판, 우물, 석등, 항아리."""
import math, random
from common import *

def shade_blob(w, h, circles, pal, seed, light=(-0.6, -0.8)):
    """여러 원을 합친 덩어리를 왼쪽 위 빛으로 칠한다. pal: 어두움→밝음."""
    im = img(w, h); r = random.Random(seed); nz = Noise(seed)
    lx, ly = light
    for y in range(h):
        for x in range(w):
            best = None
            for (cx, cy, cr) in circles:
                d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
                if d < cr:
                    k = 1 - d / cr
                    if best is None or k > best[0]: best = (k, cx, cy, cr)
            if not best: continue
            k, cx, cy, cr = best
            nx, ny = (x + 0.5 - cx) / cr, (y + 0.5 - cy) / cr
            lit = (nx * lx + ny * ly) * 0.6 + k * 0.2 + (nz.v(x, y, 1.6) - 0.5) * 0.32
            i = int((lit + 0.62) / 1.25 * len(pal)); i = max(0, min(len(pal) - 1, i))
            put(im, x, y, pal[i])
    return im

def tree(seed=1, kind='round'):
    W, H = 32, 44
    r = random.Random(seed)
    im = img(W, H)
    # 그림자
    for y in range(39, 44):
        for x in range(4, 28):
            if ((x - 16) / 12) ** 2 + ((y - 41.5) / 2.6) ** 2 < 1: put(im, x, y, 'shadow')
    # 줄기
    for y in range(26, 41):
        for x in range(13, 19):
            c = 'b2' if x < 15 else ('b1' if x < 18 else 'b0')
            if y > 38 and (x == 12 or x == 19): c = 'b1'
            put(im, x, y, c)
    put(im, 12, 40, 'b1'); put(im, 19, 40, 'b0'); put(im, 15, 31, 'b0'); put(im, 16, 34, 'b3')
    if kind == 'round':
        circles = [(16, 15, 12), (9, 20, 7.5), (23, 20, 7.5), (16, 24, 7), (11, 11, 6), (21, 10, 6.5)]
        pal = ['g0', 'g1', 'g2', 'g3', 'g4', 'g5']
    elif kind == 'maple':
        circles = [(16, 15, 12), (9, 20, 7.5), (23, 20, 7.5), (16, 24, 7), (11, 11, 6), (21, 10, 6.5)]
        pal = ['red0', 'red1', 'red2', 'or1', 'or2', 'y1']
    else:  # 소나무: 층층이
        circles = []
        pal = ['g0', 'g0', 'g1', 'g2', 'g3', 'g4']
    if kind == 'pine':
        can = img(W, H)
        for i, (cy, hw) in enumerate(((30, 14), (23, 12), (16, 10), (9, 7))):
            for y in range(cy - 9, cy + 1):
                t = (y - (cy - 9)) / 9
                half = hw * t ** 0.8
                for x in range(W):
                    if abs(x + 0.5 - 16) < half:
                        side = (x + 0.5 - 16) / max(1, half)
                        lit = -side * 0.5 + (1 - t) * 0.2 + r.random() * 0.25
                        k = int((lit + 0.55) * 3.4); k = max(0, min(5, k))
                        if y == cy: k = 0
                        put(can, x, y, pal[k])
        im.alpha_composite(outline(can, 'ink2'))
        return im
    can = shade_blob(W, H - 10, circles, pal, seed)
    # 잎 덩어리 사이 어두운 틈
    for (cx, cy, cr) in circles[1:]:
        for a in range(0, 360, 12):
            x = int(cx + math.cos(math.radians(a)) * (cr - 0.5)); y = int(cy + math.sin(math.radians(a)) * (cr - 0.5))
            if 0 < y < 34 and math.sin(math.radians(a)) < -0.3 and can.getpixel((x, y))[3]:
                put(can, x, y, pal[1])
    if kind == 'maple' or seed % 3 == 0:
        fr = 'red2' if kind == 'round' else 'y2'
        for _ in range(5):
            x, y = r.randrange(6, 26), r.randrange(6, 26)
            if can.getpixel((x, y))[3]: put(can, x, y, fr); put(can, x, y + 1, 'red0' if kind == 'round' else 'or1')
    im.alpha_composite(outline(can, 'ink2'))
    return im

def rock(seed=1, big=False):
    w, h = (24, 20) if big else (16, 14)
    im = img(w, h)
    for y in range(h - 4, h):
        for x in range(w):
            if ((x - w / 2 + 0.5) / (w / 2 - 1)) ** 2 + ((y - (h - 2.5)) / 2) ** 2 < 1: put(im, x, y, 'shadow')
    circles = [(w * 0.45, h * 0.55, h * 0.42), (w * 0.62, h * 0.62, h * 0.36), (w * 0.32, h * 0.66, h * 0.3)]
    b = shade_blob(w, h - 1, circles, ['s0', 's1', 's2', 's3', 's4'], seed)
    # 이끼
    for x in range(w):
        for y in range(h - 1):
            if b.getpixel((x, y))[3] and y < h * 0.4 and (x * 5 + y * 3 + seed) % 7 == 0: put(b, x, y, 'g3')
    im.alpha_composite(outline(b))
    return im

def bush(seed=1, berries=False):
    im = img(16, 16)
    for x in range(1, 15):
        put(im, x, 15, 'shadow'); put(im, x, 14, 'shadow')
    b = shade_blob(16, 15, [(8, 9, 6.5), (4.5, 10.5, 4), (11.5, 10.5, 4), (8, 5.5, 4.5)], ['g0', 'g1', 'g2', 'g3', 'g4'], seed)
    if berries:
        for (x, y) in ((5, 8), (10, 7), (8, 11), (12, 11)):
            put(b, x, y, 'red2'); put(b, x, y + 1, 'red0')
    im.alpha_composite(outline(b))
    return im

def fence(kind='h'):
    im = img(16, 20)
    if kind in ('h', 'post'):
        for y in range(6, 18):
            for x in range(6, 10):
                put(im, x, y, 'b3' if x == 6 else ('b2' if x < 9 else 'b1'))
        put(im, 7, 5, 'b3'); put(im, 8, 5, 'b2'); put(im, 6, 18, 'shadow'); put(im, 9, 18, 'shadow')
    if kind == 'h':
        for x in range(0, 16):
            if 6 <= x < 10: continue
            for y, c in ((8, 'b3'), (9, 'b2'), (13, 'b3'), (14, 'b2')):
                put(im, x, y, c)
            put(im, x, 10, 'b1'); put(im, x, 15, 'b1')
    if kind == 'v':
        for y in range(0, 20):
            for x in range(6, 10):
                put(im, x, y, 'b3' if x == 6 else ('b2' if x < 9 else 'b1'))
            if y % 8 == 0: put(im, 6, y, 'b1'); put(im, 9, y, 'b0')
    return outline(im)

def hanok(w=72, seed=1):
    """기와지붕 집. 끝이 살짝 올라간 처마, 나무 기둥, 창살, 돌 기단."""
    H = 64
    im = img(w, H)
    roof_top, roof_bot = 6, 28
    wall_top, wall_bot = 26, 54
    base_top = 54
    # 그림자
    for y in range(58, 64):
        for x in range(4, w - 4):
            if y < 62 or 8 < x < w - 8: put(im, x, y, 'shadow')
    # 기단 (돌)
    for y in range(base_top, 60):
        for x in range(6, w - 6):
            bx = (x + (5 if (y - base_top) // 3 % 2 else 0)) % 10
            c = 's2'
            if (y - base_top) % 3 == 2 or bx == 9: c = 's1'
            if y == base_top: c = 's3'
            put(im, x, y, c)
    # 벽과 기둥
    cols = [10, w // 2 - 1, w - 13]
    for y in range(wall_top, wall_bot):
        for x in range(10, w - 10):
            put(im, x, y, 'p2' if y > wall_top + 2 else 'p1')
        put(im, 10, y, 'p1')
    for cx in [10] + [10 + (w - 23) * i // 3 for i in (1, 2)] + [w - 13]:
        for y in range(wall_top, wall_bot):
            for x in range(cx, cx + 3):
                put(im, x, y, ('b3', 'b2', 'b1')[x - cx])
    # 인방(가로 나무)
    for x in range(10, w - 10):
        put(im, x, wall_top + 2, 'b2'); put(im, x, wall_top + 3, 'b1'); put(im, x, wall_bot - 1, 'b1')
    # 창문 (창살 + 따뜻한 빛)
    px = [10 + (w - 23) * i // 3 for i in range(4)]
    for i in range(3):
        x0, x1 = px[i] + 3, px[i + 1]
        if i == 1:  # 가운데는 문
            for y in range(wall_top + 7, wall_bot - 1):
                for x in range(x0 + 2, x1 - 2):
                    c = 'p3' if (x - x0) % 3 and (y - wall_top) % 4 else 'b1'
                    if x == x0 + 2 or x == x1 - 3: c = 'b2'
                    put(im, x, y, c)
            put(im, (x0 + x1) // 2 - 2, (wall_top + wall_bot) // 2 + 3, 'y1'); put(im, (x0 + x1) // 2 + 1, (wall_top + wall_bot) // 2 + 3, 'y1')
        else:
            for y in range(wall_top + 9, wall_top + 19):
                for x in range(x0 + 2, x1 - 2):
                    c = 'y2' if (x - x0) % 3 and (y - wall_top) % 3 else 'b1'
                    if y == wall_top + 9 or y == wall_top + 18 or x == x0 + 2 or x == x1 - 3: c = 'b2'
                    put(im, x, y, c)
    # 지붕: 곡선 처마
    for y in range(roof_top, roof_bot + 4):
        t = (y - roof_top) / (roof_bot - roof_top)
        half = 12 + (w / 2 - 12) * min(1, t * 1.15)
        lift = 0
        for x in range(w):
            dx = abs(x + 0.5 - w / 2)
            edge = (dx / (w / 2)) ** 4 * 5  # 처마 끝이 올라감
            yy = y - edge
            if dx <= half and roof_top <= yy <= roof_bot:
                tt = (yy - roof_top) / (roof_bot - roof_top)
                c = 'r2'
                row = int(yy - roof_top)
                if (int(x + (2 if row // 3 % 2 else 0))) % 4 == 0: c = 'r1'  # 기와 골
                if row % 3 == 2: c = 'r1'
                if tt < 0.12: c = 'r3' if (x % 2) else 'r2'
                if yy > roof_bot - 1.2: c = 'r0'
                if dx > half - 1.2: c = 'r1'
                put(im, x, y, c)
    # 용마루
    for x in range(int(w / 2 - 14), int(w / 2 + 14)):
        put(im, x, roof_top - 1, 'r3'); put(im, x, roof_top, 'r3'); put(im, x, roof_top + 1, 'r1')
    for s in (-1, 1):
        for k in range(3):
            put(im, int(w / 2 + s * (14 + k)), roof_top - 2 - k // 2, 'r3')
    # 처마 밑 그림자
    for x in range(10, w - 10):
        put(im, x, wall_top, 'b0'); put(im, x, wall_top + 1, 'b1')
    return outline(im)

def sign():
    im = img(16, 18)
    for y in range(8, 17):
        put(im, 7, y, 'b2'); put(im, 8, y, 'b1')
    for y in range(2, 9):
        for x in range(2, 14):
            c = 'b3' if y < 8 else 'b1'
            if y == 2: c = 'b4'
            put(im, x, y, c)
    for x in (4, 5, 6, 8, 9, 11): put(im, x, 4, 'b1')
    for x in (4, 5, 7, 8, 10, 11): put(im, x, 6, 'b1')
    put(im, 6, 17, 'shadow'); put(im, 9, 17, 'shadow')
    return outline(im)

def well():
    im = img(32, 32)
    for y in range(26, 32):
        for x in range(2, 30):
            if ((x - 16) / 14) ** 2 + ((y - 28.5) / 3) ** 2 < 1: put(im, x, y, 'shadow')
    # 지붕 기둥
    for y in range(4, 24):
        for x in (5, 6, 25, 26): put(im, x, y, 'b2' if x in (5, 25) else 'b1')
    for x in range(2, 30):
        t = abs(x - 15.5) / 14
        for y in range(int(2 + t * 3), int(7 + t * 3)):
            put(im, x, y, 'r2' if (x + y) % 3 else 'r1')
        put(im, x, int(7 + t * 3), 'r0')
    # 돌 둘레
    for y in range(16, 28):
        for x in range(4, 28):
            if ((x - 15.5) / 12) ** 2 + ((y - 22) / 6) ** 2 < 1:
                inner = ((x - 15.5) / 9) ** 2 + ((y - 20) / 3.2) ** 2 < 1
                c = 'w0' if inner else ('s3' if (x // 3 + y // 2) % 2 else 's2')
                if not inner and y > 23: c = 's1' if (x // 3 + y // 2) % 2 else 's2'
                put(im, x, y, c)
    # 두레박 줄
    for y in range(8, 18): put(im, 16, y, 'b3')
    for x in range(14, 19):
        for y in range(15, 19): put(im, x, y, 'b2' if x < 17 else 'b1')
    return outline(im)

def lantern():
    """석등: 밤에 불빛이 켜진다(빛은 게임에서 따로)."""
    im = img(16, 28)
    for x in range(2, 14): put(im, x, 27, 'shadow')
    def box(x0, y0, x1, y1, c1, c2, c3):
        for y in range(y0, y1):
            for x in range(x0, x1):
                put(im, x, y, c1 if x == x0 else (c3 if x == x1 - 1 or y == y1 - 1 else c2))
    box(4, 22, 12, 27, 's3', 's2', 's1')
    box(6, 14, 10, 22, 's3', 's2', 's1')
    box(3, 12, 13, 14, 's3', 's2', 's1')
    box(4, 6, 12, 12, 's3', 's2', 's1')
    for y in range(7, 11):
        for x in range(6, 10): put(im, x, y, 'y1' if y > 7 else 'y2')
    for x in range(2, 14):
        put(im, x, 5, 's3' if x < 8 else 's2'); put(im, x, 4, 's2' if 3 < x < 12 else None)
    for x in range(5, 11): put(im, x, 3, 's3')
    put(im, 7, 2, 's3'); put(im, 8, 2, 's2')
    return outline(im)

def jar(kind=0):
    im = img(16, 16)
    for x in range(3, 13): put(im, x, 15, 'shadow')
    b = shade_blob(16, 15, [(8, 9.5, 5.5), (8, 7.5, 4.6)], ['b0', 'b1', 'b2', 'b3'] if kind == 0 else ['red0', 'red1', 'red2', 'red3'], 3)
    for x in range(5, 11):
        put(b, x, 3, 'b1' if kind == 0 else 'red0'); put(b, x, 4, 'b2' if kind == 0 else 'red1')
    put(b, 6, 7, 'p3'); put(b, 6, 8, 'p2')
    im.alpha_composite(outline(b))
    return im

def bridge():
    """물 위 나무다리 한 칸 (가로로 이어 붙임)."""
    im = img(16, 16)
    for x in range(16):
        for y in range(3, 14):
            c = 'b3' if (x % 4) != 3 else 'b1'
            if y == 3: c = 'b4' if (x % 4) != 3 else 'b2'
            if y == 13: c = 'b0'
            put(im, x, y, c)
        put(im, x, 14, 'w1'); put(im, x, 2, 'b1'); put(im, x, 1, 'b2' if x % 8 else 'b0')
    for x in (0, 8):
        for y in range(0, 4): put(im, x, y, 'b1')
    return im

def crate():
    im = img(16, 16)
    for x in range(2, 15): put(im, x, 15, 'shadow')
    for y in range(3, 15):
        for x in range(2, 14):
            c = 'b3' if (y - 3) % 4 != 3 else 'b1'
            if x in (2, 13) or y in (3, 14): c = 'b1'
            if y == 3 and 2 < x < 13: c = 'b4'
            put(im, x, y, c)
    for k in range(10): put(im, 3 + k, 4 + k, 'b2')
    return outline(im)
