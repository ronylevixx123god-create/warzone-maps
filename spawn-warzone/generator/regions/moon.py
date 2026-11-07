"""Gray volcanic 'moon' zone v2 (2026-11-06, user: "big section of rocky spot, clay bigger and stones"; lava is NEVER open:
red/orange stained glass flush on top, lava under it).

R15/R16 (aerial): big gray plates 15-30 wide separated by wide orange channels, a crater. R05: dark stone plateaus that
step up 1-2 blocks next to the orange. R11/R01: wide light-gray floors, blocky raised slabs, dark stone heaps.

- plates: Voronoi cells (jittered grid, `plate_size`) on a 2-block grid (stair-stepped edges); each plate is floor (0),
  a light-gray slab (+1, clay 82) or a dark stone plateau (+1/+2, polished andesite, dark top);
- channels: a share of the plate borders become 2-4 wide glass-over-lava channels: orange 95:1 / red 95:14 glass at the
  surface (walkable), lava under it, sealed by cyan clay 159:9 below and beside; 1-block dark rims;
- crater (as v1) and blocky dark stone heaps.
Own RNG; at the end ctx.rng is reset to the state moon v1 left (regions/rng_after_moon_v1.json) so rock/trap stay identical.
"""
import math, random, json, os
from common import *

NAME = 'moon'
RED_GLASS, ORANGE_GLASS = (SGLASS, 14), (SGLASS, 1)


def build(G, BP, ctx):
    P = BP['moon']; S = BP['surface']; seed = BP['seed'] + 40
    rng = random.Random(seed * 13 + 5)
    moon = sorted(c for c, z in ctx.zone.items() if z == 'moon')
    mset = set(moon)
    R = BP['rock']; C = P['crater']; V = P['v2']

    def in_rock(x, z, m=0):
        return ((x - R['x']) / (R['rx'] + m)) ** 2 + ((z - R['z']) / (R['rz'] + m)) ** 2 <= 1

    def in_crater(x, z, m=0):
        return math.hypot(x - C['x'], z - C['z']) <= C['r'] + m

    # distance to the nearest non-moon column (Chebyshev, capped) - keeps lava away from wood/grass
    keep = V['keep_from_wood']
    dist = {}
    frontier = [c for c in moon if any((c[0] + dx, c[1] + dz) not in mset for dx in (-1, 0, 1) for dz in (-1, 0, 1))]
    for c in frontier: dist[c] = 1
    d = 1
    while frontier and d < keep + 2:
        nf = []
        for (x, z) in frontier:
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    n = (x + dx, z + dz)
                    if n in mset and n not in dist:
                        dist[n] = d + 1; nf.append(n)
        frontier = nf; d += 1

    # 1) Voronoi plates
    sz = V['plate_size']
    xs = [c[0] for c in moon]; zs = [c[1] for c in moon]
    seeds = {}
    for gx in range(min(xs) // sz - 1, max(xs) // sz + 2):
        for gz in range(min(zs) // sz - 1, max(zs) // sz + 2):
            seeds[(gx, gz)] = (gx * sz + rng.uniform(0.15, 0.85) * sz, gz * sz + rng.uniform(0.15, 0.85) * sz)
    keys = sorted(seeds)
    kind = {}
    for k in keys:
        r = rng.random()
        kind[k] = 0 if r < V['share_floor'] else (1 if r < V['share_floor'] + V['share_light'] else 2)
    pair_open = {}

    def channel_pair(a, b):
        key = (a, b) if a < b else (b, a)
        if key not in pair_open:
            pair_open[key] = (rng.random() < V['channel_share'], rng.uniform(*V['channel_halfwidth']))
        return pair_open[key]

    cell_plate = {}; edge = {}
    for (x, z) in moon:
        qx, qz = quant(x, 2) + 1, quant(z, 2) + 1        # 2-block grid -> stair-stepped borders
        gx, gz = int(qx // sz), int(qz // sz)
        best = []
        for dx in (-1, 0, 1, 2, -2):
            for dz in (-1, 0, 1, 2, -2):
                k = (gx + dx, gz + dz)
                if k in seeds:
                    sx, sz2 = seeds[k]; best.append(((qx - sx) ** 2 + (qz - sz2) ** 2, k))
        best.sort()
        (d1, k1), (d2, k2) = best[0], best[1]
        cell_plate[(x, z)] = k1
        edge[(x, z)] = (math.sqrt(d2) - math.sqrt(d1), k1, k2)

    def lava_ok(x, z):
        return ((x, z) in mset and dist.get((x, z), 99) > keep and not ctx.near_island(x, z, V['keep_from_island'])
                and not in_rock(x, z, 3) and not in_crater(x, z, 4) and (x, z) not in ctx.reserved)

    lava = set()
    for (x, z) in moon:
        gap, k1, k2 = edge[(x, z)]
        is_open, hw = channel_pair(k1, k2)
        if is_open and gap <= hw * 2 and lava_ok(x, z):
            lava.add((x, z))
    # drop tiny bits (< 6 cells) so channels read as channels
    seen = set()
    for c in sorted(lava):
        if c in seen: continue
        comp = [c]; seen.add(c); i = 0
        while i < len(comp):
            x, z = comp[i]; i += 1
            for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if n in lava and n not in seen: seen.add(n); comp.append(n)
        if len(comp) < 6:
            for n in comp: lava.discard(n)

    plates = 0
    for (x, z) in moon:
        if (x, z) in ctx.reserved or in_rock(x, z, 1) or in_crater(x, z, 2): continue
        if (x, z) in lava: continue
        k = cell_plate[(x, z)]; t = kind[k]
        gap = edge[(x, z)][0]
        if t == 1 and gap > 1.0:
            G.set(x, S + 1, z, *MOON_LIGHT); ctx.surf[(x, z)] = 'platform'
        elif t == 2 and gap > 1.0:
            G.set(x, S + 1, z, *MOON_MID); ctx.surf[(x, z)] = 'platform'
            if gap > 3.0 and hash2(x // 3, z // 3, seed + 3) < V['plateau_top_share']:
                G.set(x, S + 2, z, *(MOON_DARK if hash2(x, z, seed + 4) > 0.2 else MOON_MID))
    plates = len(keys)

    # 2) glass-over-lava channels (walkable, sealed)
    for (x, z) in lava:
        G.set(x, S, z, *(RED_GLASS if hash2(x // 2, z // 2, seed + 7) < V['red_share'] else ORANGE_GLASS))
        G.set(x, S - 1, z, LAVA); G.set(x, S - 2, z, *MOON_DARK)
        for y in range(S + 1, S + 4): G.set(x, y, z, AIR)
        ctx.surf[(x, z)] = 'lava'; ctx.reserved.add((x, z))
    for (x, z) in lava:
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, z + dz)
            if n in lava: continue
            G.set(n[0], S - 1, n[1], *MOON_DARK)                     # seal the side under the surface
            if ctx.surf.get(n) == 'moon':
                G.set(n[0], S, n[1], *MOON_DARK); ctx.surf[n] = 'moon_dark'   # dark rim (R15)

    # 3) crater (v1): stepped rings down to -depth, raised rim
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

    # 4) blocky dark stone heaps (R01/R11): stacked 2x2 blocks, 2-4 high
    made = 0; tries = 0
    while made < V['heaps'] and tries < 4000:
        tries += 1
        mx, mz = moon[rng.randrange(len(moon))]
        rr = rng.uniform(*V['heap_radius']); h = rng.randint(2, 4)
        if in_rock(mx, mz, rr + 4) or in_crater(mx, mz, rr + 4) or ctx.near_island(mx, mz, 4): continue
        if dist.get((mx, mz), 99) <= int(rr) + 2: continue
        box = [(mx + dx, mz + dz) for dx in range(-int(rr) - 2, int(rr) + 3) for dz in range(-int(rr) - 2, int(rr) + 3)]
        if any(c in lava or c in ctx.reserved for c in box): continue
        for x in range(int(mx - rr) - 1, int(mx + rr) + 2):
            for z in range(int(mz - rr) - 1, int(mz + rr) + 2):
                bx, bz = quant(x, 2), quant(z, 2)
                dd = math.hypot(bx - mx, bz - mz) / rr + (hash2(bx, bz, seed + 6) - 0.5) * 0.5
                if dd > 1: continue
                top = S + max(1, int(round(h * (1 - dd * 0.8))))
                for y in range(S + 1, top + 1):
                    k = hash2(bx * 7 + y, bz, seed + 8)
                    G.set(x, y, z, *((STONE, 5) if k < 0.35 else (MOON_MID if k < 0.75 else MOON_DARK)))
                ctx.surf[(x, z)] = 'mound'
        made += 1
    ctx.lava_cells = lava
    # keep the old random sequence for the regions after this one (rock) -> they stay byte-identical
    st = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rng_after_moon_v1.json')))['state']
    ctx.rng.setstate((st[0], tuple(st[1]), st[2]))
    ctx.notes.append('moon v2: %d moon columns, %d plates, %d glass-over-lava cells, %d heaps, crater at %d,%d'
                     % (len(moon), plates, len(lava), made, C['x'], C['z']))
