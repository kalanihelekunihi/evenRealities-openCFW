# OpenCFW change scan — 2026-10-08 19:29 UTC

Compared with the [18:41 scan](../rescan-2026-10-08T184112Z/REPORT.md), component C/header/assembly inventory is **600 → 612 files: 12 added, 0 modified, 0 removed**. 532 are indexed, 80 untracked, and 0 ignored. Counts include historical/scaffold variants and do not measure firmware completeness.

New sources:

- `g2/components/audio/platform_callbacks_offline/callbacks.c`
- `g2/components/audio/platform_callbacks_offline/callbacks.h`
- `g2/components/audio/platform_callbacks_offline/classify.c`
- `g2/components/audio/platform_callbacks_offline/itcm.c`
- `g2/components/audio/platform_callbacks_offline/newer.c`
- `g2/components/audio/platform_callbacks_offline/planner.c`
- `g2/components/audio/platform_callbacks_offline/prepare.c`
- `g2/components/audio/platform_callbacks_offline/public_leaf.c`
- `g2/components/audio/platform_callbacks_offline/read_init.c`
- `g2/components/audio/platform_callbacks_offline/route.c`
- `g2/components/audio/platform_callbacks_offline/select.c`
- `g2/components/audio/platform_callbacks_offline/timer.c`

## New substantive evidence

The new, currently unsealed `audio-platform-callbacks-closure-2026-10-08` batch contains reconstructed registration, power-state classification/planning/routing, calibration reads, ITCM helpers, and timer initialization/control. It has no final report or delivery manifest yet. Existing author-recorded comparisons are listed in the snapshot; this scan did not rerun them or independently validate behavior.

A significant correction to the previous report is supported by `itcm-results.json`: OTA initializer record **0x75D3E4**, compressed input **0x79430E / 22 bytes**, expands into **24 executable bytes at 0x40..0x58**, SHA-256 `0676154418085b0630f2a20cc50fbbe3967dd2d9b7794fe1aad3f6af14f2fb83`. Addresses 0x40 and 0x48 are initialized ITCM helpers present in the OTA, rather than unavailable resident-ROM dependencies. The earlier unmapped-fetch observations reflected omitted runtime initialization. Actual device calibration data and physical timing remain unverified.

Official Ambiq Apollo510 HAL source is now available at `third-party/upstream/ambiqhal-apollo510` and the additional reference checkout `third-party/reference/ambiqhal-audio-5.1.0`, pinned to `5efc0228528a8adce5eae0d226fac85d2551eb3b`. The existing registered gitlink is reused; the additional checkout is untracked. Public leaf evidence records 441 compatible inputs under compact enum ABI; forced-wide enums preserve numeric results but change output footprint. This supports selected source reuse, not whole-module or byte-identical firmware equivalence.

The unfinished integrated newer-control batch must not be reported complete merely because an older `newer-results.json` says PASS: the latest working-session verification found a flag mismatch at RAM **0x20074F6A** after integrating the preparation helper. That result remains a known unresolved verification issue, and the current-build hash comparison is recorded below. No source was changed to resolve it during this scan.

## Preservation and limits

All **1157 sealed entries**, **110 audit inputs**, and **4 checkpoints** match their recorded hashes. HEAD remains `36ff5930a4e832156f9ee3111e83480756ebef37`. Only this new report and snapshot were written; no staging, builds, generator execution, firmware writes, or campaign changes.

Gitignore hides none of the 612 component source files. A committed-only view omits 80 untracked files. These are real source additions, but still bounded offline reconstructions rather than a complete source-built or byte-identical OTA. Existing synthetic MMIO, child-entry stopping boundaries, scheduler/exception-return limits, and missing device calibration data continue to constrain conclusions.

[Exact delta, receipt/build identities, Git status and hash checks](snapshot.json).
