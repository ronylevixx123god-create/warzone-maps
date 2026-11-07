"""Tiny PNG writer (no PIL). rows = list of rows of (r,g,b)."""
import struct, zlib


def write_png(path, rows, scale=1):
    h = len(rows); w = len(rows[0])
    raw = bytearray()
    for row in rows:
        line = bytearray()
        for (r, g, b) in row:
            line += bytes((r, g, b)) * scale
        for _ in range(scale):
            raw.append(0); raw += line
    def chunk(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w * scale, h * scale, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')
    open(path, 'wb').write(png)


# rough 1.8 top colours by block id (data ignored except wool/clay/glass handled by caller)
COL = {0: (20, 20, 30), 1: (125, 125, 125), 2: (95, 160, 60), 3: (134, 96, 67), 4: (110, 110, 110), 5: (160, 130, 80),
       7: (50, 50, 50), 8: (50, 80, 200), 9: (50, 80, 200), 10: (230, 100, 20), 11: (230, 100, 20), 12: (220, 210, 160),
       13: (130, 120, 120), 17: (100, 80, 50), 18: (60, 120, 40), 20: (200, 230, 240), 24: (210, 200, 150),
       35: (220, 220, 220), 43: (150, 150, 150), 44: (160, 160, 160), 49: (20, 15, 30), 53: (160, 130, 80),
       85: (160, 130, 80), 87: (110, 50, 50), 89: (230, 200, 120), 95: (230, 150, 170), 98: (120, 120, 120),
       102: (200, 230, 240), 109: (120, 120, 120), 112: (50, 25, 30), 114: (50, 25, 30), 126: (160, 130, 80),
       155: (235, 230, 225), 159: (160, 100, 80), 160: (230, 150, 170), 172: (150, 90, 65), 173: (20, 20, 20),
       44: (160, 160, 160), 82: (160, 165, 175), 168: (100, 160, 150), 169: (200, 230, 220)}


def colour(bid, data=0):
    if bid == 5 or bid == 126 or bid == 53:  # planks by species
        return [(160, 130, 80), (110, 80, 50), (195, 180, 125), (155, 110, 80), (170, 90, 50), (65, 45, 25)][data & 7 if data < 6 else 0]
    if bid == 159 or bid == 35 or bid == 95 or bid == 160:
        pal = [(210, 180, 160), (160, 85, 40), (150, 90, 110), (115, 110, 135), (185, 135, 35), (105, 115, 55), (160, 75, 75),
               (57, 42, 35), (135, 105, 95), (85, 90, 90), (118, 70, 85), (75, 60, 90), (77, 50, 35), (75, 82, 42), (143, 61, 46), (37, 22, 16)]
        c = pal[data & 15]
        return c
    return COL.get(bid, (255, 0, 255))
