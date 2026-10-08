# OpenCFW change scan — 2026-10-08 21:28 UTC

Compared with the [previous scan](../rescan-2026-10-08T203733Z/REPORT.md), component C/header/assembly files increased **618 → 630**: **12 added, 0 modified, 0 removed**. 532 are indexed and 98 untracked. Ignore matches across inspected source: 0. Counts include historical variants and scaffolding; they are not completeness percentages.

## Concrete progress

- PCM2.1 control is now sealed: 1,336 comparisons, replacing the prior unsealed 1,297-case intermediate result.
- Four PCM2.1 children are reconstructed: preparation, state change, planner and apply. Exact-build receipt records 4,482 comparisons including control regressions.
- Nine PCM2.1 completion/lifecycle functions add TON, boost removal, timer ISR and calibration initialization. Exact-build receipt records 7,520 comparisons including earlier regressions.
- PCM2.1 default reset adds 200 direct cases; its exact build records 7,720 comparisons including regressions.
- Eight earlier PCM GPU/temperature/sleep bodies have 5,622 comparisons, including repeated on/on/off and registered callback cases.
- Twelve earlier PCM pending/TON/LP-switch/lifecycle bodies have 6,888 comparisons: 1,266 new fixtures plus 5,622 regressions.

These counts overlap through regression suites and must not be summed as distinct cases. Existing receipts and sealed files were hash-checked; tests were not rerun by this scan.

## Newly established behavior

The stock PCM2.1 planner ignores memory/SSRAM request masks and differs from public SDK unknown-temperature handling. Earlier temperature requests coalesce to the latest cached range. Draining clears pending even when hardware eligibility prevents a trim write: software completion does not prove compensation occurred. Earlier TON selects CPU LP/HP columns; they are not sleep modes. LP disable is gated by a software flag. Repeated GPU-on is not necessarily reversed by one GPU-off under synthetic fixtures. These facts inform power/display/audio patch design but do not establish a naturally occurring hardware defect.

## Preservation and remaining work

All **1328 sealed entries**, **110 audit inputs**, and **4 checkpoint images** match recorded hashes. HEAD: `36ff5930a4e832156f9ee3111e83480756ebef37`. Root index SHA: `9c8d67edda1b93e02db63ec9a4c1ac6c6ae33a3b2898afa4eaeb41d3f8ae2dad`. Only this new scan directory was written; staging and campaign work were preserved.

Initialization and original-trim capture remain actionable source leads. Physical calibration, real rail settling, full M55 exception behavior and coherent live scheduler/IRQ state remain unverified. The reconstructed offline helpers retain explicit original-code dependencies. No complete source-built or byte-identical OTA is established.

New source files:

- `g2/components/audio/early_pcm_gpu_offline/gpu.c`
- `g2/components/audio/early_pcm_gpu_offline/gpu.h`
- `g2/components/audio/early_pcm_pending_offline/pending.c`
- `g2/components/audio/early_pcm_pending_offline/pending.h`
- `g2/components/audio/pcm21_children_offline/apply.c`
- `g2/components/audio/pcm21_children_offline/children.c`
- `g2/components/audio/pcm21_children_offline/children.h`
- `g2/components/audio/pcm21_completion_offline/completion.c`
- `g2/components/audio/pcm21_completion_offline/completion.h`
- `g2/components/audio/pcm21_completion_offline/lifecycle.c`
- `g2/components/audio/pcm21_reset_offline/reset.c`
- `g2/components/audio/pcm21_reset_offline/reset.h`

[Exact inventory, hashes and receipt identities](snapshot.json).
