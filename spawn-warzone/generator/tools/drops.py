"""Find walkable island cells next to an open fall (drop-down points). usage: drops.py <world> <outdir>"""
import sys, os, collections, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anvil, pngw
W, OUT = sys.argv[1], sys.argv[2]
B = {}
for cx, cz, root in anvil.world_chunks(W):
    if cx < -2 or cx > 11 or cz < -6 or cz > 4: continue
    sec = anvil.sections(root)
    for sy in sec:
        if sy < 8: continue
        for lx in range(16):
            for lz in range(16):
                for ly in range(16):
                    y = sy * 16 + ly
                    if y < 130: continue
                    bid, dv = anvil.block_at(sec, lx, y, lz)
                    if bid: B[(cx*16+lx, y, cz*16+lz)] = (bid, dv)
pickle.dump(B, open(os.path.join(OUT, 'island_blocks.pkl'), 'wb'))
PASS = {0, 6, 27, 28, 31, 32, 37, 38, 39, 40, 50, 55, 59, 63, 65, 66, 68, 69, 70, 72, 75, 76, 77, 78, 83, 93, 94, 104, 105, 106, 115, 131, 132, 141, 142, 143, 147, 148, 157, 171, 175}
def solid(p): b = B.get(p); return b is not None and b[0] not in PASS
def air(p): b = B.get(p); return b is None or b[0] in PASS
def opencol(x, y, z):  # nothing solid from y+1 down to 130
    return all(not solid((x, yy, z)) for yy in range(130, y + 2))
drops = collections.defaultdict(list)
for (x, y, z), b in B.items():
    if b[0] in PASS: continue
    yy = y + 1
    if not (air((x, yy, z)) and air((x, yy + 1, z))): continue
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, nz = x + dx, z + dz
        if air((nx, yy, nz)) and air((nx, yy + 1, nz)) and opencol(nx, yy, nz):
            drops[yy].append((nx, nz, x, z))
for yy in sorted(drops):
    pts = drops[yy]
    print('stand y', yy, 'drop edge cells', len(pts))
pickle.dump(dict(drops), open(os.path.join(OUT, 'drops.pkl'), 'wb'))
