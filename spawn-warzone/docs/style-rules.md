# Style rules (Astro spawn warzone)

Look: clean, open, flat, "space" PvP map. Big readable areas, few props. Not medieval, not a generic spawn.

1. **Flat first.** Surface y69 everywhere (feet y70). Height changes are 1 block (platform steps, plank borders) except
   the rock, mounds (2-4), crater (-1..-3) and the trap pit. No hills, no trees, no flowers, no tall grass, no random houses.
2. **Few materials per zone.** Fields: grass + oak planks (+ light gray clay patches in the north). Moon: light gray +
   gray clay, andesite only on mounds/rock, black clay as rare accents. Centre: quartz/clay pad, glass + nether brick paths.
   Trap: dark oak / spruce outside, pink/red/magenta glass inside. Pavilion: pink clay + dark oak.
3. **Borders are blocky and irregular** (pixel-staircase edges, quantised noise), never straight lines or perfect circles,
   except man-made parts (paths, pad, trap, pavilion).
4. **Lava cracks branch** (random walks with forks, 1-2 wide, occasional 2-3 radius pools). Never straight, never a grid.
   Open lava is 1 deep (y69, floor y68) so a player who steps in can walk out.
5. **Fire safety (live doFireTick=true):** no flammable block (planks, logs, wood stairs/slabs, wool, leaves, tall grass,
   carpets) within 5 blocks horizontally or 4 above open lava. Glass-covered lava sits at y68 with nether brick on all
   sides + below and glass above: no air touches it.
6. **Room to fight.** Keep >= 70% of each zone walkable at y70. Props (mounds, rock, arches) are sparse; arches over
   paths leave >= 5 blocks headroom.
7. **Safe drops.** Nothing harmful under the island footprint (x -14..162, z -80..58): no open lava, no pits. Under the
   drop hole (centre 44,0, r 7.5) is the landing pad. Fall damage is already off on live (AstroCore ServerFixes).
8. **No mob holes.** Under the island shadow, keep light >= 8 at feet with flush glowstone/sea lanterns (lighting region).
9. **Never touch y >= 130** (island bottom y138) and nothing outside x,z -176..175.
10. Orientation: original frames place the trap + pavilion near the north edge; they are in the NE quarter. The trap door
    faces the battlefield (west); its pit stairs are on the opposite (east) side.
