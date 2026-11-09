"""assets/sprites/*.png 를 전부 다시 만든다: python3 tools/art/gen.py"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from common import *
import tiles, objects as O, doll as D, beasts as B, props as P
from up import big

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
OUT = os.path.join(ROOT, 'assets', 'sprites')
os.makedirs(OUT, exist_ok=True)

def save(name, im):
    im.save(os.path.join(OUT, name + '.png'))

def strip(frames):
    w = max(f.width for f in frames); h = max(f.height for f in frames)
    s = img(w * len(frames), h)
    for i, f in enumerate(frames): s.alpha_composite(f, (i * w + (w - f.width) // 2, h - f.height))
    return s

def remap(im, m):
    mm = {PAL[a][:3]: PAL[b] for a, b in m.items()}
    out = im.copy(); px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            c = px[x, y]
            if c[3] and c[:3] in mm: px[x, y] = mm[c[:3]][:3] + (c[3],)
    return out

CAVE = {'g0': 'ink', 'g1': 'ink2', 'g2': 's0', 'g3': 's0', 'g4': 's1', 'g5': 's2',
        'd1': 'b0', 'd2': 'd0', 'd3': 'd1', 'd4': 'd2', 'w1': 'w0', 'w2': 'w1', 'w3': 'w2'}
FOREST = {'g2': 'g1', 'g3': 'g2', 'g4': 'g3', 'g5': 'g4'}

def main():
    t = tiles.build()
    save('tiles', t); save('tiles_cave', remap(t, CAVE)); save('tiles_forest', remap(t, FOREST))
    # 캐릭터 층
    for g in ('m', 'f'):
        save('body_' + g, D.body(g))
        for o in D.OUTFITS: save('cloth_%s_%s' % (o, g), D.cloth(o, g))
    for st in D.HAIRS:
        for hc in D.HAIR_COLORS: save('hair_%s_%s' % (st, hc), D.hair(st, hc))
    for w in ('sword', 'dagger', 'staff', 'bell', 'club'): save('weapon_' + w, D.weapon(w))
    # 얼굴 그림: 사람들 + 주인공 조합
    story = json.load(open(os.path.join(ROOT, 'data', 'story.json')))
    for nid, n in story['npcs'].items():
        p = n['portrait']
        save('portrait_' + nid, D.portrait(skin=tuple(p.get('skin', ('sk1', 'sk2', 'sk3'))), hair_c=tuple(p.get('hair', ('hr0', 'hr1', 'hr2'))),
             cloth_c=tuple(p.get('cloth', ('n1', 'n2', 'n3'))), style=p.get('style', 'short'), g=p.get('g', 'm'), beard=p.get('beard', False), age=p.get('age', 0)))
    for g in ('m', 'f'):
        for st in D.HAIRS:
            for hc, cols in D.HAIR_COLORS.items():
                save('portrait_p_%s_%s_%s' % (g, st, hc), D.portrait(hair_c=cols, cloth_c=('p0', 'p1', 'p2'), style=st, g=g))
    # 몬스터
    for k, v in B.build().items(): save(k, v)
    for (name, outfit, hs, hc, w) in (('mon_bandit', 'rogue', 'short', 'black', 'club'), ('mon_chief', 'warrior', 'long', 'ash', 'sword')):
        sh = D.body('m'); sh.alpha_composite(D.cloth(outfit, 'm')); sh.alpha_composite(D.hair(hs, hc))
        sh = remap(sh, {'red0': 'ink', 'red1': 'r0', 'red2': 'r1'}) if name == 'mon_chief' else sh
        sh.alpha_composite(D.weapon(w)); save(name, sh)
    # 소품 (16 기준 그림을 키움)
    for n, im in (('tree_round', O.tree(1)), ('tree_round2', O.tree(4)), ('tree_maple', O.tree(2, 'maple')), ('tree_pine', O.tree(3, 'pine')),
                  ('rock', O.rock(1)), ('rock_big', O.rock(2, True)), ('bush', O.bush(1)), ('bush_berry', O.bush(2, True)),
                  ('fence_h', O.fence('h')), ('fence_post', O.fence('post')), ('lantern', O.lantern()), ('well', O.well()), ('sign', O.sign()),
                  ('jar', O.jar(0)), ('jar_red', O.jar(1)), ('crate', O.crate()), ('hanok', O.hanok(72)), ('hanok_big', O.hanok(96, 2))):
        save(n, big(im, hash(n) % 97, 0.02 if n.startswith('hanok') else 0.05))
    save('bridge', big(O.bridge(), 3, 0.03))
    save('tree_dark', remap(big(O.tree(5), 5), FOREST | {'g1': 'g0'}))
    # 새 소품 (32 기준)
    save('wall', P.wall()); save('gate', P.gate()); save('stall_red', P.stall('red')); save('stall_blue', P.stall('blue'))
    save('tent', P.tent()); save('palisade', P.palisade()); save('crop', P.crop())
    save('campfire', strip([P.campfire(i) for i in range(4)])); save('torch', strip([P.torch(i) for i in range(3)]))
    for i in range(3): save('cave_rock%d' % i, P.cave_rock(i + 3))
    # 아이콘·효과·창
    for iid, kind in P.ITEM_ICON.items(): save('icon_' + iid, P.icon(kind))
    for sid in ('whirl', 'rush', 'roar', 'triple', 'star', 'shadow', 'fire', 'ice', 'thunder', 'heal', 'orb', 'guard'): save('skill_' + sid, P.skill_icon(sid))
    save('coin', strip([P.coin(i) for i in range(4)])); save('spark', strip([P.spark(i) for i in range(4)])); save('puff', strip([P.puff(i) for i in range(5)]))
    save('ui_box', P.ui_box()); save('ui_slot', P.ui_slot())
    print('ok', len([f for f in os.listdir(OUT) if f.endswith('.png')]), 'png')

if __name__ == '__main__':
    main()
