# AstroPvP floating spawn + spawn Warzone (Minecraft 1.8.8 map export)

A full copy of the AstroPvP floating spawn island and the warzone built underneath it. Exported 2026-11-07.

## Download

- **Whole map in one file:** [`AstroPvP-Spawn-Warzone.zip`](https://github.com/ronylevixx123god-create/warzone-maps/raw/main/spawn-warzone/AstroPvP-Spawn-Warzone.zip)
  (holds the same `world/`, `generator/` and `docs/` folders as this one).
- Or browse the folders here: `world/` is the playable map, `generator/` holds the build scripts and schematics.

## Original world location

`C:\Users\levir\AstroPvP-WarzoneTest\world` on the AstroPvP WarzoneTest server (TacoSpigot 1.8.8,
`server.properties` `level-name=world`, no Multiverse). The island and the warzone are both in this world.
The server was stopped during the copy (last save 2026-11-06 22:48), so the files are consistent. The original
was not changed: the region files and level.dat in `world/` are byte-identical to it (SHA-256 checked).

## Minecraft version

**1.8.8** (Anvil `.mca` region files, numeric block IDs). Open it with a 1.8.x client or server, MCEdit or Amulet.
To play it, copy `world/` into a 1.8.8 server's folder or into `.minecraft/saves/`. Newer versions will
upgrade (and change) the blocks.

## What's included

| Path | Contents |
|---|---|
| `world/level.dat`, `world/uid.dat` | world settings, spawn point |
| `world/region/r.-1.-1 r.-1.0 r.0.-1 r.0.0 .mca` | all the terrain: x/z -512..511, island + warzone |
| `world/data/` | vanilla structure data |
| `generator/build.py`, `blueprint.json`, `regions/*.py` | Python generator that builds the warzone, one script per area |
| `generator/tools/` | region-file reader (`anvil.py`), island survey, drop-down finder |
| `generator/out/*.schematic` | MCEdit schematics: `wz_deploy_from_test.schematic` = the exact 352x71x352 box that went live; `warzone_full` + per-area crops |
| `generator/out/manifest.json`, `render_top.png` | paste commands, top-down render |
| `generator/WarzoneTool/` | source of the test-only console plugin used for pasting/checking |
| `docs/` | block palette, layout blueprint, style rules, screenshot analysis, full change log |

Not included: player data, inventories, stats, plugins, server configs, licence files, logs, backups,
and the vanilla `world_nether` / `world_the_end` (unrelated, untouched).

## Spawn coordinates

- World spawn (level.dat): **0, 153, 0**; players stand at 0.5 153 0.5 on a beacon pad at 0, 152, 0.
- Floating island footprint: about x -14..162, z -80..58, around y 149-160.
- Drop-down into the warzone: round hole in the island floor at x 37..51, z -7..7, y 149 (centre 44, 0),
  open all the way down to the landing pad at y 69.

## Warzone coordinates

Build box **x -176..175, z -176..175, y 50..120** (352 x 71 x 352). Ground surface y 69, players walk at y 70.

| Area | Location |
|---|---|
| Landing pad | centre 44, 69, 0, radius 14 (under the drop hole) |
| Rocky gray "moon" zone | most of the west half: ellipse centre -100, -6, radius 100 x 116, x <= -18 |
| Jagged rock landmark | centre -70, -12, about 36 x 28 wide, 30 high, 5 wide x 6 high tunnel |
| Gank pavilion + pit | x 127..131, z -137..-133; beacon at 129, 74, -135; 3x3 pit in the floor down to about y 56 |
| Plank fields | dark-oak plank floor with light-gray clay patches over the rest of the box |

## Finished structures

These were built and checked in the client. The same box went to the live server on 2026-11-06 20:28.

- Dark-oak plank battlefield floor, raised plank borders, light-gray clay patches
- Rocky moon zone v2: stone plates, dark andesite plateaus, crater, stone heaps, lava channels covered by flush
  red/orange stained glass (no open lava)
- Jagged rock landmark with its tunnel
- Drop-down hole from the island to the landing pad
- Gank pavilion (hand-built by the owner) with a working purple beacon beam and the pit
- Floating spawn island (copied from the live map, unchanged)

## Unfinished structures

- **Landing pad:** still the estimated v1 design, because no footage of the original landing exists.
- **Lava paths:** the four straight glass-over-lava paths were rejected and removed, and nothing has replaced them.
- **Plank floor beyond z -176:** the original continues there; nothing is built outside the box.

## Known issues

- The south edge of the rocky zone is estimated.
- Gray patches are a bit thicker and less rectangular than in the original screenshots.
- One foreground area is grass where the original reference shows planks (the zone layout was not redone).
- The original pavilion probably stood near x 40-60, z -150..-165; the current one is where the owner placed it.
- Glowstone lighting was removed on request (only 8 sea lanterns in the landing pad), so the map is dark at night.
- In 1.8, light-gray/gray stained clay looks brown, so the build uses clay block 82, polished andesite and cyan clay 159:9 instead.
- The test world was saved again after the live deploy (22:38-22:48 on 2026-11-06). This export is its current
  state and may include small test edits made after the deploy.
- `generator/README.md` and `docs/` refer to local Windows paths of the original setup.
