# Change log (newest first)

## 2026-11-06 ~15:45 - area 1 v3: gank hut (R24) with the pit in its floor; v2 walled trap + v1 pavilion removed
- User rejected v2 (15:20): no building around the pit; the trap is the R24 hut, hole in the middle of its floor;
  pavilion and trap are one structure. Backup: commit b66a8b7, world `backups\2026-11-06_1526_area1-v3\region`.
- regions/trap.py v3 + blueprint `trap`: hut x38..44 z-168..-160, dark oak planks 5:5 walls y70..73, cap y74, 3 roof
  steps y75..77, iron 3x3 y75 (hidden), beacon 41,76,-164, purple glass 95:10 at 41,77/78,-164 (beam). W and E faces:
  purple glass z-163..-161 y70..72, open doorway z-167..-166 y70..72. Floor dark oak; hole x40..42 z-165..-163 (centre
  under the beacon), shaft y66..68 red/green checker glass. Middle room x37..45 z-166..-160 feet y62; chamber
  x34..46 z-167..-159 feet y56 (pink/red over quartz, ceiling y59, y58 along N+W). Stairs: x45..40 y61..56 z-161
  (114:0); exit x44..45 z-160..-153 y62..69 (114:2) to the grass south of the hut. Grass apron x32..56 z-174..-154.
- pavilion region disabled (`pavilion.enabled=false`); old box re-pasted as terrain: `wz paste wz_box 106 50 -146 air`
  (11999 changed, count y70..120 = 0). Trap: `wz paste wz_trap 31 50 -175 air` (46008 changed).
- Checks: static OK; walk from pad 123968, all 3 anchors reachable; walks from 41,56,-167 and 41,62,-162 reach the pad;
  stuck only roof tops (63, y75..79); light 0 flagged (after relight). Shots + pairs `out/screens/area1-v3/pair_R*.png`.

## 2026-11-06 ~15:30 - area 1: trap v2 at original coordinates (option A 1:1), test server only
- Backup: commit 67c4a5f, world `AstroPvP-WarzoneTest\backups\2026-11-06_1449_area1-trap\region`.
- regions/trap.py rewritten + blueprint `trap` section: shell x34..49 z-169..-159 y53..74. Top room x39..47 z-168..-161
  (feet y70, dark oak walls y70..74, purple glass 95:10 west panel x38 z-163..-161 + south x39..41 z-160, lime clay 159:5
  wall x38 z-168..-165 y70..72, iron door 38,70,-166 + plates 37/39,70,-166 + slab 44:8 at 38,72,-166). Hole x39..41
  z-163..-161, shaft walls y66..68 red/green checker glass, dark oak rim y69. Middle room x37..47 z-165..-161 (feet y62,
  red/green 95:14/95:13 over clay). Lowest chamber x36..45 z-167..-163 (feet y56, pink/red glass over quartz, ceiling y59,
  y58 along N+W). Nether brick stairs: x45..40 y61..56 z-163 (data 0) and x46..47 z-161..-168 y62..69 (data 3).
  Anchors R17 43,70,-161 / R18 41,62,-162 / R07 41,56,-167 are walkable. Everything except the anchors = ESTIMATED.
- Old v1 trap removed: `build.py --box 125 -159 142 -142` -> `wz paste wz_box 125 50 -159 air` (23004 changed); count
  y70..120 there = 0, y50..68 = stone/dirt only. New trap: `wz paste wz_trap 33 50 -170 air`.
- Checks: static OK; walk from pad 123868 spots, anchors reachable; walk from 41,56,-167 = same 123868 + pad reachable;
  trap-box stuck = only wall tops (y75, y73); light 0 flagged; real plate test both sides (door 71:0 -> 71:4 -> 71:0).
- 3 shot rounds with the real 1.8.9 client; pairs in `AstroWarzone/out/screens/area1/pair_R*.png`.
- Camera tooling moved to `C:\Users\levir\wt-warzone\camera\` (+ click.ps1 for the Respawn button, tools\sidebyside.ps1).

## 2026-11-06 ~01:00 - prototype v1 on AstroPvP-WarzoneTest (NOT live)
- New test server AstroPvP-WarzoneTest (Taco, 127.0.0.1:25699, WE + FAWE + WarzoneTool only), world = live regions
  r.-1.-1 r.-1.0 r.0.-1 r.0.0 + level.dat copied 00:06 (pristine copy `_source-live-world-2026-11-06`).
- Toolchain proof: `tools/proof.py` -> wz_proof pasted at 300,70,300; ids/metadata identical; real client screenshot.
- Full build (seed 1906) pasted at -176 50 -176 with air: 8,797,184 blocks changed. Rock crop re-pasted after the tunnel
  light fix (`wz paste wz_rock -92 50 -28 air`).
- Static checks (build.py): all lava sealed, no flammable block within 5 of open lava, no open lava under the island,
  nothing above y120.
- Server checks: walk from pad 44,70,0 -> 123,715 standing spots; from pit floor, crater, rock tunnel, a lava crack,
  the west rim landing -> same set, pad reachable (no stuck ground spots; unreachable = roofs/spires/arch tops only).
  Light (day): 0 dark spots on the ground after the tunnel fix (arch tops only). Real plate test: player on 126,70,-150
  -> plate 70:1, west door 71:0 -> 71:4 (open). Real drop from 40.5,150,2.5 through the hole -> landed on the pad
  at y70 (test server has no fall-damage cancel; live does).
- Fixes during the build: neutral grays (stained clay light gray/gray are brownish in 1.8 -> clay block 82, polished
  andesite, cyan clay), lava keep-off measured in Chebyshev distance, tree-like cracks (walkers stop at other cracks),
  lamp placer within Manhattan 4, tunnel ceiling lights one block higher.

## 2026-11-06 ~01:00 - pit exit fix (audit by the minecraft-map-builder brief)
- Metadata audit (read-only, `wz block`): doors 71:0/71:1 + 71:8, 4 plates, lintel 44:8, pit stairs 114:3, pavilion roof
  rings, arch corners 114:4-7 all as intended. Finding: the pit exit needed a 1-block jump (stairs ended at y68).
- trap.py: steps = pit_depth (7 stairs y63..69, last at z -153 flush with the room floor), landing block removed.
  Re-pasted `wz paste wz_trap 125 50 -159 air`; 136/137,69,-153 = 114:3; walk from pit floor reaches the pad.
- Kept on purpose: the half-block slit between the west door and the top-slab lintel (possible pearl entry).

## 2026-11-06 18:42 - REMOVED the four straight lava trenches (user rejected them)
- User: remove all four straight lava trenches from the centre (dark portal-frame arches, curbs, leftover lava), blend
  the ground; keep island, drop shaft and current landing pad.
- blueprint.json `lava_paths.paths` = [] (old defs kept in `removed_paths`). Rebuilt crops of the four strips
  (west -21 -6..32 5, north 38 -115..49 -12, south 38 12..49 101, east 56 -6..135 5, y50..120, incl. air) as
  out/wz_rmtrench_{west,north,south,east}.schematic and pasted with air.
- Backup: world regions `AstroPvP-WarzoneTest\backups\2026-11-06_1842_remove-lava-trenches\region`, code at d9565dd.
- Check: no LAVA / GLASS / NETHER_BRICK left in x-21..135 z-115..101 y50..75; walk from pad 44,70,0 reaches 124,016
  spots (was 123,715); stuck flags only on the hut roof and rock spires (pre-existing).
- Screens: out/screens/2026-11-06_trenches-removed/.

## 2026-11-06 18:55 - area "wooden battlefield floor": oak -> dark oak
- Evidence: user correction 15:20 ("dark oak, not light oak; v1 oak read as sand"), R09/R06/R13 dark brown plank floor.
- terrain.py: plank floor + raised plank borders/slabs use blueprint `terrain.plank_data` = 5 (dark oak 5:5, slab 126:5).
- Full rebuild pasted `wz paste warzone_full -176 50 -176 air` (composite == world apart from this change).
  Result at y69-70: WOOD:5 71,835, WOOD_STEP:5 124, no WOOD:0 left.
- Backup: `AstroPvP-WarzoneTest\backups\2026-11-06_1854_area-wood-floor\region`, code e175c8d.
- Side-by-sides: out/screens/2026-11-06_area-dark-oak-floor/SIDE_*.jpg (R09, R06, R13).
- Seen in R09/R06 but NOT changed yet: more frequent light-gray blocky patches near the edges; R06 (z -185) shows the
  plank floor continuing north past the -176 box edge.
- Video search 2026-11-06 (frames in astro-video-frames): trailer qkIs1d-Lu5Y, Map #10 recap wZ6U6dPPM34, Mainpvp
  wymNTOeF88M, owner 30 min QzGcQZgTjVI, SOTW FJtr_QrltHQ = other maps/eras (desert, snow, sand/obsidian, arcade
  spawn); none shows this warzone, drop or landing. R06/R09 are themselves YouTube frames (7:31 / 7:51 videos,
  account XaitX, scoreboard "doa 01/22") - finding those videos would give the drop/landing footage.

## 2026-11-06 19:20 - area "gray patches on the plank floor" (R06, R09, R13, R21)
- terrain.py `gray_patches()` (runs AFTER the raised borders, own RNG -> moon/rock/borders byte-identical): light-gray
  clay 82 strokes = rasterised rotated rectangles (stair-stepped diagonal edges), 2-8 long x 1-3 wide, 2-4 per slanted
  cluster (spread 8); clusters north 80 / fields 95 / west 25; 12 thin diagonal strips along the north box edge (R06);
  45 short strokes within 6 of the moon edge (R21). Plank cells only; landing pad + 3 kept clear. Old north 3x3 squares
  off (`gray_patch_share_north` 0). v1 (9,055 cells) merged into blobs vs R13 -> v2 5,482 cells.
- Pasted full composite; walk from pad unchanged (124,016 spots). Backup `backups\2026-11-06_1911_area-gray-patches`.
- Side-by-sides: out/screens/2026-11-06_area-gray-patches/SIDE_*.jpg. Still different: originals are a bit thinner and
  more rectangular; R09 foreground is planks where ours is grass (zone layout, a separate area); R06 is at z -185,
  outside our -176 box.
- Video ZaVCfIdum_c (user link, Ontrack "We are back Astro PvP Montage" 2025-01-02) 2:50-4:10: brown plank floor at
  46,70,-138 @03:15.5 ("Warzone" title), gank hut + purple beam @03:34-03:37, hut interior with pink/red glass pit
  @03:52-03:54. No drop/landing, no gray patches in that part.

## 2026-11-06 19:30 - rocky zone v2 (user: "big section of rocky spot, clay bigger and stones"; lava never open)
- regions/moon.py rewritten (v1 kept as moon_v1.py): zone enlarged (terrain.moon cx -100 cz -6 rx 100 rz 116 x_max -18;
  30,748 columns); Voronoi plates (size 24, 2-block stepped edges) = floor / light clay slab +1 / dark polished-andesite
  plateau +1..+2 (R05/R11); 55% of plate borders = 2-4 wide channels: red 95:14 / orange 95:1 glass FLUSH at y69 over
  lava y68, sealed by cyan clay 159:9, dark rims (R15/R16); crater kept; 45 blocky dark stone heaps (R01/R11).
  3,907 lava cells, 0 open. Own RNG + ctx.rng reset from regions/rng_after_moon_v1.json -> rock byte-identical.
- Backup backups\2026-11-06_1930_area-rocky-moon-v2.

## 2026-11-06 19:38 - no glowstone (user) + gank hut v4 at 129,70,-135 (user)
- lighting.enabled false, rock.tunnel_lights false, trap.lights false -> 0 glowstone (8 sea lanterns in the landing pad stay).
- trap v4: hut moved to centre 129,-135 (user F3), 7x7, one purple-glass doorway + plank sill, iron door + stone plates
  entrance, NO stairs (user), pit-room exit iron door + plates -> ladder shaft to the grass, ladder to the lowest chamber.
  Bot PitBot: plate -> door opened -> walked through -> climbed the ladder -> out at 137.5,70,-132.5.
  TRAP: FAWE dropped the top ladder (136,69,-133) + its wall block on the full paste; fixed with setblock.
- Backup backups\2026-11-06_1938_hut-v4-noglow.

## 2026-11-06 19:55 - user's hand-built pavilion kept + beacon beam fixed
- XaitX rebuilt the hut by hand (~19:45): open 5x5 pavilion x127..131 z-137..-133, purple glass W + S faces, open N/E,
  dark-oak ceiling y73, 3x3 top y74 with BEACON 129,74,-135, purple glass 129,75,-135; removed my iron doors/plates
  (incl. the pit-room exit door 134,62..63,-133). No beam: the 3x3 under the beacon was dark oak.
- Fix (setblock): IRON_BLOCK at 128..130,73,-136..-134 (9); dark oak planks 5:5 at 128..130,72,-136..-134 (9, hides the
  iron from inside). Sky above clear to y255. Beam verified in the real client (purple, into the sky).
- regions/trap_user_pavilion.json (238 blocks = world minus composite) is stamped LAST by trap.py -> rebuilds keep the
  user's pavilion. Backup before the fix: backups\2026-11-06_1952_before-beacon-fix.
- Screens: out/screens/2026-11-06_pavilion-beacon/ (+ SIDE_ vs VID:ZaVCfIdum_c@00:03:35 and R10). Note: at 03:35 the
  player is at 67,71,-109 facing N with the pavilion ahead-left -> the original stood near x 40-60, z ~-150..-165.

## 2026-11-06 20:28 - DEPLOYED TO LIVE (user authorized)
- Source = AstroPvP-WarzoneTest saved world (incl. the user's hand-built pavilion + beacon fix), box x,z -176..175 y50..120
  read with tools/anvil.py -> out/wz_deploy_from_test.schematic (352x71x352). Live tool SpawnIslandTool:
  `sisland save` (backup) -> `sisland clear` -> `sisland paste world wz_deploy_2026-11-06 -176 50 -176` (2,507,134 changed).
- Verified from live region files after save-all: box == test world (0 mismatches / 8,797,184); above y120 only daylight
  sensors changed (time of day); drop column 44,0 open from y155 to the pad at y69.
- Backup + RESTORE.txt: AstroPvP-Windows-Test\_backup-2026-11-06-warzone-deploy.
