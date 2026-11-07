"""Survey a 1.8 world copy (read only): ground below the spawn island + island footprint + drop-down openings.
usage: py -3 -I survey.py <worldDir> <outDir> [x1 z1 x2 z2]
writes ground.png (top block below y<ISLAND_Y), island.png (top island block), survey.json
"""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anvil, pngw

W, OUT = sys.argv[1], sys.argv[2]
X1, Z1, X2, Z2 = (int(v) for v in sys.argv[3:7]) if len(sys.argv) > 6 else (-176, -176, 175, 175)
ISLAND_Y = 130
os.makedirs(OUT, exist_ok=True)
ground = {}   # (x,z) -> (y,id,data)  highest non-air block below ISLAND_Y
isl = {}      # (x,z) -> (ytop,id,data,ybottom,count)
idcount = collections.Counter(); gcount = collections.Counter()
for cx, cz, root in anvil.world_chunks(W):
    if cx * 16 + 15 < X1 or cx * 16 > X2 or cz * 16 + 15 < Z1 or cz * 16 > Z2: continue
    sec = anvil.sections(root)
    for lx in range(16):
        for lz in range(16):
            x, z = cx * 16 + lx, cz * 16 + lz
            if not (X1 <= x <= X2 and Z1 <= z <= Z2): continue
            g = None; top = None; bot = None; n = 0
            for y in range(255, -1, -1):
                if (y >> 4) not in sec: continue
                bid, dv = anvil.block_at(sec, lx, y, lz)
                if not bid: continue
                if y >= ISLAND_Y:
                    if top is None: top = (y, bid, dv)
                    bot = y; n += 1; idcount[bid] += 1
                elif g is None:
                    g = (y, bid, dv); gcount[bid] += 1
                    break
            if g: ground[(x, z)] = g
            if top: isl[(x, z)] = (top[0], top[1], top[2], bot, n)

def img(dct, name, ycol=True):
    rows = []
    for z in range(Z1, Z2 + 1):
        row = []
        for x in range(X1, X2 + 1):
            v = dct.get((x, z))
            if not v: row.append((10, 10, 20)); continue
            c = pngw.colour(v[1], v[2])
            if ycol:
                f = max(0.45, min(1.3, 0.6 + (v[0] - 40) / 80.0))
                c = tuple(min(255, int(k * f)) for k in c)
            if x % 16 == 0 or z % 16 == 0: c = tuple(int(k * 0.85) for k in c)
            if x == 0 or z == 0: c = (255, 0, 0)
            row.append(c)
        rows.append(row)
    pngw.write_png(os.path.join(OUT, name), rows, 2)

img(ground, 'ground.png'); img(isl, 'island.png')
ys = collections.Counter(v[0] for v in ground.values())
summary = {
    'box': [X1, Z1, X2, Z2],
    'ground_top_ids': gcount.most_common(20),
    'ground_heights': sorted(ys.items()),
    'island_columns': len(isl),
    'island_ids': idcount.most_common(30),
    'island_x': [min(k[0] for k in isl), max(k[0] for k in isl)] if isl else None,
    'island_z': [min(k[1] for k in isl), max(k[1] for k in isl)] if isl else None,
    'island_bottom_min': min(v[3] for v in isl.values()) if isl else None,
}
json.dump(summary, open(os.path.join(OUT, 'survey.json'), 'w'), indent=1)
import pickle; pickle.dump((ground, isl), open(os.path.join(OUT, 'survey.pkl'), 'wb'))
print(json.dumps(summary)[:3000])
