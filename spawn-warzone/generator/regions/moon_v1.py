"""Gray volcanic 'moon' zone: raised gray platforms with jagged edges, small mounds, a stepped crater and branching
open lava cracks/pools (sealed, 1 deep, kept away from wood, the island footprint, the rock and the crater)."""
import math
from common import *

NAME = 'moon'


def build(G, BP, ctx):
    P = BP['moon']; S = BP['surface']; seed = BP['seed'] + 40; rng = ctx.rng
    moon = [c for c, z in ctx.zone.items() if z == 'moon']
    mset = set(moon)
    R = BP['rock']; C = P['crater']

    def in_rock(x, z, m=0):
        return ((x - R['x']) / (R['rx'] + m)) ** 2 + ((z - R['z']) / (R['rz'] + m)) ** 2 <= 1

    def in_crater(x, z, m=0):
        return math.hypot(x - C['x'], z - C['z']) <= C['r'] + m

    # distance (in columns) to the nearest non-moon column, BFS limited to keep_from_wood
    L = P['lava']; keep = L['keep_from_wood']
    dist = {}
    frontier = [c for c in moon if any((c[0] + dx, c[1] + dz) not in mset for dx in (-1, 0, 1) for dz in (-1, 0, 1))]
    for c in frontier: dist[c] = 1
    d = 1
    while frontier and d < keep + 1:
        nf = []
        for (x, z) in frontier:
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):   # Chebyshev distance
                n = (x + dx, z + dz)
                if n in mset and n not in dist:
                    dist[n] = d + 1; nf.append(n)
        frontier = nf; d += 1

    def lava_ok(x, z):
        return ((x, z) in mset and dist.get((x, z), 99) > keep and not ctx.near_island(x, z, L['keep_from_island'])
                and not in_rock(x, z, 3) and not in_crater(x, z, 4) and (x, z) not in ctx.reserved)

    # 1) platforms (+1) with jagged edges: noise on a 2-grid plus per-cell jitter
    for (x, z) in moon:
        if in_rock(x, z, 1) or in_crater(x, z, 2) or (x, z) in ctx.reserved: continue
        v = fbm(quant(x, 2), quant(z, 2), P['platform_scale'], seed + 1) + (hash2(x, z, seed + 2) - 0.5) * 0.06
        if v > 1 - P['platform_share']:
            G.set(x, S + 1, z, *MOON_MID); ctx.surf[(x, z)] = 'platform'
            if v > 1 - P['platform_share'] * 0.25:
                G.set(x, S + 2, z, *(MOON_DARK if hash2(x, z, seed + 3) > 0.15 else MOON_DARKEST))

    # 2) lava cracks: branching random walks
    lava = set(); born = {}   # cell -> (walker id, step)
    walkers = [(sx, sz, rng.uniform(0, 2 * math.pi), steps) for sx, sz, steps in L['seeds']]
    wid = 0
    while walkers:
        x, z, ang, steps = walkers.pop(); wid += 1
        fx, fz = float(x), float(z)
        for step in range(int(steps)):
            if rng.random() < L['turn_p']: ang += rng.uniform(-0.9, 0.9)
            fx += math.cos(ang); fz += math.sin(ang)
            cx, cz = int(round(fx)), int(round(fz))
            if not lava_ok(cx, cz):
                break                                                   # crack ends at a forbidden area
            if step > 3 and any(born.get((cx + a, cz + b), (wid, step))[0] != wid or step - born[(cx + a, cz + b)][1] > 6
                                for a in (-2, -1, 0, 1, 2) for b in (-2, -1, 0, 1, 2) if (cx + a, cz + b) in born):
                break                                                   # ran into another crack: join it and stop
            lava.add((cx, cz)); born.setdefault((cx, cz), (wid, step))
            if rng.random() < L['wide_p']:
                w = (cx + rng.choice((-1, 0, 1)), cz + rng.choice((-1, 0, 1)))
                if lava_ok(*w): lava.add(w); born.setdefault(w, (wid, step))
            if rng.random() < L['branch_p'] and steps > 20:
                walkers.append((cx, cz, ang + rng.choice((-1, 1)) * rng.uniform(0.6, 1.3), steps * rng.uniform(0.25, 0.5)))
    cracks = sorted(lava)
    for _ in range(L['pools']):
        if not cracks: break
        px, pz = cracks[rng.randrange(len(cracks))]
        r = rng.uniform(1.6, 3.2)
        for x in range(int(px - r) - 1, int(px + r) + 2):
            for z in range(int(pz - r) - 1, int(pz + r) + 2):
                if math.hypot(x - px, z - pz) + (hash2(x, z, seed + 9) - 0.5) * 1.2 <= r and lava_ok(x, z):
                    lava.add((x, z))
    for (x, z) in lava:
        G.set(x, S, z, LAVA); G.set(x, S - 1, z, *MOON_DARK); G.set(x, S - 2, z, STONE)
        G.set(x, S + 1, z, AIR); G.set(x, S + 2, z, AIR)
        ctx.surf[(x, z)] = 'lava'
    # dark rims + darker floor around lava (volcanic look)
    for (x, z) in lava:
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                n = (x + dx, z + dz)
                if n in lava or n not in mset: continue
                s = ctx.surf.get(n)
                if s == 'moon' and (abs(dx) + abs(dz) <= 1 or hash2(n[0], n[1], seed + 4) < 0.45 - 0.1 * max(abs(dx), abs(dz))):
                    G.set(n[0], S, n[1], *(MOON_DARKEST if abs(dx) + abs(dz) <= 1 and hash2(n[0], n[1], seed + 12) < 0.3 else MOON_DARK)); ctx.surf[n] = 'moon_dark'

    # 3) crater: stepped rings down to -depth, raised rim
    r = C['r']
    for x in range(C['x'] - r - 3, C['x'] + r + 4):
        for z in range(C['z'] - r - 3, C['z'] + r + 4):
            if (x, z) not in mset or (x, z) in ctx.reserved: continue
            dd = math.hypot(x - C['x'], z - C['z']) + (hash2(x, z, seed + 5) - 0.5) * 0.9
            if dd <= r:
                depth = C['depth'] if dd < r * 0.45 else (2 if dd < r * 0.65 else (1 if dd < r * 0.85 else 0))
                depth = min(depth, C['depth'])
                for y in range(S - depth + 1, S + 3): G.set(x, y, z, AIR)
                G.set(x, S - depth, z, *(MOON_LIGHT if depth in (0, C['depth']) else MOON_MID))
                ctx.surf[(x, z)] = 'crater'
            elif dd <= r + 1.6:
                G.set(x, S + 1, z, *MOON_DARK); G.set(x, S + 2, z, AIR); ctx.surf[(x, z)] = 'crater_rim'

    # 4) mounds
    made = 0; tries = 0
    while made < P['mounds'] and tries < 2000:
        tries += 1
        mx, mz = moon[rng.randrange(len(moon))]
        rr = rng.uniform(2.0, 4.2); h = rng.randint(2, 4)
        if in_rock(mx, mz, rr + 4) or in_crater(mx, mz, rr + 4) or ctx.near_island(mx, mz, 4): continue
        if any((mx + dx, mz + dz) in lava for dx in range(-int(rr) - 2, int(rr) + 3) for dz in range(-int(rr) - 2, int(rr) + 3)): continue
        if dist.get((mx, mz), 99) <= int(rr) + 1: continue
        if any((mx + dx, mz + dz) in ctx.reserved for dx in range(-int(rr) - 3, int(rr) + 4) for dz in range(-int(rr) - 3, int(rr) + 4)): continue
        for x in range(int(mx - rr) - 1, int(mx + rr) + 2):
            for z in range(int(mz - rr) - 1, int(mz + rr) + 2):
                dd = math.hypot(x - mx, z - mz) / rr + (hash2(x, z, seed + 6) - 0.5) * 0.25
                if dd > 1: continue
                top = S + max(1, int(round(h * math.sqrt(max(0, 1 - dd * dd)))))
                for y in range(S + 1, top + 1):
                    k = hash2(x * 7 + y, z, seed + 8)
                    G.set(x, y, z, *((STONE, 5) if k < 0.4 else (MOON_MID if k < 0.7 else MOON_DARK)))
                ctx.surf[(x, z)] = 'mound'
        made += 1
    ctx.lava_cells = lava
    ctx.notes.append('moon: %d lava cells, %d mounds, crater at %d,%d' % (len(lava), made, C['x'], C['z']))
