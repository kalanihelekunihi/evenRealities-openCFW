# OpenCFW rescan — 2026-10-08 11:50 UTC

Compared with the 06:48 UTC snapshot, the component tree has **36 additional C/header files**, no changed prior source hashes and no removed prior source files. The comparison includes the previous 475 non-touch files and 13 touch files: 488 previously, 524 now. All 36 additions are touch reconstruction work. There are 520 files in the Git index and four untracked files; none of the 524 component source files is ignored. Index membership does not mean committed or staged content equals disk content.

New source covers calibration/configuration bootstrap, gesture state and speed, slider filtering/centroid, proximity processing, maximum raw counts, scan watchdog/frame execution, mode transitions, capture/init, pin control, per-sensor frame generation and all-slot orchestration. These are independent offline reconstructions, not a complete replacement firmware build.

The latest delivered mode/pin/frame batch records 7,539 comparison cases across component and composition tests (some earlier cases exercise cut dependencies). The new all-slot result records PASS for 144 cases, with actual original all-slot/per-sensor/CDAC/mask/divider instructions and no function-entry stubs. It establishes five active and four low-power slots, mask/shield overlays, and discarded per-sensor generation errors. Its synthetic descriptors/configurations do not establish physical scanning behavior. The all-slot directory is still an unsealed work product.

Pinned public Infineon PDL reproduces Capture and ConfigureScan exactly, totaling 208 compiled bytes. Configure remains behavioral attribution: its 424-byte implementation differs in 24 bytes, with 180 recorded comparison cases. This does not establish whole-image byte equality.

Integrity verification in this scan: 512 sealed manifest entries match, all 110 audit inputs match, and all four preserved bootloader candidate checkpoints match. Test suites were not rerun during this inventory scan; the test claims above come from existing delivered results and reports.

Git HEAD is now 36ff5930a4e832156f9ee3111e83480756ebef37 (Expand G2 bootloader reconstruction and independent review evidence), whereas the previous snapshot recorded 9d6b94bdd. This scan made no commits or index changes.

## Visibility

`git check-ignore -v --no-index` produces no rule for the new slots.c or generator.c. The scratch probe g2/build/probe.elf is excluded by `.gitignore:15:build/`. No nested .gitignore exists under g2/components, no .git/info/exclude file exists, and core.excludesFile is unset. One worktree is registered, this checkout. Thus source visibility is not being suppressed by .gitignore; build outputs remain intentionally excluded.

## Remaining boundary

Generated base/mode-frame functions at 0x52bc/0x5378 and auto-dither at 0x68ec remain open in the latest delivered index. All-slot generation has advanced beyond that index but is not yet sealed. Exact producer-generated cycfg configuration, physical analog behavior/factory trims/timing, and whole-image source completeness remain unproven. The bounded next step is base/mode-frame and auto-dither composition, preserving partial writes and ignored-error semantics.

Navigation: ../touch-mode-closure-2026-10-08/INDEX.md, ../touch-msclp-attribution-2026-10-08/REPORT.md, ../touch-frame-generation-closure-2026-10-08/REPORT.md, ../touch-all-slot-closure-2026-10-08/results.json. Full file/hash delta is in snapshot.json.
