"""효과음·배경음을 코드로 합성해 assets/sfx, assets/music 에 wav로 쓴다.
python3 tools/sound/gen.py   (외부 음원 없음, numpy 없이 표준 라이브러리만)
"""
import math, os, random, struct, wave, array

SR = 22050
ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')

def write(path, data, sr=SR):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    peak = max(1e-6, max(abs(x) for x in data))
    g = 0.9 / peak if peak > 0.9 else 1.0
    a = array.array('h', (int(max(-1, min(1, x * g)) * 32000) for x in data))
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(a.tobytes())

def env(t, a, d, s, r, dur):
    if t < a: return t / a
    if t < a + d: return 1 - (1 - s) * (t - a) / d
    if t < dur - r: return s
    return max(0, s * (dur - t) / r)

def osc(kind, ph):
    p = ph % 1.0
    if kind == 'sin': return math.sin(2 * math.pi * p)
    if kind == 'tri': return 4 * abs(p - 0.5) - 1
    if kind == 'sq': return 1 if p < 0.5 else -1
    if kind == 'pul': return 1 if p < 0.25 else -1
    if kind == 'saw': return 2 * p - 1
    return 0

def tone(dur, f0, f1=None, kind='sq', vol=0.5, a=0.005, d=0.05, s=0.6, r=0.05, vib=0, noise=0):
    n = int(dur * SR); out = []; ph = 0; f1 = f1 or f0; rnd = random.Random(int(f0))
    for i in range(n):
        t = i / SR; k = t / dur
        f = f0 * (f1 / f0) ** k
        if vib: f *= 1 + 0.01 * vib * math.sin(2 * math.pi * 6 * t)
        ph += f / SR
        v = osc(kind, ph) * (1 - noise) + (rnd.random() * 2 - 1) * noise
        out.append(v * vol * env(t, a, d, s, r, dur))
    return out

def noise(dur, vol=0.5, lp=0.5, a=0.002, r=0.1, f_end=None):
    n = int(dur * SR); out = []; y = 0; rnd = random.Random(7)
    for i in range(n):
        t = i / SR
        k = lp if f_end is None else lp + (f_end - lp) * t / dur
        y += (rnd.random() * 2 - 1 - y) * k
        out.append(y * vol * env(t, a, 0.01, 1, r, dur))
    return out

def mix(*parts, offs=None):
    offs = offs or [0] * len(parts)
    n = max(int(o * SR) + len(p) for p, o in zip(parts, offs))
    out = [0.0] * n
    for p, o in zip(parts, offs):
        s = int(o * SR)
        for i, v in enumerate(p): out[s + i] += v
    return out

def seq(notes, kind='sq', vol=0.4, gap=0.0):
    out = []
    for (f, d) in notes:
        out += tone(d, f, kind=kind, vol=vol, r=min(0.05, d * 0.5)) if f else [0.0] * int(d * SR)
    return out

def N(name):
    """음 이름 → 주파수. 예: 'A4', 'C#5'"""
    names = {'C': -9, 'D': -7, 'E': -5, 'F': -4, 'G': -2, 'A': 0, 'B': 2}
    n = names[name[0]]; i = 1
    if name[i] == '#': n += 1; i += 1
    elif name[i] == 'b': n -= 1; i += 1
    o = int(name[i:])
    return 440 * 2 ** ((n + (o - 4) * 12) / 12)

def sfx():
    S = lambda n, d: write(os.path.join(ROOT, 'sfx', n + '.wav'), d)
    S('swing', noise(0.14, 0.5, 0.08, r=0.1, f_end=0.5))
    S('hit', mix(tone(0.09, 220, 80, 'sq', 0.5, r=0.06), noise(0.08, 0.6, 0.6, r=0.06)))
    S('enemy_die', mix(tone(0.28, 600, 90, 'sq', 0.35, r=0.2), noise(0.3, 0.4, 0.3, r=0.25), offs=[0, 0.05]))
    S('coin', mix(tone(0.06, N('B5'), kind='sq', vol=0.3), tone(0.16, N('E6'), kind='sq', vol=0.3, r=0.12), offs=[0, 0.06]))
    S('hurt', mix(tone(0.25, 330, 110, 'saw', 0.5, r=0.15), noise(0.12, 0.3, 0.5)))
    S('roll', noise(0.18, 0.35, 0.05, r=0.12, f_end=0.15))
    S('talk', tone(0.035, 660, 620, 'tri', 0.35, r=0.02))
    S('chest', mix(*[tone(0.12, N(n), kind='pul', vol=0.3, r=0.08) for n in ('C5', 'E5', 'G5', 'C6')], offs=[0, 0.08, 0.16, 0.24]))
    S('shard', mix(*[tone(0.5, N(n), kind='tri', vol=0.35, r=0.4, vib=2) for n in ('E5', 'A5', 'C#6', 'E6', 'A6')], offs=[0, 0.1, 0.2, 0.3, 0.42]))
    S('roar', mix(tone(0.9, 140, 60, 'saw', 0.5, a=0.05, r=0.4, vib=6, noise=0.3), noise(0.9, 0.4, 0.15, a=0.05, r=0.5)))
    S('stomp', mix(tone(0.35, 90, 35, 'sin', 0.9, r=0.3), noise(0.3, 0.6, 0.2, r=0.25)))
    S('warp', tone(0.35, 300, 900, 'tri', 0.35, r=0.2))
    S('select', tone(0.07, 880, kind='sq', vol=0.25, r=0.04))
    S('heal', mix(*[tone(0.15, N(n), kind='tri', vol=0.3, r=0.1) for n in ('G5', 'B5', 'D6')], offs=[0, 0.07, 0.14]))
    S('cut', noise(0.1, 0.4, 0.5, r=0.08, f_end=0.2))
    S('fire', mix(tone(0.2, 500, 900, 'tri', 0.25, r=0.15), noise(0.2, 0.2, 0.3)))
    S('hop', tone(0.08, 200, 400, 'sq', 0.2, r=0.05))

# ── 배경음: 5음계(궁·상·각·치·우) 위주의 짧은 반복곡 ──
def song(bpm, bars, melody, bass, drums, lead='pul', pad=None):
    beat = 60 / bpm; total = bars * 4 * beat
    n = int(total * SR); out = [0.0] * n
    def place(part, at):
        s = int(at * SR)
        for i, v in enumerate(part):
            if s + i < n: out[s + i] += v
            else: out[(s + i) % n] += v  # 반복 이음매가 자연스럽게
    t = 0
    for (f, d) in melody:
        if f: place(tone(d * beat * 0.95, N(f), kind=lead, vol=0.22, a=0.01, d=0.08, s=0.55, r=0.08, vib=1.5), t)
        t += d * beat
    t = 0
    for (f, d) in bass:
        if f: place(tone(d * beat * 0.9, N(f), kind='tri', vol=0.35, r=0.05), t)
        t += d * beat
    if pad:
        t = 0
        for (fs, d) in pad:
            for f in fs: place(tone(d * beat, N(f), kind='sin', vol=0.06, a=0.3, d=0.2, s=0.8, r=0.4), t)
            t += d * beat
    steps = int(total / (beat / 2))
    for i in range(steps):
        ch = drums[i % len(drums)]
        at = i * beat / 2
        if ch == 'k': place(tone(0.12, 120, 45, 'sin', 0.5, r=0.08), at)
        elif ch == 's': place(noise(0.1, 0.22, 0.5, r=0.08), at)
        elif ch == 'h': place(noise(0.03, 0.08, 0.9, r=0.02), at)
    return out

def notes(txt):
    out = []
    for tok in txt.split():
        n, d = tok.split(':')
        out.append((None if n == '-' else n, float(d)))
    return out

def brass(dur, f, vol=0.2):
    """두 겹으로 살짝 어긋난 톱니파 + 사각파: 신스 브라스 느낌"""
    a = tone(dur, f, kind='saw', vol=vol * 0.6, a=0.03, d=0.12, s=0.7, r=0.08, vib=2)
    b = tone(dur, f * 1.006, kind='sq', vol=vol * 0.35, a=0.03, d=0.12, s=0.6, r=0.08, vib=2)
    return [x + y for x, y in zip(a, b)]

def song2(bpm, bars, mel, chords, drums, lead='brass', bass_pat='8', arp=True, vol=1.0):
    beat = 60 / bpm; total = bars * 4 * beat
    n = int(total * SR); out = [0.0] * n
    def place(part, at):
        s0 = int(at * SR)
        for k, v in enumerate(part):
            out[(s0 + k) % n] += v * vol
    t = 0
    seq_mel = []
    tot = sum(d for _, d in mel)
    while sum(d for _, d in seq_mel) + tot <= bars * 4 + 0.01: seq_mel += mel
    for (f, d) in seq_mel:
        if f:
            dur = d * beat * 0.92
            place(brass(dur, N(f)) if lead == 'brass' else tone(dur, N(f), kind=lead, vol=0.2, a=0.01, d=0.08, s=0.6, r=0.06, vib=1.5), t)
        t += d * beat
    # 화음: 마디마다 (근음, 3음, 5음)
    for bi in range(bars):
        ch = chords[bi % len(chords)]
        at = bi * 4 * beat
        root = ch[0]
        # 베이스: 8분음 펌핑 (근음·옥타브)
        steps = 8 if bass_pat == '8' else 4
        for k in range(steps):
            f = N(root) * (2 if (k % 4 == 3 and bass_pat == '8') else 1)
            place(tone(beat * (4 / steps) * 0.85, f, kind='tri', vol=0.33, r=0.03), at + k * beat * 4 / steps)
            place(tone(beat * (4 / steps) * 0.5, f, kind='pul', vol=0.06, r=0.02), at + k * beat * 4 / steps)
        # 패드 + 아르페지오
        for f in ch[1:]:
            place(tone(4 * beat, N(f), kind='sin', vol=0.05, a=0.2, d=0.3, s=0.8, r=0.3), at)
        if arp:
            seq_ = [ch[1], ch[2], ch[3] if len(ch) > 3 else ch[1], ch[2]] * 4
            for k, f in enumerate(seq_):
                place(tone(beat * 0.22, N(f) * 2, kind='pul', vol=0.045, r=0.03), at + k * beat / 4)
    steps = int(total / (beat / 2))
    for k in range(steps):
        ch = drums[k % len(drums)]; at = k * beat / 2
        if ch in 'kK': place(tone(0.14, 130, 42, 'sin', 0.6, r=0.1), at)
        if ch in 'sK': place(mix(noise(0.13, 0.28, 0.6, r=0.1), tone(0.08, 220, 140, 'tri', 0.15)), at)
        if ch in 'h': place(noise(0.03, 0.08, 0.95, r=0.02), at)
        if ch == 'o': place(noise(0.2, 0.08, 0.9, r=0.18), at)
        if ch == 'c': place(noise(0.6, 0.12, 0.85, r=0.55), at)
    return out

def guitar(dur, root, vol=0.12):
    """찌그러뜨린 파워 코드 (근음 + 5도 + 옥타브)"""
    parts = [tone(dur, root * k, kind='saw', vol=vol, a=0.005, d=0.05, s=0.8, r=0.03) for k in (1, 1.498, 2)]
    out = []
    for vals in zip(*parts):
        v = sum(vals) * 2.2
        out.append(math.tanh(v) * vol * 1.6)
    return out

def theme(bpm, sections, vol=1.0):
    """여러 마디 묶음(절·후렴)을 이어 붙이는 주제곡. section = (마디 수, 멜로디, 화음들, 드럼, 기타 여부, 심벌)"""
    beat = 60 / bpm
    total_bars = sum(s[0] for s in sections)
    n = int(total_bars * 4 * beat * SR); out = [0.0] * n
    def place(part, at):
        s0 = int(at * SR)
        for k, v in enumerate(part): out[(s0 + k) % n] += v * vol
    bar0 = 0
    for (bars, mel, chords, drums, gtr, crash) in sections:
        t0 = bar0 * 4 * beat; t = t0
        for (f, d) in mel:
            if f: place(brass(d * beat * 0.94, N(f), 0.21), t)
            t += d * beat
        for bi in range(bars):
            ch = chords[bi % len(chords)]; at = t0 + bi * 4 * beat
            for k in range(8):
                f = N(ch[0])
                place(tone(beat * 0.45, f, kind='tri', vol=0.34, r=0.03), at + k * beat / 2)
                if gtr: place(guitar(beat * 0.42, f * 2, 0.07), at + k * beat / 2)
            for f in ch[1:]:
                place(tone(4 * beat, N(f), kind='sin', vol=0.045, a=0.25, d=0.3, s=0.8, r=0.3), at)
            for k, f in enumerate([ch[1], ch[2], ch[3], ch[2]] * 4):
                place(tone(beat * 0.2, N(f) * 2, kind='pul', vol=0.035 if gtr else 0.05, r=0.03), at + k * beat / 4)
            if crash and bi == 0: place(noise(1.2, 0.14, 0.85, r=1.0), at)
        steps = bars * 8
        for k in range(steps):
            ch_ = drums[k % len(drums)]; at = t0 + k * beat / 2
            if ch_ in 'kK': place(tone(0.14, 130, 42, 'sin', 0.6, r=0.1), at)
            if ch_ in 'sK': place(mix(noise(0.13, 0.28, 0.6, r=0.1), tone(0.08, 220, 140, 'tri', 0.15)), at)
            if ch_ in 'hs.' and ch_ != '.': pass
            if ch_ == 'h' or ch_ in 'ks': place(noise(0.03, 0.07, 0.95, r=0.02), at + (beat / 4 if ch_ != 'h' else 0))
        bar0 += bars
    return out

def music():
    M = lambda n, d: write(os.path.join(ROOT, 'music', n + '.wav'), d)
    # 처음 화면: 힘차게 펼쳐지는 모험의 시작 (D장조, 138)
    mel = notes("A4:1 D5:.5 E5:.5 F#5:1.5 E5:.5 D5:1 E5:1 F#5:1 A5:1 B5:1.5 A5:.5 F#5:2 "
                "G5:1 F#5:.5 E5:.5 D5:1 B4:1 D5:1 E5:1 A4:2 "
                "A4:1 D5:.5 E5:.5 F#5:1.5 E5:.5 D5:1 E5:1 F#5:1 A5:1 D6:1.5 C#6:.5 B5:2 "
                "G5:1 A5:.5 B5:.5 A5:1 F#5:1 E5:1 F#5:.5 E5:.5 D5:4")
    ch = [('D3', 'D4', 'F#4', 'A4'), ('B2', 'B3', 'D4', 'F#4'), ('G2', 'G3', 'B3', 'D4'), ('A2', 'A3', 'C#4', 'E4')]
    # 메인 테마: 설렘과 아련함이 섞인 90년대 애니풍 록 발라드 (D장조, 132). 직접 새로 쓴 선율.
    IV, V, iii, vi = ('G2', 'G3', 'B3', 'D4'), ('A2', 'A3', 'C#4', 'E4'), ('F#2', 'F#3', 'A3', 'C#4'), ('B2', 'B3', 'D4', 'F#4')
    I = ('D3', 'D4', 'F#4', 'A4')
    verse = notes("F#4:1 A4:.5 B4:.5 A4:1 F#4:.5 E4:.5 D4:1 E4:.5 F#4:.5 A4:2 "
                  "B4:1 A4:.5 F#4:.5 E4:1 D4:.5 E4:.5 F#4:3 -:1 "
                  "F#4:1 A4:.5 B4:.5 D5:1 B4:.5 A4:.5 B4:1 C#5:.5 D5:.5 E5:2 "
                  "D5:.5 C#5:.5 B4:.5 A4:.5 B4:1 C#5:1 A4:4")
    pre = notes("B4:.5 C#5:.5 D5:1 C#5:.5 B4:.5 A4:1 F#4:1 G4:.5 A4:.5 B4:1 C#5:1 "
                "D5:.5 E5:.5 F#5:1 E5:.5 D5:.5 C#5:1.5 A4:.5 B4:1 C#5:2")
    chorus = notes("D5:1 E5:.5 F#5:.5 A5:1.5 F#5:.5 G5:1 F#5:.5 E5:.5 D5:1 E5:1 "
                   "F#5:1 E5:.5 D5:.5 C#5:1 A4:1 B4:1.5 C#5:.5 D5:2 "
                   "D5:1 E5:.5 F#5:.5 A5:1.5 B5:.5 A5:1 F#5:.5 E5:.5 F#5:1 A5:1 "
                   "B5:1 A5:.5 F#5:.5 E5:1 F#5:.5 E5:.5 D5:4")
    M('title', theme(132, [
        (8, verse, [IV, V, iii, vi], 'k.h.s.h.k.k.s.h.', False, True),
        (4, pre, [IV, V, iii, ('A2', 'A3', 'C#4', 'E4')], 'k.hsk.hsk.hsKsKs', True, False),
        (8, chorus, [IV, V, iii, vi, IV, V, I, I], 'k.hsk.hsk.hsk.hs', True, True)]))
    # 마을: 밝고 경쾌한 장터 (G장조, 120)
    mel = notes("D5:.5 G5:.5 A5:.5 B5:1 A5:.5 G5:.5 E5:.5 D5:1 E5:.5 G5:.5 A5:1 G5:.5 E5:.5 D5:2 "
                "B4:.5 D5:.5 E5:.5 G5:1 E5:.5 D5:.5 B4:.5 A4:1 B4:.5 D5:.5 E5:1 D5:.5 B4:.5 G4:2 "
                "D5:.5 G5:.5 A5:.5 B5:1 D6:.5 B5:.5 A5:.5 G5:1 A5:.5 B5:.5 A5:1 G5:.5 E5:.5 D5:2 "
                "E5:1 G5:.5 E5:.5 D5:1 B4:1 A4:.5 B4:.5 D5:1 G4:2")
    ch = [('G2', 'G3', 'B3', 'D4'), ('E2', 'E3', 'G3', 'B3'), ('C3', 'C4', 'E4', 'G4'), ('D3', 'D4', 'F#4', 'A4')]
    M('town', song2(120, 16, mel, ch, 'k.h.s.h.k.hks.h.', lead='sq', vol=0.9))
    # 들판: 달리는 모험 (A장조, 150)
    mel = notes("E5:.5 A5:.5 B5:.5 C#6:1 B5:.5 A5:.5 B5:.5 E5:1.5 F#5:.5 G#5:.5 A5:.5 B5:2 "
                "A5:.5 G#5:.5 F#5:.5 E5:1 C#5:.5 E5:.5 F#5:.5 E5:1 B4:.5 C#5:.5 E5:.5 A4:2 "
                "E5:.5 A5:.5 B5:.5 C#6:1 E6:.5 C#6:.5 B5:.5 A5:1.5 B5:.5 C#6:.5 D6:.5 E6:2 "
                "D6:.5 C#6:.5 B5:.5 A5:1 F#5:.5 G#5:.5 B5:.5 A5:4")
    ch = [('A2', 'A3', 'C#4', 'E4'), ('F#2', 'F#3', 'A3', 'C#4'), ('D3', 'D4', 'F#4', 'A4'), ('E3', 'E4', 'G#4', 'B4')]
    M('field', song2(150, 16, mel, ch, 'k.hsk.hsk.hsk.ss'))
    # 숲: 신비롭지만 씩씩하게 (E 단조 → G, 108)
    mel = notes("E5:1 G5:.5 A5:.5 B5:1.5 A5:.5 G5:1 F#5:1 E5:2 D5:1 E5:.5 F#5:.5 G5:1.5 F#5:.5 E5:1 D5:1 B4:2 "
                "E5:1 G5:.5 A5:.5 B5:1.5 D6:.5 C6:1 B5:1 A5:2 G5:1 A5:.5 B5:.5 A5:1 G5:.5 F#5:.5 E5:4")
    ch = [('E2', 'E3', 'G3', 'B3'), ('C3', 'C4', 'E4', 'G4'), ('G2', 'G3', 'B3', 'D4'), ('D3', 'D4', 'F#4', 'A4')]
    M('forest', song2(108, 16, mel, ch, 'k...h.s.k.k.h.s.', lead='tri', vol=0.95))
    # 굴: 긴장감 있는 어두운 행진 (A 단조, 112)
    mel = notes("A4:1 C5:.5 B4:.5 A4:1 E5:1 D5:.5 C5:.5 B4:1 G#4:2 A4:1 C5:.5 D5:.5 E5:1 F5:1 E5:.5 D5:.5 C5:1 B4:2 "
                "A4:1 C5:.5 B4:.5 A4:1 E5:1 F5:.5 G5:.5 A5:1 G#5:2 A5:1 G5:.5 F5:.5 E5:1 D5:1 C5:.5 B4:.5 A4:4")
    ch = [('A2', 'A3', 'C4', 'E4'), ('F2', 'F3', 'A3', 'C4'), ('D3', 'D4', 'F4', 'A4'), ('E2', 'E3', 'G#3', 'B3')]
    M('cave', song2(112, 16, mel, ch, 'k..hs..hk.k.s..h', arp=False, vol=0.9))
    # 대왕전: 몰아치는 결전 (D 단조, 160)
    mel = notes("D5:.5 D5:.5 F5:.5 D5:.5 G5:.5 F5:.5 D5:.5 C5:.5 A4:1 C5:.5 D5:.5 F5:1 E5:1 "
                "D5:.5 D5:.5 F5:.5 D5:.5 A5:.5 G5:.5 F5:.5 E5:.5 F5:1 G5:.5 A5:.5 C6:1 A5:1 "
                "Bb5:1 A5:.5 G5:.5 A5:1 F5:1 G5:1 F5:.5 E5:.5 F5:1 D5:1 "
                "Bb4:.5 C5:.5 D5:.5 F5:.5 E5:.5 F5:.5 G5:.5 A5:.5 D6:2 C#6:2")
    ch = [('D3', 'D4', 'F4', 'A4'), ('Bb2', 'Bb3', 'D4', 'F4'), ('C3', 'C4', 'E4', 'G4'), ('A2', 'A3', 'C#4', 'E4')]
    M('boss', song2(160, 16, mel, ch, 'kskskkskkskskKsc'))

if __name__ == '__main__':
    sfx(); music(); print('ok')
