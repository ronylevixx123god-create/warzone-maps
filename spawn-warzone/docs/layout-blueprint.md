# Layout blueprint (prototype v1, 2026-11-06)

World: live main `world` (copy on AstroPvP-WarzoneTest). All numbers live in `AstroWarzone/blueprint.json`; this doc
explains them. Coordinates are real world coordinates (block x, y, z). Transform from the original frames: see
`screenshot-analysis.md` (x' = 0.92(x+100), z' = 0.92(z+8)); with it R12 (72,98) -> (158,98), R15 (-177,-99) -> (-71,-84),
north edge z -192 -> -169 (corrected 2026-11-06).
**2026-11-06: the user chose option A (original HUD coordinates 1:1, no transform, no shift), so the v1 transform is retired.**

## Frame
- Warzone box = WG `spawnwarzone` + Factions WarZone chunks -11..10: **x -176..175, z -176..175** (352 x 352).
- Generated volume y 50..120 (schematic `warzone_full`, 352x71x352, min corner -176 50 -176). y 50..65 stone,
  66..68 dirt, **surface y69, players stand y70**, y70..120 cleared to air (old ocean/trees/hills inside the box are gone;
  outside the box nothing changes, so the box edge is a 7-block cliff into the ocean, or into the SW hills).
- Spawn island (not touched): x -14..162, y 138..220, z -80..58, /spawn 0.5 153 0.5. **Drop-down: round 15-wide hole in the
  y149 floor, x 37..51 z -7..7, centre (44, 0)**, 44 blocks east of /spawn down the hall (found by walking the island from
  /spawn, `tools/reach.py`). Secondary edge drops: the round west terrace rim (x -11, z -36..16, gaps every 4) and the
  outer garden rims (all fall onto plain floor - nothing harmful under the footprint).

## Zones (noise-perturbed, blocky borders)
| Zone | Where | Surface |
|---|---|---|
| Moon (gray volcanic) | ellipse centre (-72,-22), rx 60, rz 96, x <= ~-18 | clay block 82 base, polished andesite platforms (+1), cyan clay/coal accents, cracks |
| West fields | x < ~-130 | grass + oak planks (38% wood), raised plank borders |
| North wood | z < ~-104 | oak planks (88%) + clay-block light-gray patches |
| Fields (rest, incl. under the island) | everything else | oak planks 55% / grass, raised plank borders, flush glowstone lamps under the island |

## Features
| Feature | Position | Notes |
|---|---|---|
| Landing pad | centre (44,0), r 14, y69 | chiseled quartz centre, quartz ring at r 7.5 = hole edge above, 8 spokes, 8 sea lanterns |
| Glass lava paths | W: x -18..29 z -2..1; N: x 42..45 z -112..-15; S: x 42..45 z 15..98; E: x 59..132 z -2..1 | 4 wide, lava y68 under glass y69, nether brick curbs/ends/bottom, arches every 22 (y70..75) with fence+glowstone posts |
| Rock landmark | centre (-70,-12), 36x28 base, peak y99 | jagged spires, E-W tunnel z -14..-10 y70..75 (5 wide, arched), ceiling glowstone |
| Crater | (-104,44) r 10 | stepped rings down to y66, raised dark rim |
| Lava cracks | moon only, 896 open lava cells (seed 1906) | branching walks that stop when they meet another crack; 7 pools; >= 6 from wood/grass, >= 6 from island footprint |
| Mounds | 22 in the moon | r 2-4, 2-4 high, andesite/polished andesite/cyan clay |
| Trap (= pavilion) | v3 hut x 38..44 z -168..-160, apron x 32..56 z -174..-154 | R24 hut, pit hole in its floor centre (41,-164), middle feet y62, chamber feet y56, exit stairs south; see change-log 2026-11-06 ~15:45. v1 pavilion and v2 walled trap removed |
| Pavilion | removed (merged into the trap hut) | `pavilion.enabled=false` |
| Lighting | island shadow | 320 flush glowstone (lattice spacing 12 + greedy fill to light >= 8 at feet) |

## Re-run recipes
- Rock taller: `--set rock.height=36` (or edit blueprint) -> `build.py --only rock` -> paste `wz_rock` (box from manifest).
  If the footprint grows, also rebuild `moon` (cracks keep 3 off the rock).
- Move the pit/trap: edit `trap.x/z` -> `build.py --only trap --box <old box>` -> paste `wz_trap` and `wz_box`.
- More/less lava: `moon.lava.seeds` (x, z, steps), `branch_p`, `pools` -> `--only moon` -> paste `wz_moon`.
- Everything: `build.py` -> paste `warzone_full` at -176 50 -176 with air (8.8 M blocks, ~25 s on FAWE).
