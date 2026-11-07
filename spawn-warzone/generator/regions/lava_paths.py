"""Glass-covered lava paths near the centre (4 wide). Lava at y68 sealed by nether brick (sides + bottom) and covered by
flush glass at y69, nether brick curbs at y69 on both sides; nether brick arches over the path every arch_every blocks,
and low nether-brick posts with glowstone beside each arch."""
from common import *

NAME = 'lava_paths'


def build(G, BP, ctx):
    P = BP['lava_paths']; S = BP['surface']; w = P['width']; LP = BP['landing']
    half_lo = -(w // 2); half_hi = half_lo + w - 1           # 4 wide -> offsets -2..1
    cells = 0; arches = 0
    for p in P['paths']:
        a, b, c = p['a'], p['b'], p['c']
        for t in range(a, b + 1):
            for off in range(half_lo - 1, half_hi + 2):
                x, z = (t, c + off) if p['axis'] == 'x' else (c + off, t)
                curb = off in (half_lo - 1, half_hi + 1)
                for y in range(S + 1, S + 6):
                    if G.get(x, y, z) and G.get(x, y, z)[0] != AIR and not curb: G.set(x, y, z, AIR)
                if curb:
                    G.set(x, S, z, NETHER_BRICK); G.set(x, S - 1, z, NETHER_BRICK); G.set(x, S - 2, z, NETHER_BRICK)
                    G.set(x, S + 1, z, AIR)
                    ctx.surf[(x, z)] = 'curb'
                else:
                    G.set(x, S, z, GLASS); G.set(x, S - 1, z, LAVA); G.set(x, S - 2, z, NETHER_BRICK)
                    ctx.surf[(x, z)] = 'path'; cells += 1
                ctx.reserved.add((x, z))
            # path ends: close the channel with nether brick (lava must be sealed on all sides)
            if t in (a, b):
                e = t - 1 if t == a else t + 1
                for off in range(half_lo - 1, half_hi + 2):
                    x, z = (e, c + off) if p['axis'] == 'x' else (c + off, e)
                    G.set(x, S - 1, z, NETHER_BRICK); G.set(x, S, z, NETHER_BRICK); G.set(x, S - 2, z, NETHER_BRICK)
                    ctx.surf[(x, z)] = 'curb'; ctx.reserved.add((x, z))
            # arches (skip the first/last 6 blocks)
            if (t - a) % P['arch_every'] == P['arch_every'] // 2 and a + 6 < t < b - 6:
                arches += 1
                for off in (half_lo - 1, half_hi + 1):
                    x, z = (t, c + off) if p['axis'] == 'x' else (c + off, t)
                    for y in range(S + 1, S + 6): G.set(x, y, z, NETHER_BRICK)
                    # post with a light beside the arch (outside the curb)
                    po = off + (-1 if off < 0 else 1)
                    px, pz = (t, c + po) if p['axis'] == 'x' else (c + po, t)
                    G.set(px, S + 1, pz, NB_FENCE); G.set(px, S + 2, pz, GLOWSTONE)
                for off in range(half_lo, half_hi + 1):
                    x, z = (t, c + off) if p['axis'] == 'x' else (c + off, t)
                    G.set(x, S + 6, z, NETHER_BRICK)
                    if off in (half_lo, half_hi):            # rounded inner corners: upside-down stairs
                        if p['axis'] == 'x':
                            d = 3 if off == half_lo else 2   # high side toward the curb (N=3 / S=2)
                        else:
                            d = 1 if off == half_lo else 0   # W=1 / E=0
                        G.set(x, S + 5, z, NB_STAIRS, d + 4)
                for off in (half_lo - 1, half_hi + 1):
                    x, z = (t, c + off) if p['axis'] == 'x' else (c + off, t)
                    G.set(x, S + 6, z, NETHER_BRICK)
    ctx.notes.append('lava_paths: %d glass-over-lava cells, %d arches' % (cells, arches))
