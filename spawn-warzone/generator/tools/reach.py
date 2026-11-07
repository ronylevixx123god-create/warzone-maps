"""Walk the island from /spawn (BFS, 1-block steps up, any fall) and list where a player falls off into open air
(the real drop-down points). usage: reach.py <outdir with island_blocks.pkl> [sx sy sz]"""
import sys, os, pickle, collections
OUT = sys.argv[1]
B = pickle.load(open(os.path.join(OUT, 'island_blocks.pkl'), 'rb'))
S = tuple(int(v) for v in sys.argv[2:5]) if len(sys.argv) > 4 else (0, 153, 0)
PASS = {0, 6, 27, 28, 31, 32, 37, 38, 39, 40, 50, 55, 59, 63, 65, 66, 68, 69, 70, 72, 75, 76, 77, 78, 83, 93, 94, 104, 105, 106, 115, 131, 132, 141, 142, 143, 147, 148, 157, 171, 175, 64, 71, 96, 167}  # doors/trapdoors passable
TALL = {85, 113, 188, 189, 190, 191, 192, 139, 101, 102, 160, 107, 183, 184, 185, 186, 187}
def solid(p): b = B.get(p); return b is not None and b[0] not in PASS
def free(p): return not solid(p)
def standable(x, y, z):
    b = B.get((x, y - 1, z)); return b is not None and b[0] not in PASS and b[0] not in TALL and free((x, y, z)) and free((x, y + 1, z))
def fall(x, y, z):
    for yy in range(y, 129, -1):
        if solid((x, yy - 1, z)):
            return yy if (B[(x, yy - 1, z)][0] not in TALL) else None
    return 'VOID'
seen = {S}; q = collections.deque([S]); drops = []
while q:
    x, y, z = q.popleft()
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, nz = x + dx, z + dz
        for ny in (y, y + 1):
            if ny == y + 1 and solid((x, y + 2, z)): continue
            if standable(nx, ny, nz):
                n = (nx, ny, nz)
                if n not in seen: seen.add(n); q.append(n)
                break
        else:
            if free((nx, y, nz)) and free((nx, y + 1, nz)):
                r = fall(nx, y, nz)
                if r == 'VOID': drops.append((nx, y, nz, x, z))
                elif r is not None:
                    n = (nx, r, nz)
                    if n not in seen and standable(*n): seen.add(n); q.append(n)
print('reachable cells', len(seen), 'y range', min(p[1] for p in seen), max(p[1] for p in seen))
# cluster drops
dset = {}
for d in drops: dset[(d[0], d[2])] = d[1]
seenc = set(); comps = []
for p in dset:
    if p in seenc: continue
    st = [p]; seenc.add(p); c = []
    while st:
        a = st.pop(); c.append(a)
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                n = (a[0] + dx, a[1] + dz)
                if n in dset and n not in seenc: seenc.add(n); st.append(n)
    comps.append(c)
for c in sorted(comps, key=len, reverse=True):
    xs = [p[0] for p in c]; zs = [p[1] for p in c]; ys = [dset[p] for p in c]
    print('DROP', len(c), 'cells x', min(xs), max(xs), 'z', min(zs), max(zs), 'from y', min(ys), max(ys))
pickle.dump((seen, comps, dset), open(os.path.join(OUT, 'reach.pkl'), 'wb'))
