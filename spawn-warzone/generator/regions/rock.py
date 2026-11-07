"""Big jagged volcanic rock landmark (not a pyramid): elliptical base, uneven shoulders, several spires, light-gray clay
with gray/black patches and andesite grain, an arched east-west tunnel players can walk/fight through."""
import math
from common import *

NAME = 'rock'


def build(G, BP, ctx):
    R = BP['rock']; S = BP['surface']; seed = BP['seed'] + 80; rng = ctx.rng
    cx, cz, rx, rz, H = R['x'], R['z'], R['rx'], R['rz'], R['height']
    spires = []
    for i in range(R['spires']):
        a = rng.uniform(0, 2 * math.pi); d = rng.uniform(0.0, 0.62)
        spires.append((cx + math.cos(a) * d * rx, cz + math.sin(a) * d * rz, H * rng.uniform(0.55, 1.0), rng.uniform(2.5, 5.0)))
    spires.append((cx + 1.5, cz - 2.5, H, 4.5))                        # main peak
    T = R['tunnel']; tw = T['width'] // 2
    blocks = 0
    for x in range(int(cx - rx) - 2, int(cx + rx) + 3):
        for z in range(int(cz - rz) - 2, int(cz + rz) + 3):
            e = math.sqrt(((x - cx) / rx) ** 2 + ((z - cz) / rz) ** 2) + (hash2(quant(x, 2), quant(z, 2), seed) - 0.5) * 0.18
            if e > 1: continue
            base = H * 0.45 * (1 - e) ** 0.7 * (0.6 + 0.8 * fbm(x, z, 9, seed + 1))
            h = base
            for (sx, sz, sh, sr) in spires:
                dd = math.hypot(x - sx, z - sz)
                if dd < sr * 2.2:
                    h = max(h, sh * max(0.0, 1 - dd / (sr * 2.2)) ** 1.25)
            h += (hash2(x, z, seed + 2) - 0.5) * 2.4                      # jagged top
            h = int(round(max(1, h)))
            for y in range(S + 1, S + 1 + h):
                if y > BP['y_max'] - 2: break
                k = fbm(quant(x, 3) + y * 0.0, quant(z, 3) + quant(y, 3) * 13, 6, seed + 3)
                g = hash2(x * 31 + y, z, seed + 4)
                if g < 0.05: blk = MOON_DARKEST
                elif g < 0.16: blk = (STONE, 5)
                elif k > 0.58: blk = MOON_DARK
                elif k > 0.5: blk = MOON_MID
                else: blk = MOON_LIGHT
                G.set(x, y, z, *blk); blocks += 1
            G.set(x, S, z, *MOON_DARK)
            ctx.surf[(x, z)] = 'rock'; ctx.reserved.add((x, z))
    # tunnel east-west through the middle, arched (centre 6 high, sides 5)
    for x in range(int(cx - rx) - 3, int(cx + rx) + 4):
        for dz in range(-tw, tw + 1):
            top = T['height'] - (1 if abs(dz) == tw else 0)
            for y in range(S + 1, S + 1 + top):
                G.set(x, y, cz + dz, AIR)
            G.set(x, S, cz + dz, *MOON_LIGHT)
            above = G.get(x, S + 1 + top, cz + dz)
            if ((x - int(cx)) % 4 == 0 and dz == 0 or (x - int(cx)) % 4 == 2 and abs(dz) == tw) and above and above[0] not in (AIR, GLOWSTONE) and R.get('tunnel_lights', True):
                G.set(x, S + 1 + top, cz + dz, GLOWSTONE)                   # tunnel lights (in the ceiling)
    ctx.notes.append('rock: %d blocks, peak y%d, tunnel z %d..%d y%d..%d' % (blocks, S + H, cz - tw, cz + tw, S + 1, S + T['height']))
