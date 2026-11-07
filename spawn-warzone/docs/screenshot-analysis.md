# Screenshot analysis (21 reference frames, 2026-11-06)

**Superseded for file locations:** the images now live permanently in
`C:\Users\levir\wt-warzone\AstroWarzone\references\astro-original\` (catalog IDs R01..R23; the `#` below = the old
028e file number, mapped to R-IDs in `REFERENCE_CATALOG.md`). The Temp paths below were cleaned up on 2026-11-06.

Source: user-supplied frames (`...\028e113b-...\images\1.png .. 21.webp`). 21 files = 18 distinct images
(6=7, 18=19 are duplicates; 1.png is the AstroPvP logo, not the map). Frames come from at least three videos:
**Fredo** ("Violent" faction, pre-reset, x -272..-118), **Devil** (x -234), **XaitX** ("doa"/"Quarterback",
Astro Reborn, x -177..72, z -192..98). Player effects, nametags, particles, the pack's colours and the big obsidian
"derp" walls (frames 4, 7, 8) are ignored. The pack recolours blocks (smooth gray textures, darker wood), so block
choices below are the closest vanilla 1.8 ids, not certainties.

| # (028e) | HUD coords (feet) | facing | What it shows (map only) |
|---|---|---|---|
| 1.png | - | - | AstroPvP logo, not a map frame |
| 2 | x?, z -91 | ? | night, wide flat **light-gray "moon" platforms** with jagged 1-block edges, darker gray stepped blocks in the distance |
| 3.png | - | - | **big jagged volcanic rock**: light gray mass with darker gray block patches, spiky silhouette, ~25-30 high, wide base on a flat gray floor |
| 4 | -272, -26 | E | oak-plank floor + grass patches with blocky borders; low gray ridge in the distance |
| 5 | -270, -20 | N | grass field meeting oak planks along a stepped (pixel-staircase) border; raised plank layers in the distance |
| 6/7 | -118, -77 | NE | dark-gray platform blocks stepping up, **open lava pools/channels** right next to them ("can't destroy in Warzone") |
| 8 | 56, 77, -185 (flying) | E | dark brown plank floor with **light-gray irregular patches**; obsidian derp walls (ignore) |
| 9 | 41, 56, -167 | W | **inside the trap**: pink + red (checker) stained-glass interior, low ceiling, players fighting; feet y56 |
| 10.png | ? | ? | close-up: small **pavilion** with pink pillars and a brown **stepped roof** + pink beacon beam |
| 11 | 9, 70, -155 | E | plank floor + light-gray patches; the pavilion ~20-25 ahead (east); pink beam |
| 12 | 19, 73, -192 | S | "Leaving Warzone / Entering Chaos" => **warzone edge at z ~ -192**; pavilion on the left; gray zone far ahead |
| 13 | -234, -21 | SE | gray moon floor, low gray steps, orange lava streaks far off |
| 14 | 72, 70, 98 | N | plank floor, white beacon beam |
| 15 | -152, 78, -175 | S | plank floor with light-gray patches, open sky |
| 16 | - | - | plank floor; small **gray/brown mounds** on the horizon |
| 17 | -177, 87, -99 | E | (tab list) aerial: **gray volcanic area with branching lava cracks**, a darker gray rock patch, planks on the north (left) side |
| 18/19 | - | - | aerial: planks (left) meet gray; **round crater** (stepped rings) and **branching lava cracks** |
| 20 | 43, 70, -161 | W | top of the trap: dark-wood walls, purple/magenta glass, red outline (pressure-plate/selection), red/green checker floor below |
| 21 | 41, 62, -162 | down/W | in the trap one level lower (feet y62): red/green checker glass, nether-brick-dark frame |

## Facts used
- Floor level: XaitX's frames read feet **y70** on the floor => surface block **y69**. We keep y69.
- Trap levels: rim/top y70 (frame 20), room level y62 (frame 21, 8 below), lowest chamber y56 (frame 9, 14 below).
  Brief says "pit about 7 deep": we model **room floor = surface (y69), pit floor y62 (7 deep, feet y63)**; the y56 chamber
  is an open question (parameter `trap.lower_chamber`, off).
- Trap at original (41..43, -167..-161), near the north warzone edge (z -192). Pavilion ~10-15 blocks away (frames 11, 12).
- Warzone edge z ~ -192 in XaitX's map; Fredo/Devil frames at x -272/-234 are inside their warzone, so their map was
  wider in x (or a different season). Fredo/Devil coordinates are used for **direction only** (west = grass/wood fields,
  then gray moon, then lava).
- Lava: open lava cracks/pools in the gray area (frames 6/7, 17, 18). Glass-covered lava is NOT visible in any frame;
  it is from the brief. Decision (documented in the blueprint): lava 1 block **under** flush glass, nether-brick curbs beside.

## Coordinate transform (original -> our world)
Our warzone is fixed by WorldGuard `spawnwarzone` + Factions WarZone chunks: x,z -176..175, and the spawn island sits
east of centre (x -14..162, z -80..58), drop hole at (44, 0). Transform used for XaitX frames (trustworthy, consistent
with a +-192 warzone):

    x' = round(0.92 * (x + 100)),  z' = round(0.92 * (z + 8)),  y' = y

0.92 = 176/192 shrinks the +-192 box into ours; +100 in x shifts the original "east" features (trap, pavilion) over to
the NE corner so the open west keeps the grass + moon zones from Fredo's frames. Results: trap (42,-163) -> (131,-143),
pavilion (~34,-160) -> (123,-155) [moved to (112,-140) to leave a gap], XaitX wood (9,-155) -> (100,-135),
(72,98) -> (158,98), aerial (-177,-99) -> (-71,-84), lava (-118,-77) -> (-17,-78), edge z -192 -> -169 (box -176).
(Numbers corrected 2026-11-06: R12 (158,98), R15 (-71,-84), north edge -169.)

**RETIRED 2026-11-06: the user chose option A (original HUD coordinates 1:1, no transform, no shift); the v1 transform above is no longer used.**
Fredo/Devil (x < -192) fall outside the box and are used as directions only.

## Still uncertain
- Exact block types under the pack (wool vs stained clay for grays; oak vs spruce planks). Chosen: stained clay (non-flammable).
- Whether the trap's checker floor is glass over the pit (frames 20/21) or a solid floor. Chosen: solid pit, glass-free.
- The y56 chamber, the red lines in frame 20, the white beam in frame 14.
- Real size/shape of the original rock; the frame has no coordinates. Chosen ~34x26 base, ~30 high, E-W tunnel.
