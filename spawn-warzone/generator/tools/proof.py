"""Toolchain proof: tiny schematic with grass, oak planks, stone, glass, stairs, slab, iron door + plates.
Expected after paste at (X,Y,Z): see printed checklist (relative coords)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grid import Grid
g = Grid(0, 0, 0, 9, 6, 9)
for x in range(9):
    for z in range(9):
        g.set(x, 0, z, 2 if (x + z) % 3 else 5)          # grass / oak planks floor
for x in range(2, 7):
    for z in range(2, 7):
        for y in range(1, 4):
            edge = x in (2, 6) or z in (2, 6)
            g.set(x, y, z, (1 if y < 3 else 20) if edge else 0)   # stone walls, glass top row
g.set(4, 1, 2, 71, 1); g.set(4, 2, 2, 71, 8)            # iron door in north wall, facing north... (data 1 = facing south? checked in-game)
g.set(4, 1, 1, 70, 0); g.set(4, 1, 3, 70, 0)            # pressure plates outside + inside
g.set(4, 3, 2, 44, 0)                                    # stone slab (bottom) above the doorway
for x in range(2, 7): g.set(x, 4, 7, 53, 2)              # oak stairs row (data 2) beside, to check orientation
g.set(0, 1, 0, 95, 6); g.set(1, 1, 0, 95, 14)            # pink + red stained glass
g.write_schematic(sys.argv[1])
print('wrote', sys.argv[1])
