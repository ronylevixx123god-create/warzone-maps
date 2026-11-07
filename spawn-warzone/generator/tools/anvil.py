"""Minimal NBT + Anvil (1.8) reader."""
import gzip, os, struct, zlib


def _read(b, p, t):
    if t == 1: return struct.unpack_from('>b', b, p)[0], p + 1
    if t == 2: return struct.unpack_from('>h', b, p)[0], p + 2
    if t == 3: return struct.unpack_from('>i', b, p)[0], p + 4
    if t == 4: return struct.unpack_from('>q', b, p)[0], p + 8
    if t == 5: return struct.unpack_from('>f', b, p)[0], p + 4
    if t == 6: return struct.unpack_from('>d', b, p)[0], p + 8
    if t == 7:
        n = struct.unpack_from('>i', b, p)[0]; p += 4
        return b[p:p + n], p + n
    if t == 8:
        n = struct.unpack_from('>H', b, p)[0]; p += 2
        return b[p:p + n].decode('utf-8', 'replace'), p + n
    if t == 9:
        et = b[p]; n = struct.unpack_from('>i', b, p + 1)[0]; p += 5
        out = []
        for _ in range(n):
            v, p = _read(b, p, et); out.append(v)
        return ('list', et, out), p
    if t == 10:
        d = {}
        while True:
            ct = b[p]; p += 1
            if ct == 0: return d, p
            n = struct.unpack_from('>H', b, p)[0]; p += 2
            name = b[p:p + n].decode('utf-8', 'replace'); p += n
            v, p = _read(b, p, ct); d[name] = (ct, v)
    if t == 11:
        n = struct.unpack_from('>i', b, p)[0]; p += 4
        return list(struct.unpack_from('>%di' % n, b, p)), p + 4 * n
    raise ValueError('tag %d' % t)


def parse(b):
    assert b[0] == 10
    n = struct.unpack_from('>H', b, 1)[0]
    v, _ = _read(b, 3 + n, 10)
    return v


def val(d, *path):
    for k in path:
        d = d[k][1]
    return d


def level_dat(path):
    return parse(gzip.open(path).read())


def region_chunks(path):
    """yield (cx, cz, root) for every chunk in a region file"""
    data = open(path, 'rb').read()
    for i in range(1024):
        off = int.from_bytes(data[i * 4:i * 4 + 3], 'big'); cnt = data[i * 4 + 3]
        if off == 0 or cnt == 0: continue
        p = off * 4096
        ln = struct.unpack_from('>i', data, p)[0]; comp = data[p + 4]
        raw = data[p + 5:p + 4 + ln]
        raw = zlib.decompress(raw) if comp == 2 else gzip.decompress(raw)
        root = parse(raw)
        lvl = val(root, 'Level')
        yield val(lvl, 'xPos'), val(lvl, 'zPos'), root


def world_chunks(world):
    rd = os.path.join(world, 'region')
    for f in sorted(os.listdir(rd)):
        if f.endswith('.mca'):
            yield from region_chunks(os.path.join(rd, f))


def sections(root):
    """{sectionY: (blocks bytes, data bytes, add bytes|None)}"""
    out = {}
    for s in val(root, 'Level', 'Sections')[2]:
        y = s['Y'][1]
        out[y] = (s['Blocks'][1], s['Data'][1], s['Add'][1] if 'Add' in s else None)
    return out


def block_at(sec, x, y, z):
    """x,z 0..15 local, y 0..255 -> (id, data)"""
    s = sec.get(y >> 4)
    if s is None: return 0, 0
    i = ((y & 15) << 8) | (z << 4) | x
    bid = s[0][i]
    if s[2] is not None:
        a = s[2][i >> 1]; bid |= ((a >> 4) if i & 1 else (a & 15)) << 8
    d = s[1][i >> 1]
    return bid, ((d >> 4) if i & 1 else (d & 15))
