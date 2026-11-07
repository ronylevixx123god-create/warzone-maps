# 1.8.8 block palette (legacy id:data) used by the warzone

Only ids that exist in Minecraft 1.8.8. `F` = flammable (keep >= 5 blocks from open lava).

| Use | Block | id:data |
|---|---|---|
| Grass field | grass | 2:0 |
| Under grass/wood | dirt | 3:0 |
| Fill below y66 | stone | 1:0 |
| PvP floor | oak planks (F) | 5:0 |
| Raised border step | oak slab bottom (F) | 126:0 (top half 126:8) |
| Raised border edge | oak stairs (F) | 53:0-3 (0 E,1 W,2 S,3 N = high side), +4 upside-down |
| Floor patches (north) | light gray stained clay | 159:8 |
| Moon base | light gray stained clay | 159:8 |
| Moon platforms / crack rims | gray stained clay | 159:7 |
| Rock dark accents | black stained clay | 159:15 |
| Mounds / rock texture | andesite / polished andesite / stone | 1:5 / 1:6 / 1:0 |
| Crater rings | cobblestone? no -> gray clay + light gray clay | 159:7 / 159:8 |
| Open lava (cracks, pools) | still lava | 11:0 |
| Lava path cover | glass | 20:0 |
| Lava path curbs / channel | nether brick | 112:0 |
| Arches | nether brick, nether brick stairs, nether brick fence | 112, 114:0-7, 113 |
| Landing pad | quartz block / chiseled quartz / light gray clay / gray clay | 155:0 / 155:1 / 159:8 / 159:7 |
| Lighting (under island) | glowstone / sea lantern | 89:0 / 169:0 |
| Trap outer walls | dark oak planks (F), spruce log vertical (F) | 5:5, 17:1 |
| Trap windows | magenta stained glass | 95:2 |
| Trap interior | pink / red stained glass | 95:6 / 95:14 |
| Trap pit walls/floor backing | pink / red stained clay | 159:6 / 159:14 |
| Trap doors | iron door lower / upper | 71:0-3 (0 E,1 S,2 W,3 N facing) / 71:8 (+1 hinge right) |
| Trap plates | stone pressure plate | 70:0 |
| Slab over doorway | stone slab top half | 44:8 (bottom 44:0) |
| Trap pit stairs | nether brick stairs | 114:0-3 (0 E,1 W,2 S,3 N) |
| Trap roof | dark oak slab (F) | 126:5 / top 126:13 |
| Pavilion pillars | pink stained clay | 159:6 |
| Pavilion roof | dark oak stairs (F), dark oak planks | 164:0-3 (+4 upside-down), 5:5 |
| Pavilion beam | beacon, iron blocks, pink stained glass | 138, 42, 95:6 |

Checked on the test server (2026-11-06, proof paste at 300,70,300): door 71:1 + 71:8, slab 44:0, stairs 53:2
(high side south), stained glass 95:6/95:14, planks 5:0, grass 2, stone 1, glass 20 all import with the same id:data.
