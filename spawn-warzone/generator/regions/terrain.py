"""Base terrain: fill y fill_from..68, clear above, zone map, grass/oak-plank fields with blocky irregular borders,
light-gray patches in the north, low raised plank borders. Every other region builds on top of this."""
import math, random
from common import *

NAME = 'terrain'


def zone_of(x, z, P, S, seed):
    m = P['moon']
    n = (fbm(x, z, 40, seed + 7) - 0.5) * 2
    d = ((x - m['cx']) / m['rx']) ** 2 + ((z - m['cz']) / m['rz']) ** 2
    if d < 1 + m['noise'] * n * 2 and x <= m['x_max'] + n * 4:
        return 'moon'
    bn = (fbm(x, z, 26, seed + 11) - 0.5) * 2 * P['border_noise']
    if z < P['north_z'] + bn:
        return 'north'
    if x < P['west_x'] + bn:
        return 'west'
    return 'fields'


def build(G, BP, ctx):
    P = BP['terrain']; S = BP['surface']; seed = BP['seed']
    x1, z1, x2, z2 = BP['box']
    q = P['patch_grid']
    for x in range(x1, x2 + 1):
        for z in range(z1, z2 + 1):
            zone = zone_of(x, z, P, S, seed)
            ctx.zone[(x, z)] = zone
            # fill + clear
            for y in range(P['fill_from'], S):
                G.set(x, y, z, DIRT if y >= P['dirt_from'] else STONE)
            for y in range(S + 1, BP['y_max'] + 1):
                G.set(x, y, z, AIR)
            if zone == 'moon':
                G.set(x, S, z, *MOON_LIGHT); G.set(x, S - 1, z, *MOON_LIGHT); G.set(x, S - 2, z, STONE)
                ctx.surf[(x, z)] = 'moon'
                continue
            # blocky (quantised) noise decides wood vs grass
            qx, qz = quant(x, q), quant(z, q)
            v = stretch(fbm(qx, qz, P['noise_scale'], seed + 3))
            share = P['wood_share'][zone]
            wood = v < share
            if wood:
                G.set(x, S, z, PLANKS, P.get('plank_data', 5)); ctx.surf[(x, z)] = 'wood'
                if zone == 'north' and stretch(fbm(qx + 500, qz, 14, seed + 5), 3.0) < P['gray_patch_share_north']:
                    G.set(x, S, z, *MOON_LIGHT); ctx.surf[(x, z)] = 'gray'
            else:
                G.set(x, S, z, GRASS); ctx.surf[(x, z)] = 'grass'
    # raised plank borders: short runs along wood/grass borders, wood side raised by 1 with slabs at the ends
    rb = P['raised_borders']; rng = ctx.rng
    borders = [(x, z) for (x, z), s in ctx.surf.items() if s == 'wood' and ctx.zone[(x, z)] in ('west', 'fields')
               and any(ctx.surf.get((x + dx, z + dz)) == 'grass' for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)))
               and not ctx.near_island(x, z, 2)]
    borders.sort()
    made = 0; tries = 0
    while made < rb['count'] and tries < 400 and borders:
        tries += 1
        sx, sz = borders[rng.randrange(len(borders))]
        # follow the border for len cells
        L = rng.randint(rb['len_min'], rb['len_max'])
        cells = [(sx, sz)]; cur = (sx, sz); seen = {cur}
        for _ in range(L):
            nxt = None
            for dx, dz in ((1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)):
                c = (cur[0] + dx, cur[1] + dz)
                if c in seen or ctx.surf.get(c) != 'wood': continue
                if any(ctx.surf.get((c[0] + a, c[1] + b)) == 'grass' for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    nxt = c; break
            if not nxt: break
            seen.add(nxt); cells.append(nxt); cur = nxt
        if len(cells) < rb['len_min']: continue
        for i, (x, z) in enumerate(cells):
            # raise this cell and the wood cell behind it (2 wide) -> 1-block plank border, slabs on the run's ends
            end = i < 2 or i >= len(cells) - 2
            for (cx, cz) in [(x, z)] + [(x + dx, z + dz) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))
                                        if ctx.surf.get((x + dx, z + dz)) == 'wood' and ctx.surf.get((x - dx, z - dz)) == 'grass']:
                G.set(cx, BP['surface'] + 1, cz, SLAB_WOOD if end else PLANKS, BP['terrain'].get('plank_data', 5))
                ctx.surf[(cx, cz)] = 'wood_raised'
        made += 1
    gray_patches(BP, ctx, G)                 # after the borders: ctx.rng sequence (moon, rock, ...) unchanged
    ctx.notes.append('terrain: %d raised plank borders' % made)


def _stroke(cx, cz, length, width, ang):
    """Cells of a rotated rectangle (centre cx,cz) rasterised on the block grid -> stair-stepped diagonal edges."""
    ca, sa = math.cos(ang), math.sin(ang)
    r = int(length / 2 + width) + 1
    out = []
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            u = dx * ca + dz * sa; v = -dx * sa + dz * ca
            if abs(u) <= length / 2 and abs(v) <= width / 2:
                out.append((cx + dx, cz + dz))
    return out


def gray_patches(BP, ctx, G):
    """Light-gray patches on the plank floor (R06, R09, R13, R21): small rotated strokes 1-4 wide, 2-12 long, in slanted
    clusters of 2-5 roughly parallel strokes; long thin diagonal strips along the north edge (R06); denser next to the
    gray moon (R21 transition). Only plank cells change; grass, moon, island footprint and landing stay."""
    GP = BP['terrain'].get('gray_patches')
    if not GP: return
    S = BP['surface']; rng = random.Random(BP['seed'] * 31 + 7)   # own RNG: raised borders keep their layout
    x1, z1, x2, z2 = BP['box']
    wood = [k for k, s in ctx.surf.items() if s == 'wood']
    wood.sort()
    woodset = set(wood)
    L = BP['landing']
    def ok(c):
        return c in woodset and (c[0] - L['x']) ** 2 + (c[1] - L['z']) ** 2 > (L['r'] + 3) ** 2
    painted = set()
    def paint(cells):
        for c in cells:
            if ok(c) and c not in painted:
                G.set(c[0], S, c[1], *MOON_LIGHT); ctx.surf[c] = 'gray'; painted.add(c)
    by_zone = {}
    for c in wood: by_zone.setdefault(ctx.zone[c], []).append(c)
    clusters = 0
    for zone, n in GP['clusters'].items():
        cells = by_zone.get(zone, [])
        for _ in range(n if cells else 0):
            cx, cz = cells[rng.randrange(len(cells))]
            ang = rng.uniform(0, math.pi)                     # cluster direction; strokes stay near-parallel to it
            for k in range(rng.randint(*GP['strokes_per_cluster'])):
                off = rng.uniform(-1, 1) * GP['cluster_spread']
                px = cx + int(round(-math.sin(ang) * off + rng.uniform(-2, 2)))
                pz = cz + int(round(math.cos(ang) * off + rng.uniform(-2, 2)))
                paint(_stroke(px, pz, rng.uniform(*GP['length']), rng.uniform(*GP['width']), ang + rng.uniform(-0.25, 0.25)))
            clusters += 1
    # R06: long thin diagonal strips along the north box edge
    ne = GP['north_edge']
    for _ in range(ne['count']):
        sx = rng.randint(x1 + 4, x2 - 4); sz = z1 + rng.randint(1, ne['depth'])
        ang = rng.choice((1, -1)) * rng.uniform(*ne['angle'])
        paint(_stroke(sx, sz, rng.uniform(*ne["length"]), rng.uniform(1, 1.6), ang))
    # R21: denser short strokes on plank cells within `band` of the moon
    mb = GP['moon_band']
    near = [c for c in wood if any(ctx.zone.get((c[0] + dx, c[1] + dz)) == 'moon'
                                   for dx in (-mb['band'], 0, mb['band']) for dz in (-mb['band'], 0, mb['band']))]
    for _ in range(mb['strokes'] if near else 0):
        cx, cz = near[rng.randrange(len(near))]
        paint(_stroke(cx, cz, rng.uniform(3, 9), rng.uniform(1, 3), rng.uniform(0, math.pi)))
    ctx.notes.append('gray patches: %d clusters, %d cells' % (clusters, len(painted)))
