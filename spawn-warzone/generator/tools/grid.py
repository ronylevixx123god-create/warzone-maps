"""Block grid for 1.8 legacy ids + MCEdit/WorldEdit .schematic writer/reader (no external libraries).

Grid covers world x [x0, x0+w), y [y0, y0+h), z [z0, z0+l). Unset cells are 'keep' (0xFFFF marker in a separate mask)
so region scripts can be layered: a cell is only written when a script sets it. Air is a real value (id 0) and is
written as air when the schematic is pasted with 'air'.
"""
import gzip, struct


class Grid:
    def __init__(self, x0, y0, z0, w, h, l):
        self.x0, self.y0, self.z0, self.w, self.h, self.l = x0, y0, z0, w, h, l
        n = w * h * l
        self.ids = bytearray(n)
        self.data = bytearray(n)
        self.set_mask = bytearray(n)   # 1 = this cell was written by some region
        self.owner = bytearray(n)      # index of the region that wrote it last (for per-region exports)
        self.cur_owner = 0

    def idx(self, x, y, z):
        return ((y - self.y0) * self.l + (z - self.z0)) * self.w + (x - self.x0)

    def inside(self, x, y, z):
        return self.x0 <= x < self.x0 + self.w and self.y0 <= y < self.y0 + self.h and self.z0 <= z < self.z0 + self.l

    def set(self, x, y, z, bid, data=0, owner=None):
        if not self.inside(x, y, z):
            return False
        i = self.idx(x, y, z)
        self.ids[i] = bid; self.data[i] = data; self.set_mask[i] = 1
        self.owner[i] = self.cur_owner if owner is None else owner
        return True

    def get(self, x, y, z):
        if not self.inside(x, y, z):
            return None
        i = self.idx(x, y, z)
        return (self.ids[i], self.data[i]) if self.set_mask[i] else None

    def column_top(self, x, z, ymax=None):
        """highest y with a non-air set block (or None)"""
        ymax = self.y0 + self.h - 1 if ymax is None else ymax
        for y in range(ymax, self.y0 - 1, -1):
            b = self.get(x, y, z)
            if b and b[0]:
                return y
        return None

    # ------------------------------------------------------------------ schematic output
    def write_schematic(self, path, box=None, owners=None):
        """box = (x1,y1,z1,x2,y2,z2) inclusive world coords (default: whole grid). owners = set of owner ids to include
        (others become air if inside box... no: others are kept as they are in the composite). Unset cells become air."""
        if box is None:
            box = (self.x0, self.y0, self.z0, self.x0 + self.w - 1, self.y0 + self.h - 1, self.z0 + self.l - 1)
        x1, y1, z1, x2, y2, z2 = box
        W, H, L = x2 - x1 + 1, y2 - y1 + 1, z2 - z1 + 1
        ids = bytearray(W * H * L); dat = bytearray(W * H * L)
        for y in range(y1, y2 + 1):
            for z in range(z1, z2 + 1):
                row_out = ((y - y1) * L + (z - z1)) * W
                if not (self.y0 <= y < self.y0 + self.h and self.z0 <= z < self.z0 + self.l):
                    continue
                for x in range(max(x1, self.x0), min(x2, self.x0 + self.w - 1) + 1):
                    i = self.idx(x, y, z)
                    if self.set_mask[i] and (owners is None or self.owner[i] in owners):
                        ids[row_out + x - x1] = self.ids[i]; dat[row_out + x - x1] = self.data[i]
        write_schematic(path, W, H, L, ids, dat, origin=(x1, y1, z1))
        return (W, H, L)


# ---------------------------------------------------------------------- NBT writer
def _s(name):
    b = name.encode('utf-8'); return struct.pack('>H', len(b)) + b


def tag_short(n, v): return b'\x02' + _s(n) + struct.pack('>h', v)
def tag_int(n, v): return b'\x03' + _s(n) + struct.pack('>i', v)
def tag_string(n, v): return b'\x08' + _s(n) + _s(v)
def tag_bytes(n, v): return b'\x07' + _s(n) + struct.pack('>i', len(v)) + bytes(v)
def tag_list_empty(n, et=10): return b'\x09' + _s(n) + bytes([et]) + struct.pack('>i', 0)


def write_schematic(path, W, H, L, ids, dat, origin=(0, 0, 0)):
    body = (tag_short('Width', W) + tag_short('Height', H) + tag_short('Length', L) + tag_string('Materials', 'Alpha')
            + tag_bytes('Blocks', ids) + tag_bytes('Data', dat) + tag_list_empty('Entities') + tag_list_empty('TileEntities')
            + tag_int('WEOriginX', origin[0]) + tag_int('WEOriginY', origin[1]) + tag_int('WEOriginZ', origin[2])
            + tag_int('WEOffsetX', 0) + tag_int('WEOffsetY', 0) + tag_int('WEOffsetZ', 0))
    nbt = b'\x0a' + _s('Schematic') + body + b'\x00'
    with gzip.open(path, 'wb') as f:
        f.write(nbt)


def read_schematic(path):
    """returns (W,H,L, ids, data, origin) for our own files (simple parser)"""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import anvil
    root = anvil.parse(gzip.open(path).read())
    g = lambda k: root[k][1]
    org = (g('WEOriginX'), g('WEOriginY'), g('WEOriginZ')) if 'WEOriginX' in root else (0, 0, 0)
    return g('Width'), g('Height'), g('Length'), g('Blocks'), g('Data'), org
