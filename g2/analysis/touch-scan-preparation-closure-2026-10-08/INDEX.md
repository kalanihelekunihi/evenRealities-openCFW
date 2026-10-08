# Touch knowledge: latest bounded closures

| Family | Source | Evidence |
|---|---|---|
|Clock selection/LFSR/PRS/SSC/timer|clock_selection_offline/clock.c,h|1,583 comparisons;42 exact compiled public-helper bytes|
|Stock preparation/dither measurement and scale|scan_preparation_offline/prepare.c,h|348 comparisons; actual closed-source composition; explicit synthetic limits|
|Base/mode/pin and auto-dither/all-slot|../touch-auto-dither-closure-2026-10-08/INDEX.md|Earlier2,304+240 fresh comparisons,144 preserved all-slot cases|
|Earlier mode, GPIO, initialization, per-sensor frames|../touch-mode-closure-2026-10-08/INDEX.md|Individual suites and attribution limits|

See REPORT.md and ../touch-clock-selection-closure-2026-10-08/REPORT.md. build_offline.py rebuilds clock and preparation ELFs into an explicit scratch directory; verify.py in each corresponding analysis directory runs original instructions against the source. screen_public_helpers.py independently reproduces selected public-helper matches from hash-pinned source. No commits/index/production/device writes.

Next lead is ISR0x6780 and its four data/completion helpers. The stored0x6781 pointer is metadata, not an implemented ISR. Synthetic completion/FIFO does not prove physical timing or analog response. Whole-image source completion/byte equality remains separate.
