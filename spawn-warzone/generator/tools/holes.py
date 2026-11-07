"""find enclosed empty columns (drop holes) inside the island footprint. usage: holes.py <survey.pkl>"""
import sys, pickle, collections
ground, isl = pickle.load(open(sys.argv[1], 'rb'))
xs = [k[0] for k in isl]; zs = [k[1] for k in isl]
X1, X2, Z1, Z2 = min(xs) - 1, max(xs) + 1, min(zs) - 1, max(zs) + 1
# flood fill outside from border; remaining empty = enclosed holes
out = set(); st = [(X1, Z1)]
while st:
    p = st.pop()
    if p in out or p in isl: continue
    x, z = p
    if not (X1 <= x <= X2 and Z1 <= z <= Z2): continue
    out.add(p); st += [(x+1, z), (x-1, z), (x, z+1), (x, z-1)]
holes = [(x, z) for x in range(X1, X2+1) for z in range(Z1, Z2+1) if (x, z) not in isl and (x, z) not in out]
seen = set(); comps = []
for h in holes:
    if h in seen: continue
    st = [h]; seen.add(h); c = []
    while st:
        q = st.pop(); c.append(q); x, z = q
        for n in ((x+1, z), (x-1, z), (x, z+1), (x, z-1)):
            if n in holes and n not in seen: seen.add(n); st.append(n)
    comps.append(c)
hs = set(holes)
for c in sorted(comps, key=len, reverse=True):
    cx = [p[0] for p in c]; cz = [p[1] for p in c]
    # rim: island columns around it
    rim = collections.Counter()
    for (x, z) in c:
        for n in ((x+1, z), (x-1, z), (x, z+1), (x, z-1)):
            if n in isl: rim[(isl[n][0], isl[n][1])] += 1
    print(len(c), 'x', min(cx), max(cx), 'z', min(cz), max(cz), 'rim(top y,id)', rim.most_common(5))
