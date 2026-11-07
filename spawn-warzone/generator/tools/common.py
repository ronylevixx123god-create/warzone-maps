"""Shared helpers for region scripts: deterministic noise, zone map access, block constants."""
import math, random

# --- 1.8 ids ------------------------------------------------------------------------------------------------------
AIR, STONE, GRASS, DIRT, PLANKS, GLASS, LAVA = 0, 1, 2, 3, 5, 20, 11
SLAB_STONE, SLAB_WOOD = 44, 126
OAK_STAIRS, DARKOAK_STAIRS, NB_STAIRS = 53, 164, 114
CLAY = 159; SGLASS = 95; LOG = 17
NETHER_BRICK, NB_FENCE = 112, 113
QUARTZ, GLOWSTONE, SEA_LANTERN = 155, 89, 169
IRON_DOOR, STONE_PLATE, BEACON, IRON_BLOCK = 71, 70, 138, 42
LADDER = 65
CLAYBLOCK, COAL_BLOCK = 82, 173
# stained clay / glass colours (159:9 cyan clay = neutral dark gray in vanilla 1.8)
WHITE, MAGENTA, PINK, GRAY, LGRAY, CYAN, RED, BLACK = 0, 2, 6, 7, 8, 9, 14, 15
# neutral grays used for the moon/rock: light = clay block 82, mid = polished andesite 1:6, dark = cyan clay 159:9
MOON_LIGHT, MOON_MID, MOON_DARK, MOON_DARKEST = (82, 0), (1, 6), (159, 9), (173, 0)
FLAMMABLE = {5, 17, 162, 53, 134, 135, 136, 163, 164, 126, 35, 18, 161, 31, 171, 85, 107, 183, 184, 185, 186, 187, 47}


def hash2(x, z, seed):
    h = (x * 374761393 + z * 668265263 + seed * 2147483647) & 0xffffffff
    h = ((h ^ (h >> 13)) * 1274126177) & 0xffffffff
    return ((h ^ (h >> 16)) & 0xffffff) / float(0xffffff)


def vnoise(x, z, scale, seed):
    """smooth value noise 0..1"""
    fx, fz = x / scale, z / scale
    x0, z0 = math.floor(fx), math.floor(fz)
    tx, tz = fx - x0, fz - z0
    tx = tx * tx * (3 - 2 * tx); tz = tz * tz * (3 - 2 * tz)
    a = hash2(x0, z0, seed); b = hash2(x0 + 1, z0, seed); c = hash2(x0, z0 + 1, seed); d = hash2(x0 + 1, z0 + 1, seed)
    return (a * (1 - tx) + b * tx) * (1 - tz) + (c * (1 - tx) + d * tx) * tz


def fbm(x, z, scale, seed, octaves=3):
    v = 0; amp = 1; tot = 0
    for o in range(octaves):
        v += vnoise(x, z, scale / (2 ** o), seed + o * 101) * amp
        tot += amp; amp *= 0.5
    return v / tot


def stretch(v, k=2.6):
    """fbm values cluster around 0.5; stretch them to roughly 0..1 so share thresholds mean what they say"""
    return max(0.0, min(1.0, (v - 0.5) * k + 0.5))


def quant(v, q):
    return (v // q) * q


class Ctx:
    """shared state between regions: zone map, protected cells, the blueprint, rng"""
    def __init__(self, bp):
        self.bp = bp
        self.zone = {}          # (x,z) -> 'west'|'fields'|'north'|'moon'
        self.surf = {}          # (x,z) -> 'grass'|'wood'|'gray'|'moon'|'platform'|'lava'|'path'|'pad'|'struct'|'rock'|'crater'
        self.reserved = set()   # (x,z) columns owned by structures (later regions must not put lava etc.)
        self.island = set()     # island footprint columns (exact, from survey)
        self.rng = random.Random(bp['seed'])
        self.notes = []

    def in_box(self, x, z):
        b = self.bp['box']
        return b[0] <= x <= b[2] and b[1] <= z <= b[3]

    def near_island(self, x, z, m):
        f = self.bp['island']['footprint']
        return f[0] - m <= x <= f[2] + m and f[1] - m <= z <= f[3] + m
