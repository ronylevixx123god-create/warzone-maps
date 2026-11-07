import sys, os, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pngw
OUT = sys.argv[1]; X1, Z1, X2, Z2, SC = (int(v) for v in sys.argv[2:7])
B = pickle.load(open(os.path.join(OUT, 'island_blocks.pkl'), 'rb'))
seen, comps, dset = pickle.load(open(os.path.join(OUT, 'reach.pkl'), 'rb'))
top = {}
for (x, y, z), b in B.items():
    if (x, z) not in top or top[(x, z)][0] < y: top[(x, z)] = (y, b)
walk = {}
for (x, y, z) in seen: walk[(x, z)] = max(walk.get((x, z), 0), y)
rows = []
for z in range(Z1, Z2 + 1):
    row = []
    for x in range(X1, X2 + 1):
        if (x, z) in dset: c = (255, 0, 0)
        elif (x, z) in top:
            y, b = top[(x, z)]; c = pngw.colour(*b)
            if (x, z) in walk: c = tuple(int(k * 0.6 + 100 * 0.4) for k in c)
        else: c = (0, 0, 40)
        if x == 0 and z == 0: c = (0, 255, 0)
        if x % 10 == 0 and z % 10 == 0: c = (255, 255, 0)
        row.append(c)
    rows.append(row)
pngw.write_png(os.path.join(OUT, sys.argv[7]), rows, SC)
