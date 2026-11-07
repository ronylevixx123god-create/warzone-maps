"""Build the spawn warzone from blueprint.json into one composite grid, run static safety checks, write schematics,
a top-down render and a manifest with exact paste coordinates.

  py -3 -I build.py                       all regions; writes out/warzone_full.schematic + every region crop
  py -3 -I build.py --only trap rock      composite is rebuilt, only these crops are written
  py -3 -I build.py --box x1 z1 x2 z2     also write out/wz_box.schematic (composite crop of that column box, incl. air)
  py -3 -I build.py --set rock.height=36  override any blueprint value for this run (dotted path, JSON value)

Paste on the test server (min corner): wz paste <name> <minX> <minY> <minZ> air   (see out/manifest.json)
"""
import sys, os, json, time, pickle, importlib, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'tools')); sys.path.insert(0, os.path.join(HERE, 'regions'))
from grid import Grid
from common import Ctx, LAVA, AIR, FLAMMABLE, GLOWSTONE
import pngw

ORDER = ['terrain', 'landing', 'lava_paths', 'moon', 'rock', 'trap', 'pavilion', 'lighting']


def main(argv):
    bp = json.load(open(os.path.join(HERE, 'blueprint.json')))
    only, box = None, None
    i = 0
    while i < len(argv):
        if argv[i] == '--only':
            only = []
            while i + 1 < len(argv) and not argv[i + 1].startswith('--'): only.append(argv[i + 1]); i += 1
        elif argv[i] == '--box':
            box = [int(v) for v in argv[i + 1:i + 5]]; i += 4
        elif argv[i] == '--set':
            k, v = argv[i + 1].split('=', 1); i += 1
            d = bp; ks = k.split('.')
            for kk in ks[:-1]: d = d[kk]
            d[ks[-1]] = json.loads(v)
        i += 1
    out = os.path.join(HERE, 'out'); os.makedirs(out, exist_ok=True)
    x1, z1, x2, z2 = bp['box']
    G = Grid(x1, bp['y_min'], z1, x2 - x1 + 1, bp['y_max'] - bp['y_min'] + 1, z2 - z1 + 1)
    ctx = Ctx(bp)
    sp = os.path.join(HERE, bp['island']['survey'])
    ground, isl = pickle.load(open(sp, 'rb'))
    ctx.island = set(k for k in isl if ctx.in_box(*k))
    for n, name in enumerate(ORDER, start=1):
        t = time.time()
        G.cur_owner = n
        importlib.import_module(name).build(G, bp, ctx)
        print('%-11s %5.1fs  %s' % (name, time.time() - t, ctx.notes[-1] if ctx.notes else ''))
    problems = checks(G, bp, ctx)
    # outputs
    manifest = {'built': time.strftime('%Y-%m-%d %H:%M:%S'), 'blueprint': bp, 'notes': ctx.notes, 'checks': problems, 'schematics': {}}
    def write(name, b):
        t = time.time()
        dims = G.write_schematic(os.path.join(out, name + '.schematic'), b)
        manifest['schematics'][name] = {'min': [b[0], b[1], b[2]], 'max': [b[3], b[4], b[5]], 'size': dims,
                                        'paste': 'wz paste %s %d %d %d air' % (name, b[0], b[1], b[2])}
        print('wrote %s %s (%.1fs)' % (name, dims, time.time() - t))
    ymin, ymax = bp['y_min'], bp['y_max']
    if not only:
        write('warzone_full', (x1, ymin, z1, x2, ymax, z2))
    for n, name in enumerate(ORDER, start=1):
        if only and name not in only: continue
        if name in ('terrain', 'lighting'): continue
        bb = owner_box(G, n)
        if bb: write('wz_' + name, (bb[0] - 1, ymin, bb[2] - 1, bb[1] + 1, ymax, bb[3] + 1))
    if box:
        write('wz_box', (box[0], ymin, box[1], box[2], ymax, box[3]))
    render(G, bp, ctx, os.path.join(out, 'render_top.png'))
    mp = os.path.join(out, 'manifest.json')
    if os.path.exists(mp):                      # keep entries of crops not rewritten this run
        old = json.load(open(mp)).get('schematics', {})
        old.update(manifest['schematics']); manifest['schematics'] = old
    json.dump(manifest, open(mp, 'w'), indent=1)
    print('checks:', 'OK' if not any(problems.values()) else json.dumps(problems)[:2000])


def owner_box(G, n):
    xs0 = zs0 = 10 ** 9; xs1 = zs1 = -10 ** 9; found = False
    W, L = G.w, G.l
    # fast scan: per (y,z) row search owner bytes
    ob = bytes(G.owner); key = bytes([n])
    for y in range(G.h):
        for z in range(L):
            row = ob[(y * L + z) * W:(y * L + z + 1) * W]
            a = row.find(key)
            if a < 0: continue
            b = row.rfind(key)
            found = True
            xs0 = min(xs0, a); xs1 = max(xs1, b); zs0 = min(zs0, z); zs1 = max(zs1, z)
    if not found: return None
    return (G.x0 + xs0, G.x0 + xs1, G.z0 + zs0, G.z0 + zs1)


def checks(G, bp, ctx):
    S = bp['surface']; f = bp['island']['footprint']
    sealed, fire, under_island, high = [], [], [], []
    lava = []
    for y in range(G.y0, G.y0 + G.h):
        for z in range(G.z0, G.z0 + G.l):
            base = ((y - G.y0) * G.l + (z - G.z0)) * G.w
            row = G.ids[base:base + G.w]
            start = 0
            while True:
                a = row.find(bytes([LAVA]), start)
                if a < 0: break
                lava.append((G.x0 + a, y, z)); start = a + 1
    for (x, y, z) in lava:
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, -1, 0)):
            b = G.get(x + dx, y + dy, z + dz)
            if b is None or b[0] == AIR: sealed.append((x, y, z)); break
        open_top = (G.get(x, y + 1, z) or (0, 0))[0] == AIR
        if open_top:
            if f[0] <= x <= f[2] and f[1] <= z <= f[3]: under_island.append((x, y, z))
            hit = False
            for dx in range(-5, 6):
                for dz in range(-5, 6):
                    for dy in range(0, 5):
                        b = G.get(x + dx, y + dy, z + dz)
                        if b and b[0] in FLAMMABLE: fire.append((x, y, z, x + dx, y + dy, z + dz)); hit = True; break
                    if hit: break
                if hit: break
    print('lava cells %d (open %d)' % (len(lava), sum(1 for (x, y, z) in lava if (G.get(x, y + 1, z) or (0, 0))[0] == AIR)))
    return {'lava_not_sealed': sealed[:20], 'flammable_near_open_lava': fire[:20], 'open_lava_under_island': under_island[:20],
            'y_max_ok': G.y0 + G.h - 1 < 130}


def render(G, bp, ctx, path):
    import pngw
    x1, z1, x2, z2 = bp['box']; f = bp['island']['footprint']; S = bp['surface']
    h = bp['island']['drop_holes'][0]
    rows = []
    for z in range(z1, z2 + 1):
        row = []
        for x in range(x1, x2 + 1):
            y = G.column_top(x, z)
            if y is None: row.append((0, 0, 0)); continue
            b = G.get(x, y, z)
            c = pngw.colour(*b)
            if b[0] == LAVA: c = (235, 110, 20)
            if b[0] == GLOWSTONE: c = (255, 230, 140)
            if b[0] == 20: c = (190, 225, 235)
            sh = max(0.55, min(1.45, 1 + (y - S) * 0.06))
            c = tuple(min(255, int(k * sh)) for k in c)
            if (x, z) in ctx.island and ((x + z) % 6 == 0): c = tuple(int(k * 0.75) for k in c)   # island shadow hatch
            if abs(math.hypot(x - h['x'], z - h['z']) - h['r']) < 0.5: c = (0, 220, 255)               # drop hole outline
            if (x in (f[0], f[2]) and f[1] <= z <= f[3]) or (z in (f[1], f[3]) and f[0] <= x <= f[2]): c = (0, 160, 255)
            if x % 32 == 0 and z % 32 == 0: c = (255, 255, 255)
            row.append(c)
        rows.append(row)
    pngw.write_png(path, rows, 2)


if __name__ == '__main__':
    main(sys.argv[1:])
