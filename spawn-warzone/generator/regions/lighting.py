"""Flush floor lights in the island's shadow so the covered area is not dark (and hostile mobs can't spawn):
simulates block light at feet level (y70) from every floor light already placed (sea lanterns, glowstone, lava under the
glass paths, open lava) and greedily adds flush glowstone until every shadowed floor cell has light >= min_light.
Light model: source in the floor (y69) gives 14 at feet above it, lava at y68 under glass gives 13, then -1 per block
(Manhattan) across open floor. Matches vanilla propagation on a flat open floor (glass does not dim light)."""
from collections import deque
from common import *

NAME = 'lighting'
FLOOR_OK = ('wood', 'grass', 'gray', 'moon', 'moon_dark', 'platform')


def build(G, BP, ctx):
    L = BP['lighting']; S = BP['surface']; need = L.get('min_light', 9)
    if not L.get('enabled', True):
        ctx.notes.append('lighting: off (user 2026-11-06: no glowstone)'); return
    shadow = set(ctx.island)
    cells = {c for c in shadow if ctx.surf.get(c) not in ('struct', 'rock', 'mound')}
    light = {}

    def spread(srcs):
        q = deque()
        for (x, z, lv) in srcs:
            if light.get((x, z), 0) < lv: light[(x, z)] = lv; q.append((x, z))
        while q:
            x, z = q.popleft(); lv = light[(x, z)] - 1
            if lv <= 0: continue
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, z + dz)
                if n in cells and light.get(n, 0) < lv: light[n] = lv; q.append(n)

    srcs = []
    for (x, z) in cells:
        b = G.get(x, S, z); b2 = G.get(x, S - 1, z)
        if b and b[0] in (GLOWSTONE, SEA_LANTERN): srcs.append((x, z, 14))
        elif b and b[0] == LAVA: srcs.append((x, z, 15))
        elif b2 and b2[0] == LAVA: srcs.append((x, z, 13))
    spread(srcs)
    n = 0
    sp = L['spacing']
    # 1) staggered lattice (max Manhattan distance sp/2 -> >= 15-1-sp/2 at feet), nudged onto a plain floor cell
    for (x, z) in sorted(cells):
        if not ((x % sp == 0 and z % sp == 0) or ((x + sp // 2) % sp == 0 and (z + sp // 2) % sp == 0)): continue
        if light.get((x, z), 0) >= 13: continue
        for (dx, dz) in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (2, 0), (0, 2)):
            c = (x + dx, z + dz)
            if c in cells and ctx.surf.get(c) in FLOOR_OK and c not in ctx.reserved:
                G.set(c[0], S, c[1], GLOWSTONE); ctx.surf[c] = 'lamp'; n += 1; spread([(c[0], c[1], 14)]); break
    # 2) greedy fill of what is still too dark
    for (x, z) in sorted(cells, key=lambda c: (c[1], c[0])):
        if light.get((x, z), 0) >= need: continue
        # put a lamp a few blocks further on (so one lamp covers this cell and the next ones), on a plain floor cell
        best = None
        for (dx, dz) in ((2, 2), (0, 4), (4, 0), (1, 3), (3, 1), (-2, 2), (0, 3), (3, 0), (-1, 3), (1, 1), (0, 2), (2, 0),
                         (-2, 1), (0, 1), (1, 0), (-1, 1), (0, 0), (-1, 0), (0, -1), (-2, 0), (0, -2), (-3, 1), (-4, 0)):
            c = (x + dx, z + dz)                                     # Manhattan <= 4 -> this cell gets >= 10
            if c in cells and ctx.surf.get(c) in FLOOR_OK and c not in ctx.reserved:
                best = c; break
        if not best: continue
        G.set(best[0], S, best[1], GLOWSTONE); ctx.surf[best] = 'lamp'; n += 1
        spread([(best[0], best[1], 14)])
    dark = sum(1 for c in cells if light.get(c, 0) < need)
    ctx.notes.append('lighting: %d flush glowstone lamps under the island, %d shadow cells still < %d' % (n, dark, need))
