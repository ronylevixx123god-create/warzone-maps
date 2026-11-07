"""Landing pad under the island's drop-down hole (centre 44,0; hole r 7.5 at y149): round quartz/clay pad that the
four glass lava paths start from. A quartz ring marks the hole edge so players see where they come down."""
import math
from common import *

NAME = 'landing'


def build(G, BP, ctx):
    L = BP['landing']; S = BP['surface']; cx, cz, r = L['x'], L['z'], L['r']
    hole = BP['island']['drop_holes'][0]['r']
    n = 0
    for x in range(cx - r - 1, cx + r + 2):
        for z in range(cz - r - 1, cz + r + 2):
            d = math.hypot(x - cx, z - cz)
            if d > r + 0.5: continue
            ang = math.degrees(math.atan2(z - cz, x - cx)) % 45
            if d < 2.5: blk = (QUARTZ, 1)
            elif 5.0 <= d < 5.9: blk = MOON_DARK
            elif hole <= d < hole + 1.1: blk = (QUARTZ, 0)
            elif d >= r - 0.5: blk = MOON_DARK
            elif d > hole + 1.1 and (ang < 2.5 or ang > 42.5): blk = MOON_DARK      # 8 spokes
            else: blk = MOON_LIGHT
            if abs(d - 11) < 0.6 and abs(ang - 22.5) < 3.5: blk = (SEA_LANTERN, 0)  # flush lights between spokes
            G.set(x, S, z, *blk); G.set(x, S - 1, z, STONE)
            for y in range(S + 1, S + 6): G.set(x, y, z, AIR)
            ctx.surf[(x, z)] = 'pad'; ctx.reserved.add((x, z)); n += 1
    ctx.notes.append('landing: pad r%d at %d,%d (%d columns); hole r%.1f directly above at y149' % (r, cx, cz, n, hole))
