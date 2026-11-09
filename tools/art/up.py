"""16픽셀 기준으로 그린 소품을 32픽셀 세상에 맞게 키운다: Scale2x(모서리 다듬기) → 테두리를 1픽셀로 다시 → 잔무늬."""
import random
from common import *

def scale2x(im):
    w, h = im.size; src = im.load(); out = img(w * 2, h * 2); o = out.load()
    def g(x, y):
        x = min(w - 1, max(0, x)); y = min(h - 1, max(0, y)); return src[x, y]
    for y in range(h):
        for x in range(w):
            P = g(x, y); A = g(x, y - 1); B = g(x + 1, y); C = g(x - 1, y); D = g(x, y + 1)
            e0 = A if (C == A and C != D and A != B) else P
            e1 = B if (A == B and A != C and B != D) else P
            e2 = C if (D == C and D != B and C != A) else P
            e3 = D if (B == D and B != A and D != C) else P
            o[2 * x, 2 * y] = e0; o[2 * x + 1, 2 * y] = e1; o[2 * x, 2 * y + 1] = e2; o[2 * x + 1, 2 * y + 1] = e3
    return out

def thin_outline(im, ink=('ink', 'ink2', 'v0', 'n0')):
    """두꺼워진 테두리를 지우고 1픽셀로 다시 두른다."""
    out = im.copy(); px = out.load()
    inks = {PAL[k][:3] for k in ink}
    col = {}
    for y in range(out.height):
        for x in range(out.width):
            c = px[x, y]
            if c[3] and c[:3] in inks:
                col[(x, y)] = c
                px[x, y] = (0, 0, 0, 0)
    # 테두리 자리를 안쪽 색으로 채운 뒤(안쪽 선 유지), 바깥 한 줄만 다시 그림
    res = out.copy(); rp = res.load()
    for (x, y), c in col.items():
        inside = 0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            xx, yy = x + dx, y + dy
            if 0 <= xx < out.width and 0 <= yy < out.height and px[xx, yy][3] and (xx, yy) not in col: inside += 1
        if inside >= 2:
            rp[x, y] = c  # 안쪽 선(부품 사이)은 남김
    return outline(res, 'ink')

def detail(im, seed=1, amount=0.06):
    """같은 색 넓은 곳에 한 픽셀 잔무늬 (밝게/어둡게)."""
    r = random.Random(seed); out = im.copy(); px = out.load()
    ramp = {}
    for ch in ('g', 'b', 's', 'r', 'p', 'd', 'red', 'o', 'n', 'v'):
        keys = [k for k in PAL if k.startswith(ch) and k[len(ch):].isdigit()]
        keys.sort(key=lambda k: int(k[len(ch):]))
        for i, k in enumerate(keys):
            ramp[PAL[k][:3]] = (PAL[keys[i - 1]] if i > 0 else None, PAL[keys[i + 1]] if i + 1 < len(keys) else None)
    for y in range(1, out.height - 1):
        for x in range(1, out.width - 1):
            c = px[x, y]
            if c[3] and c[:3] in ramp and r.random() < amount:
                dark, light = ramp[c[:3]]
                pick = dark if r.random() < 0.55 else light
                if pick: px[x, y] = pick
    return out

def big(im, seed=1, amount=0.05):
    return detail(thin_outline(scale2x(im)), seed, amount)
