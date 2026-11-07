"""Small pink-and-dark-wood booth with a stepped roof on the wooden battlefield near the trap: pink clay posts, dark oak
floor/lintels, 4 tiers of dark oak stairs, and (beacon=true) a beacon on a hidden 3x3 iron base whose beam goes up
through pink stained glass in the roof (the pink beam seen in the frames)."""
from common import *

NAME = 'pavilion'


def build(G, BP, ctx):
    V = BP['pavilion']
    if not V.get('enabled', True):
        ctx.notes.append('pavilion: disabled (merged into the trap hut, area 1 v3)'); return
    S = BP['surface']; cx, cz = V['x'], V['z']; h = V['size'] // 2   # 7 -> 3
    post_top = S + 4
    for dx in range(-h - 2, h + 3):
        for dz in range(-h - 2, h + 3):
            x, z = cx + dx, cz + dz
            ctx.reserved.add((x, z))
            for y in range(S + 1, S + 12): G.set(x, y, z, AIR)
            if max(abs(dx), abs(dz)) <= h + 1:
                G.set(x, S, z, *((CLAY, PINK) if max(abs(dx), abs(dz)) == h + 1 else (PLANKS, 5)))
                ctx.surf[(x, z)] = 'struct'
    for dx in (-h, h):
        for dz in (-h, h):
            for y in range(S + 1, post_top + 1): G.set(cx + dx, y, cz + dz, CLAY, PINK)
    for dx in range(-h, h + 1):                       # lintel ring
        for dz in range(-h, h + 1):
            if max(abs(dx), abs(dz)) == h:
                G.set(cx + dx, post_top + 1, cz + dz, PLANKS, 5)
                if abs(dx) != h or abs(dz) != h:
                    G.set(cx + dx, post_top, cz + dz, CLAY, PINK) if (dx + dz) % 2 == 0 else None
    # stepped roof: tier k (0..3) at y post_top+1+k, ring radius h+1-k of stairs (high side inward), inside planks
    for k in range(h + 1):
        y = post_top + 1 + k; r = h + 1 - k
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                x, z = cx + dx, cz + dz
                if dx == 0 and dz == 0:
                    G.set(x, y, z, SGLASS, PINK) if V.get('beacon') else G.set(x, y, z, PLANKS, 5)
                    continue
                if max(abs(dx), abs(dz)) == r:
                    if dx == -r: d = 0          # west edge: high side east
                    elif dx == r: d = 1         # east edge: high side west
                    elif dz == -r: d = 2        # north edge: high side south
                    else: d = 3                 # south edge: high side north
                    G.set(x, y, z, DARKOAK_STAIRS, d)
                elif k == 0 or max(abs(dx), abs(dz)) == r - 1:
                    G.set(x, y, z, PLANKS, 5)
        if k == 0:                              # pink trim under the eaves
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if max(abs(dx), abs(dz)) == r and (dx + dz) % 2 == 0:
                        G.set(cx + dx, y - 1, cz + dz, CLAY, PINK) if max(abs(dx), abs(dz)) > h else None
    if V.get('beacon'):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1): G.set(cx + dx, S - 1, cz + dz, IRON_BLOCK)
        G.set(cx, S, cz, BEACON)
        for y in range(S + 1, post_top + 1): G.set(cx, y, cz, AIR)
    ctx.notes.append('pavilion: centre %d,%d posts y%d..%d roof y%d..%d beacon=%s' % (cx, cz, S + 1, post_top, post_top + 1, post_top + 1 + h, V.get('beacon')))
