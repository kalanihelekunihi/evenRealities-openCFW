# OpenCFW change scan — 2026-10-08 20:37 UTC

Compared with the [19:29 scan](../rescan-2026-10-08T192959Z/REPORT.md), component C/header/assembly files increased **612 → 618**: **6 added, 1 modified, 0 removed**. 532 are indexed and 86 untracked. Git check-ignore reports 0 matching rules for these files. This inventory includes historical/scaffold variants and is not a completeness percentage.

## What changed

The previously unfinished platform-callback batch is now sealed. Its corrected integrated newer-control comparison resolves the earlier RAM flag mismatch at 0x20074F6A; current receipts and sealed hashes replace the obsolete intermediate result. Initialized ITCM helpers remain supported by authenticated OTA decoder evidence.

The transition/timer batch adds seven reconstructed functions with 1,364 author-recorded comparisons. The subsequent producer batch covers all 27 PCM2.2 transition-table entries and exposes 32 new functions, linking seven prior functions. Its exact-build receipt reports 12,019 comparisons, including 1,364 linked regressions. These recover power/rail/cache changes, delayed completions and cancellation behavior; selected stock behavior differs from the pinned public Ambiq SDK.

A new PCM2.1 control reconstruction exists at `g2/components/audio/pcm21_control_offline`. Its current result records PASS for 1,297 comparisons against original instructions, with real stock prepare/state-change/planner/apply children executing. This batch is **unsealed and has no final report**, so treat it as work in progress. It identifies inactive-buck early return, sleep-to-active planning bypass, and deferred CPU-state update. Synthetic calibration/MMIO and omitted stack-only profiling records limit parity claims.

## New source paths

- `g2/components/audio/pcm21_control_offline/control.c`
- `g2/components/audio/pcm21_control_offline/control.h`
- `g2/components/audio/transition_producers_offline/producers.c`
- `g2/components/audio/transition_producers_offline/producers.h`
- `g2/components/audio/transition_timer_offline/transition.c`
- `g2/components/audio/transition_timer_offline/transition.h`

## Preservation and limits

All **1233 sealed entries**, **110 audit inputs**, and **4 checkpoints** match recorded hashes. HEAD is `36ff5930a4e832156f9ee3111e83480756ebef37`. This scan only writes its own report and snapshot; it does not stage changes or rerun builds/tests. No complete source-built or byte-identical firmware is established. Device calibration, physical timing and coherent live scheduler/IRQ state remain external validation gaps.

[Exact inventory delta, receipt identities, Git status and preservation evidence](snapshot.json).
