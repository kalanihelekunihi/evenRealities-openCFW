# OpenCFW rescan — 2026-10-08 12:57 UTC

Compared with the 11:50 UTC snapshot, there are **13 additional C/header files**, no changed prior source hashes, and no removed prior source files. The same inventory scope (C, headers and assembly under g2/components) now contains **537 files**, up from524. Of these,532 are in the Git index and5 are untracked; none is ignored. Index membership does not establish committed content or equality between index and disk.

## Concrete progress

The additions are base-frame generation (base.c/h), auto-dither (dither.c/h), clock selection (clock.c/h), scan preparation (prepare.c/h), scan ISR/dispatch (isr.c/h), and low-power history reset/decoder (reset.c,decoder.c,history.h), all under g2/components/touch. The history decoder is a new offline/app helper, not a recovered stock consumer. These remain bounded offline source artifacts, not a complete replacement firmware build.

Existing results record PASS for2304 base-frame cases,240 auto-dither cases,1583 clock-selection cases,348 preparation cases and1636 ISR/dispatch cases. These compare selected original instructions and independent source with explicit synthetic MMIO/state/callback limits. The unsealed history batch records594 PASS cases, including stock-reset/IRQ comparisons, original-only type7 bypass observations and new-decoder guard tests;594 must not be described as594 stock-equivalence tests. No tests were rerun for this scan.

The ISR work establishes actual project dispatch at0x3948, reset-copied context pointers, positional LP samples (disabled slots leave unwritten holes), continuation/completion behavior and FIFO transfer. It documents an unbounded history writer rather than demonstrating a hardware overflow. The history work is still unsealed; generated allocation size, physical IRQ delivery, analog behavior and hardware scheduling remain unverified. Prior source gates/full-image completeness and byte-identical rebuilding remain separate from these bounded results.

## Integrity and visibility

All582 sealed manifest entries checked match, all110 audit inputs match, and all4 preserved bootloader candidate checkpoints match. HEAD remains36ff5930a4e832156f9ee3111e83480756ebef37. This scan made no source edits, commits or index changes.

`git check-ignore -v --no-index` finds no rule for the13 added files. The scratch path g2/build/probe.elf is excluded by `.gitignore:15:build/`. No nested .gitignore exists under g2/components, .git/info/exclude is absent, and core.excludesFile is unset. One worktree remains registered. Thus .gitignore does not conceal the new source work.

Navigation: ../touch-scan-isr-closure-2026-10-08/REPORT.md; ../touch-scan-preparation-closure-2026-10-08/INDEX.md; ../touch-clock-selection-closure-2026-10-08/REPORT.md; ../touch-lp-history-closure-2026-10-08/results.json (unsealed). Exact file hashes/delta, Git visibility and preserved checkpoint evidence are in snapshot.json.
