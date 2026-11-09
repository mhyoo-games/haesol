"""지도를 코드로 짓는다 → data/maps.json  (한 칸 32픽셀)
땅: . 풀  P 흙길  S 돌길  W 물  D 다리
소품: T t M N 나무  K 짙은 나무  r R 바위  b B 덤불  f F 울타리  l 석등  j J 항아리  c 상자  H 성벽  X 굴벽  C 밭  k 목책  # 막힘
python3 tools/maps/gen.py
"""
import json, os, random

class Map:
    def __init__(self, key, name, w, h, music, theme='', tint=(1, 1, 1), seed=1, dark=False):
        self.key, self.name, self.w, self.h, self.music, self.theme, self.tint, self.dark = key, name, w, h, music, theme, tint, dark
        self.g = [['.'] * w for _ in range(h)]
        self.o = [[' '] * w for _ in range(h)]
        self.e = []; self.r = random.Random(seed)
    def fill(self, L, x0, y0, x1, y1, ch):
        A = self.g if L == 'g' else self.o
        for y in range(max(0, y0), min(self.h, y1 + 1)):
            for x in range(max(0, x0), min(self.w, x1 + 1)): A[y][x] = ch
    def blob(self, L, cx, cy, rx, ry, ch, jag=0.15):
        A = self.g if L == 'g' else self.o
        for y in range(self.h):
            for x in range(self.w):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1 - jag * self.r.random(): A[y][x] = ch
    def line(self, L, pts, ch, width=2):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            n = max(abs(x1 - x0), abs(y1 - y0))
            for i in range(n + 1):
                x = round(x0 + (x1 - x0) * i / max(1, n)); y = round(y0 + (y1 - y0) * i / max(1, n))
                self.fill(L, x, y, x + width - 1, y + width - 1, ch)
    def obj(self, x, y, ch, force=False):
        if 0 <= x < self.w and 0 <= y < self.h and (force or (self.o[y][x] == ' ' and self.g[y][x] == '.' and not self.near(x, y, 1))):
            self.o[y][x] = ch
    def near(self, x, y, d=2):
        for e in self.e:
            if 'x' not in e: continue
            ex, ey = e['x'], e['y']; fw = e.get('fw', 1); fh = e.get('fh', 1)
            if ex - d <= x <= ex + fw - 1 + d and ey - fh + 1 - d <= y <= ey + d: return True
        return False
    def border(self, kinds, depth=2, gaps=()):
        for y in range(self.h):
            for x in range(self.w):
                d = min(x, y, self.w - 1 - x, self.h - 1 - y)
                if d >= depth or any(a <= x <= c and b <= y <= dd for (a, b, c, dd) in gaps): continue
                self.o[y][x] = kinds[self.r.randrange(len(kinds))] if (d == 0 or (x + y) % 2 == d % 2) else '#'
    def scatter(self, ch, n, area=None):
        x0, y0, x1, y1 = area or (2, 2, self.w - 3, self.h - 3)
        for _ in range(n * 6):
            if n <= 0: break
            x, y = self.r.randint(x0, x1), self.r.randint(y0, y1)
            if self.o[y][x] == ' ' and self.g[y][x] == '.' and not self.near(x, y):
                self.o[y][x] = ch; n -= 1
    def clear(self, x0, y0, x1, y1): self.fill('o', x0, y0, x1, y1, ' ')
    def ent(self, **kw): self.e.append(kw); return kw
    def out(self):
        return {'name': self.name, 'w': self.w, 'h': self.h, 'music': self.music, 'theme': self.theme, 'tint': list(self.tint), 'dark': self.dark,
                'ground': [''.join(r) for r in self.g], 'objects': [''.join(r) for r in self.o], 'entities': self.e}

def town():
    m = Map('town', '해솔성', 48, 40, 'town', tint=(1.0, 0.97, 0.92), seed=3)
    # 성벽 (동문·남문은 비움)
    for x in range(m.w):
        for y in (0, 1): m.o[y][x] = 'H'
        for y in (m.h - 2, m.h - 1):
            if not 22 <= x <= 25: m.o[y][x] = 'H'
    for y in range(m.h):
        for x in (0, 1): m.o[y][x] = 'H'
        for x in (m.w - 2, m.w - 1):
            if not 18 <= y <= 21: m.o[y][x] = 'H'
    # 큰길: 동서·남북 돌길 + 마당
    m.fill('g', 2, 19, m.w - 1, 20, 'S'); m.fill('g', 23, 2, 24, m.h - 1, 'S')
    m.blob('g', 23.5, 19.5, 6, 4.5, 'S', 0.02)
    m.line('g', [(8, 12), (8, 19)], 'P'); m.line('g', [(36, 12), (36, 19)], 'P'); m.line('g', [(12, 28), (12, 20)], 'P'); m.line('g', [(35, 28), (35, 20)], 'P')
    m.ent(type='gate', x=46, y=21, fw=2, fh=4, face='east')
    m.ent(type='gate', x=22, y=39, fw=4, fh=2, face='south')
    # 건물: 주막·대장간·포목점·수련관·성주 댁
    m.ent(type='house', sprite='hanok_big', x=5, y=11, fw=6, fh=4, name='주막')
    m.ent(type='house', sprite='hanok', x=33, y=11, fw=5, fh=4, name='대장간')
    m.ent(type='house', sprite='hanok', x=9, y=27, fw=5, fh=4, name='포목점')
    m.ent(type='house', sprite='hanok_big', x=32, y=27, fw=6, fh=4, name='수련관')
    m.ent(type='house', sprite='hanok_big', x=20, y=7, fw=6, fh=4, name='성주 댁')
    m.ent(type='well', x=23, y=19)
    # 장터 가판
    for i, x in enumerate((14, 17, 28, 31)):
        m.ent(type='stall', sprite='stall_red' if i % 2 else 'stall_blue', x=x, y=17, fw=2, fh=1)
    # 사람들
    m.ent(type='npc', id='captain', x=44, y=18)
    m.ent(type='npc', id='hana', x=8, y=13)
    m.ent(type='npc', id='smith', x=36, y=13)
    m.ent(type='npc', id='tailor', x=12, y=29)
    m.ent(type='npc', id='elder', x=35, y=29)
    for i, j in enumerate(('m_warrior', 'm_rogue', 'm_mage', 'm_priest')):
        m.ent(type='npc', id=j, x=30 + i * 3, y=33)
    m.ent(type='npc', id='mujin', x=26, y=36)
    m.ent(type='sign', x=42, y=22, text='동문 → 솔내들 (산토끼·청설모·들개)')
    m.ent(type='sign', x=26, y=35, text='남문 → 안개숲 (너구리·불여우)')
    m.ent(type='portal', x=47, y=18, w=1, h=4, to='field', tx=2, ty=20)
    m.ent(type='portal', x=22, y=39, w=4, h=1, to='forest', tx=24, ty=2)
    m.ent(type='start', x=23, y=22)
    for (x, y) in ((19, 16), (28, 16), (19, 23), (28, 23), (5, 18), (42, 18), (21, 34), (26, 31)): m.obj(x, y, 'l', True)
    for (x, y, c) in ((11, 12, 'j'), (12, 12, 'J'), (32, 12, 'c'), (31, 12, 'c'), (14, 28, 'j'), (39, 28, 'J'), (4, 12, 'c')): m.obj(x, y, c, True)
    m.fill('o', 2, 33, 18, 33, 'f'); m.obj(2, 33, 'F', True); m.obj(18, 33, 'F', True)
    m.fill('o', 3, 35, 17, 37, 'C')
    for x in range(3, 46, 3):
        if m.o[3][x] == ' ': m.obj(x, 3, 'T' if x % 2 else 'M', True)
    m.scatter('t', 10, (3, 3, 44, 36)); m.scatter('b', 10, (3, 3, 44, 36)); m.scatter('B', 4)
    return m

def field():
    m = Map('field', '솔내들', 54, 42, 'field', seed=7)
    m.line('g', [(0, 20), (12, 20), (20, 14), (34, 14), (44, 20), (53, 20)], 'P', 2)
    m.line('g', [(20, 14), (22, 4)], 'P', 2); m.line('g', [(34, 14), (36, 34)], 'P', 2)
    # 개울과 다리
    for y in range(m.h):
        x = 27 + int(3 * __import__('math').sin(y * 0.3))
        m.fill('g', x, y, x + 2, y, 'W')
    for y in (14, 15):
        for x in range(22, 34):
            if m.g[y][x] == 'W': m.g[y][x] = 'D'
    for y in (34, 35):
        for x in range(22, 34):
            if m.g[y][x] == 'W': m.g[y][x] = 'D'
    m.border('NTtN', 2, gaps=[(0, 19, 1, 22)])
    m.ent(type='portal', x=0, y=19, w=1, h=4, to='town', tx=45, ty=20)
    m.ent(type='sign', x=4, y=18, text='← 해솔성 동문')
    # 밭과 울타리 (서남쪽)
    m.fill('o', 4, 28, 14, 28, 'f'); m.fill('o', 4, 36, 14, 36, 'f')
    m.fill('o', 5, 30, 13, 34, 'C')
    m.ent(type='spawn', mon='rabbit', area=[3, 22, 20, 38], n=8)
    m.ent(type='spawn', mon='squirrel', area=[36, 22, 50, 38], n=7)
    m.ent(type='spawn', mon='dog', area=[30, 3, 50, 12], n=7)
    m.ent(type='spawn', mon='rabbit', area=[6, 4, 18, 14], n=4)
    m.scatter('T', 16, (32, 22, 51, 39)); m.scatter('t', 10); m.scatter('M', 6); m.scatter('r', 10); m.scatter('b', 14); m.scatter('B', 5)
    return m

def forest():
    m = Map('forest', '안개숲', 54, 44, 'forest', theme='forest', tint=(0.86, 0.92, 0.9), seed=11)
    m.line('g', [(24, 0), (24, 10), (14, 20), (20, 32), (36, 34), (48, 26), (53, 26)], 'P', 2)
    m.line('g', [(24, 10), (40, 12), (44, 20)], 'P', 2)
    m.blob('g', 12, 36, 6, 4, 'W', 0.1)
    m.border('KKNt', 3, gaps=[(23, 0, 26, 2), (51, 25, 53, 28)])
    m.ent(type='portal', x=23, y=0, w=4, h=1, to='town', tx=23, ty=37)
    m.ent(type='portal', x=53, y=25, w=1, h=4, to='cave1', tx=2, ty=16)
    m.ent(type='sign', x=49, y=24, text='→ 멧쥐굴 (위험!)')
    m.ent(type='npc', id='woodcutter', x=40, y=14)
    m.ent(type='spawn', mon='raccoon', area=[4, 4, 22, 18], n=8)
    m.ent(type='spawn', mon='fox', area=[26, 18, 48, 40], n=9)
    m.ent(type='spawn', mon='raccoon', area=[30, 4, 48, 12], n=4)
    for _ in range(140):
        x, y = m.r.randint(3, m.w - 4), m.r.randint(3, m.h - 4)
        if m.g[y][x] == '.' and m.o[y][x] == ' ' and not m.near(x, y) and (x + y) % 2 == 0: m.o[y][x] = m.r.choice('KKNt')
    m.scatter('b', 20); m.scatter('r', 8)
    return m

def cave(key, name, seed, rooms, links, exits):
    m = Map(key, name, 44, 34, 'cave', theme='cave', tint=(0.62, 0.6, 0.72), seed=seed, dark=True)
    m.fill('o', 0, 0, m.w - 1, m.h - 1, 'X')
    for (cx, cy, rx, ry) in rooms:
        m.blob('o', cx, cy, rx, ry, ' ', 0.12)
    for (a, b) in links:
        (x0, y0), (x1, y1) = rooms[a][:2], rooms[b][:2]
        m.line('o', [(x0, y0), (x1, y0), (x1, y1)], ' ', 3)
    for e in exits: m.ent(**e); m.line('o', [(e['x'], e['y']), (e.get('cx', e['x']), e.get('cy', e['y']))], ' ', 3)
    # 벽 칸에만 굴벽, 바닥에는 가끔 돌·횃불
    return m

def cave1():
    rooms = [(5, 16, 4, 3), (15, 10, 5, 4), (16, 24, 5, 4), (28, 16, 6, 5), (38, 8, 4, 4), (38, 26, 4, 4)]
    m = cave('cave1', '멧쥐굴 1층', 21, rooms, [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (3, 5)],
             [dict(type='portal', x=0, y=15, w=1, h=3, to='forest', tx=51, ty=26, cx=4, cy=16),
              dict(type='portal', x=40, y=26, w=2, h=2, to='cave2', tx=4, ty=26, kind='down')])
    m.ent(type='spawn', mon='rat', area=[10, 6, 34, 28], n=10)
    m.ent(type='spawn', mon='bat', area=[24, 4, 42, 30], n=6)
    for (x, y) in ((6, 14), (15, 7), (28, 12), (38, 6), (38, 24), (16, 21)): m.ent(type='torch', x=x, y=y)
    return m

def cave2():
    rooms = [(6, 26, 4, 3), (16, 20, 5, 4), (12, 9, 5, 4), (28, 24, 5, 4), (30, 9, 8, 5), (40, 20, 3, 4)]
    m = cave('cave2', '멧쥐굴 2층', 23, rooms, [(0, 1), (1, 2), (1, 3), (3, 4), (2, 4), (3, 5)],
             [dict(type='portal', x=3, y=27, w=2, h=2, to='cave1', tx=39, ty=24, kind='up'),
              dict(type='portal', x=30, y=0, w=3, h=1, to='camp', tx=20, ty=31, need='done:q_cave', cx=31, cy=6)])
    m.ent(type='boss', mon='ratking', x=30, y=10)
    m.ent(type='spawn', mon='rat', area=[10, 14, 34, 30], n=10)
    m.ent(type='spawn', mon='bat', area=[8, 4, 22, 14], n=6)
    for (x, y) in ((6, 23), (16, 17), (12, 6), (24, 7), (36, 7), (28, 21)): m.ent(type='torch', x=x, y=y)
    return m

def camp():
    m = Map('camp', '흑풍단 소굴', 42, 34, 'boss', tint=(0.8, 0.74, 0.74), seed=31)
    m.blob('g', 21, 15, 15, 11, 'P', 0.05)
    m.border('NNKt', 3, gaps=[(19, 31, 22, 33)])
    for x in range(6, 37):
        if not 18 <= x <= 23: m.o[27][x] = 'k'
    m.ent(type='portal', x=19, y=33, w=4, h=1, to='cave2', tx=31, ty=2)
    for (x, y) in ((10, 10), (30, 10), (12, 20), (30, 21)): m.ent(type='tent', x=x, y=y, fw=2, fh=1)
    for (x, y) in ((16, 15), (26, 15), (21, 22)): m.ent(type='campfire', x=x, y=y)
    m.ent(type='npc', id='captive', x=8, y=22)
    m.ent(type='npc', id='mujin', x=24, y=29)
    m.ent(type='spawn', mon='bandit', area=[8, 6, 34, 25], n=9)
    m.ent(type='boss', mon='chief', x=21, y=7)
    m.scatter('c', 6, (6, 5, 36, 25)); m.scatter('j', 4, (6, 5, 36, 25))
    return m

if __name__ == '__main__':
    data = {mm.key: mm.out() for mm in (town(), field(), forest(), cave1(), cave2(), camp())}
    p = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'maps.json')
    json.dump(data, open(p, 'w'), ensure_ascii=False, indent=1)
    for k, v in data.items():
        print(k, v['w'], v['h'])
        if k in ('town', 'cave2'):
            print('\n'.join(''.join(o if o != ' ' else g for g, o in zip(a, b)) for a, b in zip(v['ground'], v['objects'])))
