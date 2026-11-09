"""바닥 타일: 풀, 꽃·돌 장식, 흙길·물·돌바닥(모서리 4칸으로 정하는 이중 격자 방식)."""
import math, random
from common import *

T = 32

class PNoise:
    """T칸마다 반복되는 매끄러운 잡음 (타일 이음매가 안 보이게)."""
    def __init__(self, seed, cells=4):
        r = random.Random(seed); self.n = cells
        self.g = [[r.random() for _ in range(cells)] for _ in range(cells)]
    def v(self, x, y):
        n = self.n; x = x / T * n; y = y / T * n
        x0, y0 = int(math.floor(x)), int(math.floor(y)); fx, fy = x - x0, y - y0
        fx = fx*fx*(3-2*fx); fy = fy*fy*(3-2*fy); g = self.g
        a = g[y0 % n][x0 % n]; b = g[y0 % n][(x0+1) % n]; c = g[(y0+1) % n][x0 % n]; d = g[(y0+1) % n][(x0+1) % n]
        return (a*(1-fx)+b*fx)*(1-fy) + (c*(1-fx)+d*fx)*fy

def grass(seed, tufts=0, flowers=False):
    im = img(T, T); r = random.Random(seed)
    n1 = PNoise(seed, 4); n2 = PNoise(seed + 7, 16)
    for y in range(T):
        for x in range(T):
            v = n1.v(x, y) * 0.65 + n2.v(x, y) * 0.35
            c = 'g2'
            if n1.v(x, y) > 0.58: c = 'g3' if n2.v(x, y) > 0.42 else 'g2'
            if n1.v(x, y) < 0.32 and n2.v(x, y) < 0.45: c = 'g1'
            if c == 'g2' and n2.v(x, y) > 0.8: c = 'g3'
            put(im, x, y, c)
    for _ in range(tufts * 3):
        x, y = r.randrange(1, T - 2), r.randrange(2, T - 1)
        put(im, x, y, 'g4'); put(im, x + 1, y - 1, 'g4'); put(im, x + 2, y, 'g4')
        put(im, x + 1, y, 'g1')
    return im

def decal(kind, seed):
    im = img(T, T); r = random.Random(seed)
    if kind == 'flowers':
        cols = [('wht', 'y1'), ('y1', 'or1'), ('pk2', 'pk1'), ('v3', 'y2')]
        for _ in range(6):
            pc, cc = cols[r.randrange(len(cols))]
            x, y = r.randrange(3, T - 4), r.randrange(3, T - 4)
            put(im, x, y + 2, 'g1'); put(im, x, y + 1, 'g3')
            for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)): put(im, x + dx, y + dy - 1, pc)
            put(im, x, y - 1, cc)
    elif kind == 'pebbles':
        for _ in range(3):
            x, y = r.randrange(3, T - 4), r.randrange(4, T - 4)
            put(im, x, y, 's3'); put(im, x + 1, y, 's2'); put(im, x, y + 1, 's1'); put(im, x + 1, y + 1, 's1')
            put(im, x - 1, y + 1, 'g1'); put(im, x + 2, y + 1, 'g1'); put(im, x, y + 2, 'g1'); put(im, x + 1, y + 2, 'g1')
    elif kind == 'tall':
        for i in range(10):
            x = 4 + i * 2 + r.randrange(0, 2); h = r.randrange(6, 13)
            for k in range(h):
                put(im, x + (1 if k > h - 3 and i % 2 else 0), T - 2 - k, 'g4' if k > h - 3 else 'g3')
            put(im, x, T - 1, 'g1')
    elif kind == 'clover':
        for _ in range(2):
            x, y = r.randrange(3, 12), r.randrange(3, 12)
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (2, 1), (1, -1), (0, 2)):
                put(im, x + dx, y + dy, 'g4' if (dx + dy) % 2 else 'g3')
            put(im, x + 1, y + 2, 'g1')
    return im

def field(mask, x, y, seed):
    """모서리 값(TL,TR,BL,BR)을 섞어 0~1. 가장자리에서는 잡음이 0이라 이웃 타일과 이어진다."""
    tl, tr, bl, br = [(mask >> i) & 1 for i in (3, 2, 1, 0)]
    u = (x + 0.5) / T; v = (y + 0.5) / T
    f = (tl * (1 - u) + tr * u) * (1 - v) + (bl * (1 - u) + br * u) * v
    nz = PNoise(seed, 4).v(x, y) - 0.5
    f += nz * 0.28 * math.sin(math.pi * u) * math.sin(math.pi * v)
    # 둥글게: 가운데 쪽을 조금 끌어올림
    return f

def region(mask, seed):
    return [[field(mask, x, y, seed) > 0.5 for x in range(T)] for y in range(T)]

def path_tile(mask, seed=11):
    im = img(T, T)
    if mask == 0: return im
    R = region(mask, seed); n = PNoise(seed + 3, 16); r = random.Random(seed * 31 + mask)
    def inside(x, y):
        if 0 <= x < T and 0 <= y < T: return R[y][x]
        # 바깥은 모서리 규칙으로 추정
        xx, yy = min(T - 1, max(0, x)), min(T - 1, max(0, y))
        return R[yy][xx]
    for y in range(T):
        for x in range(T):
            if not R[y][x]:
                # 길 위쪽 풀 그림자 / 아래쪽 풀 밝은 테
                if inside(x, y + 1): put(im, x, y, 'g4')
                continue
            edge = not (inside(x+1, y) and inside(x-1, y) and inside(x, y+1) and inside(x, y-1))
            v = n.v(x, y)
            c = 'd3'
            if v > 0.7 and dither(x, y, 0.25): c = 'd4'
            if v < 0.28 and dither(x, y, 0.25): c = 'd2'
            if edge: c = 'd2'
            if not inside(x, y - 1): c = 'd1'
            put(im, x, y, c)
    for _ in range(2):
        x, y = r.randrange(T), r.randrange(T)
        if R[y][x] and inside(x+1, y) and inside(x, y+1):
            put(im, x, y, 'd4'); put(im, x + 1, y, 'd2'); put(im, x, y + 1, 'd1')
    return im

def plaza_tile(mask, seed=23):
    """마을 마당 돌바닥."""
    im = img(T, T)
    if mask == 0: return im
    R = region(mask, seed)
    def inside(x, y):
        xx, yy = min(T - 1, max(0, x)), min(T - 1, max(0, y)); return R[yy][xx]
    for y in range(T):
        for x in range(T):
            if not R[y][x]:
                if inside(x, y + 1): put(im, x, y, 'g1')
                continue
            # 8×8 벽돌 무늬 (반 칸씩 엇갈림)
            bx = (x + (8 if (y // 16) % 2 else 0)) % 16; by = y % 16
            c = 's2'
            if by == 15 or bx == 15: c = 's1'
            elif by == 0 or bx == 0: c = 's3'
            elif (x * 7 + y * 3) % 13 == 0: c = 's1'
            if not inside(x, y - 1) or not inside(x - 1, y) or not inside(x + 1, y): c = 's1'
            if not inside(x, y + 1): c = 's0'
            put(im, x, y, c)
    return im

def water_tile(mask, frame, seed=41):
    im = img(T, T)
    if mask == 0: return im
    R = region(mask, seed)
    def inside(x, y):
        xx, yy = min(T - 1, max(0, x)), min(T - 1, max(0, y)); return R[yy][xx]
    for y in range(T):
        for x in range(T):
            if not R[y][x]:
                continue
            d = 9
            for k in range(1, 6):
                if not (inside(x+k, y) and inside(x-k, y) and inside(x, y+k) and inside(x, y-k)): d = k; break
            if not (inside(x+1, y) and inside(x-1, y) and inside(x, y+1) and inside(x, y-1)): d = 0
            # 물결: 시간에 따라 흐르는 사인 무늬
            c = 'w2' if d < 4 else 'w1'
            if d == 3 and (x + y) % 2: c = 'w1'
            # 반짝이는 물결 조각: 프레임마다 옆으로 흐른다
            for (sx, sy) in ((3, 4), (20, 9), (6, 25), (26, 18), (12, 14), (24, 29)):
                xx = (sx + frame * 2) % T
                if y == sy and xx <= x < xx + 3 and d >= 1: c = 'w3' if x != xx + 1 else 'w4'
            if d == 0: c = 'foam' if (x + frame) % 4 else 'w4'
            elif d == 1 and c == 'w2': c = 'w3' if (x + y + frame) % 5 == 0 else 'w2'
            # 물가 위쪽은 언덕 그림자
            if not inside(x, y - 1) and d == 0: c = 'g1'
            elif not inside(x, y - 2) and d <= 1: c = 'w1'
            put(im, x, y, c)
    return im

def build():
    W, H = 16, 8
    at = img(W * T, H * T)
    for i in range(8):
        at.alpha_composite(grass(100 + i, tufts=(0, 1, 2, 0, 1, 3, 0, 2)[i]), (i * T, 0))
    kinds = ['flowers', 'flowers', 'pebbles', 'tall', 'clover', 'flowers', 'tall', 'pebbles']
    for i, k in enumerate(kinds):
        at.alpha_composite(decal(k, 200 + i), (i * T, T))
    for m in range(16):
        at.alpha_composite(path_tile(m), (m * T, 2 * T))
        for f in range(3):
            at.alpha_composite(water_tile(m, f), (m * T, (3 + f) * T))
        at.alpha_composite(plaza_tile(m), (m * T, 6 * T))
    return at
