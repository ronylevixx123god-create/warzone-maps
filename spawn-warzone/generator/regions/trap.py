"""Gank hut + pit, v3 (area 1, 2026-11-06 after the user's feedback): NO building around the pit; the gank structure is
the small dark-wood hut of R24 and the pit hole is in the middle of its floor. Original HUD coordinates 1:1 (option A).

- Hut (R24 outside, R17/R19 inside): dark oak plank walls, a purple-glass doorway and an open doorway in the west face
  and (mirrored to fit R24's left/right, see blueprint _doc) the same in the east face, a stepped roof (3 steps) to a
  short flat top, beacon on a hidden 3x3 iron base inside the roof, purple glass above it -> purple beam (R24).
- Pit: 3x3 hole in the hut floor, shaft walls red/green checker glass under a dark-wood rim (R17), drop to the middle
  room (feet y62, red/green checker, R18), stairs down to the lowest chamber (feet y56, pink/red checker, stepped
  ceiling, R07), and a stair run back up to the grass OUTSIDE the hut (walk out, no jump).
- Flat grass apron around the hut (R24/R17 grass). Every size/position not tied to an R-ID is ESTIMATED."""
from common import *

NAME = 'trap'
GREEN = 13


def build(G, BP, ctx):
    T = BP['trap']; S = BP['surface']
    hut, mid, low = T['hut'], T['mid'], T['low']
    sh, ap = T['shell'], T['apron']
    oak = (PLANKS, 5)
    pane = (SGLASS, T['window_colour'])

    def P(x, y, z, b, d=0): G.set(x, y, z, b, d)

    def box(x1, y1, z1, x2, y2, z2, b, d=0):
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                for z in range(z1, z2 + 1): P(x, y, z, b, d)

    # 0) grass apron at the surface (air above), solid stone under the whole pit area
    for x in range(ap[0], ap[2] + 1):
        for z in range(ap[1], ap[3] + 1):
            P(x, S, z, GRASS); P(x, S - 1, z, DIRT)
            for y in range(S + 1, S + 12): P(x, y, z, AIR)
            ctx.reserved.add((x, z)); ctx.surf[(x, z)] = 'grass'
    box(sh[0], low['floor'] - 2, sh[1], sh[2], S - 2, sh[3], STONE)

    def checker(x, y, z, a, b):
        return a if (x + y + z) % 2 else b

    def back(c, bk):
        b = (bk or {}).get(str(c))
        return tuple(b) if b else (CLAY, c)

    def room(R, fy, cy, cols, light_every):
        """glass box: floor fy, ceiling cy, glass walls one cell outside the interior, backing one more cell out."""
        x1, z1, x2, z2 = R['x1'], R['z1'], R['x2'], R['z2']; bk = R.get('backing')
        for x in range(x1 - 2, x2 + 3):
            for z in range(z1 - 2, z2 + 3):
                for y in range(fy - 1, cy + 2):
                    inside = x1 <= x <= x2 and z1 <= z <= z2
                    wall = x1 - 1 <= x <= x2 + 1 and z1 - 1 <= z <= z2 + 1
                    c = checker(x, y, z, *cols)
                    if inside and fy < y < cy: P(x, y, z, AIR)
                    elif (inside and y in (fy, cy)) or (wall and fy <= y <= cy): P(x, y, z, SGLASS, c)
                    else: P(x, y, z, *back(c, bk))
        for x in range(x1 + 1, x2, light_every):
            for z in range(z1 + 1, z2, light_every):
                if T.get('lights', True): P(x, cy + 1, z, GLOWSTONE)

    # 1) middle room (R18) first, then the lowest chamber (R07) which shares the y60 layer (keeps its lights)
    mf, mc = mid['floor'], mid['ceil']
    room(mid, mf, mc, (RED, GREEN), 3)
    lf, lc = low['floor'], low['ceil']
    room(low, lf, lc, (RED, PINK), 3)
    sides = low.get('low_sides', '')
    for x in range(low['x1'], low['x2'] + 1):           # stepped ceiling: one block lower along the listed sides
        for z in range(low['z1'], low['z2'] + 1):
            if (x == low['x1'] and 'W' in sides) or (x == low['x2'] and 'E' in sides) or \
               (z == low['z1'] and 'N' in sides) or (z == low['z2'] and 'S' in sides):
                P(x, lc - 1, z, SGLASS, checker(x, lc - 1, z, RED, PINK))

    # 2) hut: floor, walls, doorways, stepped roof, beacon
    hx1, hz1, hx2, hz2, wt = hut['x1'], hut['z1'], hut['x2'], hut['z2'], hut['wall_top']
    for x in range(hx1, hx2 + 1):
        for z in range(hz1, hz2 + 1):
            P(x, S, z, *oak); ctx.surf[(x, z)] = 'struct'
            ring = x in (hx1, hx2) or z in (hz1, hz2)
            for y in range(S + 1, wt + 1): P(x, y, z, *(oak if ring else (AIR, 0)))
    dh = hut['door_h']
    for face in hut['door_faces']:
        x = hx1 if face == 'W' else hx2
        g0, g1 = hut['glass_z']; o0, o1 = hut.get('open_z') or (None, None)
        box(x, S + 1, g0, x, S + dh, g1, *pane)
        if o0 is not None: box(x, S + 1, o0, x, S + dh, o1, AIR)
    for k in range(hut['roof_steps'] + 1):               # k=0 cap over the walls, then one step in per layer
        y = wt + 1 + k
        box(hx1 + k, y, hz1 + k, hx2 - k, y, hz2 - k, *oak)
    top = wt + 1 + hut['roof_steps']
    bx, bz = (hx1 + hx2) // 2, (hz1 + hz2) // 2
    if hut.get('beacon'):
        box(bx - 1, wt + 2, bz - 1, bx + 1, wt + 2, bz + 1, IRON_BLOCK)    # hidden inside roof step 1
        P(bx, wt + 3, bz, BEACON)                                           # inside roof step 2
        for y in range(wt + 4, top + 2): P(bx, y, bz, *pane)               # top layer + one block on top: purple

    # 3) pit hole in the hut floor -> middle room; shaft walls checker glass, dark-wood rim = hut floor
    px1, pz1, px2, pz2 = T['hole']
    for x in range(px1 - 2, px2 + 3):
        for z in range(pz1 - 2, pz2 + 3):
            inside = px1 <= x <= px2 and pz1 <= z <= pz2
            ring1 = px1 - 1 <= x <= px2 + 1 and pz1 - 1 <= z <= pz2 + 1 and not inside
            for y in range(mc, S + 1):
                c = checker(x, y, z, RED, GREEN)
                if inside: P(x, y, z, AIR)
                elif mc < y < S: P(x, y, z, *((SGLASS, c) if ring1 else (CLAY, c)))

    # 4) stairs: each run starts at `top` (y_top, flush with the floor above) and goes one cell `step` and 1 down per stair
    for st in T['stairs']:
        sx, sz = st['step']
        for i in range(st['count']):
            y = st['y_top'] - i
            for (cx, cz) in st['top']:
                x, z = cx + sx * i, cz + sz * i
                if st.get('fill', True):
                    for yy in range(lf, y): P(x, yy, z, NETHER_BRICK)   # solid under the run inside the chamber
                P(x, y, z, NB_STAIRS, st['data'])
                for yy in range(y + 1, y + 4):
                    if yy <= S: P(x, yy, z, AIR)

    # 5) v4: plank sill in front of the glass doorway, iron doors with pressure plates, ladders (no stairs)
    for (x, z) in T.get('sill', []):
        P(x, S, z, *oak); ctx.surf[(x, z)] = 'struct'
    for dr in T.get('doors', []):
        x, y, z = dr['at']; ox, oz = dr['out']
        if dr.get('cut'):                                    # cut a 1-wide, 2-high passage through the wall
            for (cx, cz) in dr['cut']:
                for yy in (y, y + 1): P(cx, yy, cz, AIR)
                P(cx, y - 1, cz, *dr.get('floor', oak)); P(cx, y + 2, cz, *dr.get('ceil', oak))
        P(x, y, z, IRON_DOOR, dr['facing']); P(x, y + 1, z, IRON_DOOR, 8)
        for (px, pz) in ((x - ox, z - oz), (x + ox, z + oz)):          # plate on both sides
            P(px, y - 1, pz, *dr.get('floor', oak)); P(px, y, pz, STONE_PLATE); P(px, y + 1, pz, AIR)
    for ld in T.get('ladders', []):
        x, z = ld['at']; bx2, bz2 = ld['wall']
        for y in range(ld['y1'], ld['y2'] + 1):
            P(x, y, z, LADDER, ld['data']); P(bx2, y, bz2, STONE)
        for y in range(ld['y2'] + 1, ld['y2'] + 3):
            if y > S: P(x, y, z, AIR)
        for (cx, cz) in ld.get('clear_top', []):
            P(cx, ld['y2'] + 1, cz, AIR); P(cx, ld['y2'] + 2, cz, AIR)

    # 6) the user's hand-built pavilion (+ beacon fix) wins over everything above
    import json as _json, os as _os
    up = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'trap_user_pavilion.json')
    if T.get('user_pavilion', True) and _os.path.exists(up):
        for x, y, z, b, dd in _json.load(open(up))['blocks']: P(x, y, z, b, dd)

    ctx.notes.append('trap v4: hut x %d..%d z %d..%d walls y%d..%d roof y%d..%d beacon %d,%d,%d; hole x %d..%d z %d..%d; '
                     'mid feet y%d, low feet y%d; apron x %d..%d z %d..%d' % (
                         hx1, hx2, hz1, hz2, S + 1, wt, wt + 1, top + 1, bx, wt + 3, bz, px1, px2, pz1, pz2,
                         mf + 1, lf + 1, ap[0], ap[2], ap[1], ap[3]))
