---
name: astro-warzone-builder
description: Workflow, file layout, palette and blueprint for rebuilding the AstroPvP main spawn warzone (grass/oak-plank fields, gray volcanic moon area with branching lava cracks, jagged rock landmark, glass-covered lava paths, drop-down landing, pink gank trap with pit, pink pavilion) under the floating spawn island, on the isolated 1.8.8 test server only. Use when building, changing or testing any part of that warzone (e.g. "make the rock taller", "move the pit", "more lava cracks").
---

# Astro warzone builder

Everything here is TEST-ONLY until the user explicitly approves a live install. Live = `C:\Users\levir\AstroPvP-Windows-Test`.

## Original references (read FIRST, every reconstruction task)
The user's original AstroPvP screenshots are saved permanently (never ask the user to re-upload them):
`C:\Users\levir\wt-warzone\AstroWarzone\references\astro-original\`
- `REFERENCE_CATALOG.md` - every image R01..R23: file, source session, size, location, facing, HUD coordinates,
  landmarks, candidate blocks, confirmed vs uncertain, groups of frames showing the same structure.
- `ANALYSIS_NOTES.md` - the user's own area descriptions, confirmed facts, things no frame shows, corrections on
  record, and the lessons from prototype v1 (what it invented). Read section 5 before changing any region.
- Category folders `01-main-floating-spawn` .. `11-unknown-locations` hold the image files (byte copies, checked by
  `SHA256SUMS.txt`). Open the images themselves with Read; the catalog is a guide, the pixels are the source of truth.
- Rules: resource-pack colours are not block ids; never invent a measurement or coordinate; empty folders
  (`02-spawn-drop-down`, `06-lava-under-glass`, `10-entrances-and-stairs`) mean NO original image exists yet.
- Keep originals separate: put test-build screenshots in `AstroWarzone/out/screens/`, never in `references/`.
- New user screenshots: copy them in with the next free R-number (cp -n, never overwrite), add a catalog row, update
  `SHA256SUMS.txt`. Images in `%TEMP%\claude\...\images` get cleaned up - copy them the same session.

## Original video references (watch-video skill)
Original AstroPvP YouTube videos and the user's local recordings are references too, through the `watch-video` skill.
- Check `C:\Users\levir\astro-video-frames\INDEX.md` FIRST: frames already extracted in earlier sessions are reused, not
  re-extracted. Each run folder has `index.json` + `README.md` with every frame's real video timestamp.
- New extraction (frames are saved permanently with timestamps):
  `bash ~/.claude/skills/watch-video/scripts/astro_frames.sh "<URL or local file>" --note "<area>"`
  YouTube: add `--section 2:10-3:05` for the part that shows the area; flyovers/cuts: `--scene-threshold 0.3`;
  small detail/text: `--width 1180 --quality 2`; cap frames with `--max-frames 20`.
- Read the frames with Read. Cite them as `VID:<slug>@HH:MM:SS` next to R-numbers; a video frame confirms a feature
  just like a screenshot, but motion blur / compression is NOT block-id evidence (same rule as resource-pack colours).
- Video frames stay in `astro-video-frames`, never inside `references/astro-original/` (that folder is user screenshots
  only) and never in any server folder. If the user wants a frame promoted to an R-number, ask first.

## Files
- Code (git, branch `astro-warzone`): `C:\Users\levir\wt-warzone\AstroWarzone\`
  - `blueprint.json` - every tunable number (zone borders, rock size, pit depth, trap/pavilion position, seeds).
  - `build.py` - runs the region scripts in order into one grid, writes `out/warzone_full.schematic`, one crop schematic per
    region (`out/wz_<region>.schematic`, full box of that region incl. air), `out/render_top.png`, `out/manifest.json`.
  - `regions/*.py` - one script per area: `terrain`, `moon`, `rock`, `lava_paths`, `landing`, `trap`, `pavilion`, `lighting`.
    Each has `build(G, P, ctx)` and reads its own section of blueprint.json.
  - `tools/grid.py` (grid + .schematic writer), `tools/anvil.py` (Anvil reader), `tools/survey.py`, `tools/drops.py`,
    `tools/reach.py` (island drop-down finder), `tools/wzc.sh` (send console commands to the test server), `tools/shots.sh` (real-client screenshot tour). The top-down render is written by build.py.
  - `WarzoneTool/` - test-only console plugin (`wz paste|count|block|walk|path|stuck|light|report`), `sh build.sh`.
- Reference docs (this folder, `reference/`): `screenshot-analysis.md`, `block-palette.md`, `layout-blueprint.md`,
  `style-rules.md`, `change-log.md`. Read the blueprint + style rules before any change; append to the change log after.
- Test server: `C:\Users\levir\AstroPvP-WarzoneTest` (TacoSpigot, 127.0.0.1:25699, offline, plugins: WorldEdit 6.1.7.3,
  FAWE, WarzoneTool only). Pristine live-world input: `_source-live-world-2026-11-06`.

## Workflow
1. Edit `blueprint.json` (preferred) or the owning region script.
2. `cd C:\Users\levir\wt-warzone\AstroWarzone && py -3 -I build.py` (or `--only trap` for one region; the composite is
   always rebuilt so overlaps stay right, but only the named crops are written).
3. Copy the schematic(s) to `AstroPvP-WarzoneTest\plugins\FastAsyncWorldEdit\schematics\` and paste on the running
   test server: `sh tools/wzc.sh -w 20 "wz paste wz_<region> <minX> <minY> <minZ> air"` (coordinates are in
   `out/manifest.json`). Moving something = rebuild, then paste the crop of BOTH the old and the new box
   (`build.py --box x1 z1 x2 z2` writes a crop of any box).
4. Checks (console): `wz walk 44 70 0 -176 -176 175 175` then `wz stuck -176 -176 175 175 60 110`,
   `wz light ...`, `wz block x y z`, `wz count ...`. Door/plate test needs a player on the plate (camera client).
5. Real screenshots: camera tooling in `C:\Users\levir\wt-warzone\camera\` (outside git, moved there 2026-11-06 from a
   wiped Temp scratchpad; vanilla 1.8.9 client WarzoneCam). Start off-screen:
   `powershell -File C:\Users\levir\wt-warzone\camera\offscreen.ps1 -LaunchPy C:\Users\levir\wt-warzone\camera\launch_wz.py`
   (pid in `camera\client_wz.pid`); console `tp WarzoneCam x y z yaw pitch` (yaw S 0, W 90, N 180, E -90), then
   `restore.ps1 -ProcId <pid>` and `shot.ps1 -ProcId <pid> -Out <png>` (or `tools/shots.sh <pid> <outdir>`).
6. Log the change in `reference/change-log.md`.

## Rules that bite
- Live gamerule doFireTick=true: open lava needs >= 5 blocks to any wood/wool/leaves/tall grass; lava under glass must be
  sealed on all sides (nether brick) - see style-rules.
- Never write y >= 130 (island bottom is y138). Surface is y69 (players stand at y70, like the original Astro frames).
- Box = WorldGuard `spawnwarzone` / Factions WarZone chunks: x,z -176..175. Nothing outside it.
- 1.8.8 ids only (palette doc). Door lower half data = facing (0 E,1 S,2 W,3 N), upper half 8 (+1 = hinge right).
- WorldEdit 6 cannot paste from console; WarzoneTool does (FAWE EditSession, relights).
- Production install is a separate, user-approved step: back up live, stop nothing for tests, use the arkreboot rules in memory.
