# AstroWarzone - spawn warzone rebuild (TEST ONLY)

Generator + test tool for the AstroPvP main spawn warzone under the floating spawn island. Prototype v1 2026-11-06,
built and checked only on `C:\Users\levir\AstroPvP-WarzoneTest` (127.0.0.1:25699). Not installed on live.

Docs (workflow, palette, blueprint, screenshot analysis, style rules, change log):
`C:\Users\levir\.claude\skills\astro-warzone-builder\` (skill `astro-warzone-builder`), agent
`C:\Users\levir\.claude\agents\minecraft-map-builder.md`.

    py -3 -I tools/survey.py <world copy> out/survey          # once: island footprint (needed by build.py)
    py -3 -I tools/drops.py  <world copy> out/survey && py -3 -I tools/reach.py out/survey   # drop-down finder
    py -3 -I build.py [--only trap] [--box x1 z1 x2 z2] [--set rock.height=36]
    sh WarzoneTool/build.sh                                   # test-only console plugin

Outputs: out/warzone_full.schematic (+ wz_<region> crops), out/manifest.json (paste commands), out/render_top.png.
Real client screenshots: out/screens/ (not in git).
