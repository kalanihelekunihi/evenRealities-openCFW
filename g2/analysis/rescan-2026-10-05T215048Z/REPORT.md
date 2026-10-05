# Checkout rescan

Compared with `rescan-2026-10-05T205632Z`, foundation C/header files increased from 50 to 59: nine additions in freertos_resume and freertos_tick. All 50 earlier source hashes are unchanged; no earlier source was removed. Sources include pinned FreeRTOS subsets, reconstructed helpers, interfaces and simulator providers, so file counts are not nine newly reconstructed firmware functions.

The formerly pending ready-list batch now has a saved PASS comparison: 301 cases, 280 additional disjoint original instruction bytes. Resume adds 267 cases and 308 disjoint bytes. Tick has 271 cases and 328 additional disjoint bytes under its explicit O0 semantic profile. The cumulative foundation evidence ledger increased from 3,250 to 4,166 unique original instruction bytes (+916). This is bounded source-comparison evidence, not whole-firmware semantic coverage or byte-identical compiled source. Comparison artifact hashes still match their saved inventories; current per-result source-manifest checks are recorded in snapshot.json. Tests were not rerun for this scan.

Optimized tick correctness remains unresolved. The saved diagnostic hook matrix reports O2 and O2-with-no-strict-aliasing completing without memory hooks, but failing with memory hooks; O0 completes in each tested hook configuration. This narrows the failure to an instrumentation-sensitive execution case but does not establish a complete optimized correctness proof or rule out separate C aliasing concerns. The failing diagnostics remain preserved in unicorn-it-divergence-2026-10-05 and the ignored build directory.

Source files are not ignored. New daemon/ready/resume/tick directories remain untracked, while earlier foundation additions are predominantly staged. The tick ELF is ignored by .gitignore line15 (`build/`). Committed-only or staged-only views therefore miss real new source work.

Zero fully source-complete payloads and no source-built byte-identical bundle are established. Whole-image percentages from the earlier assessment were not remeasured. Scheduler selection/context switching, hardware behavior, and optimized tick validation remain outside the passing result. Preserve the optimized failure as a correctness gate before further scheduler expansion.

This scan made no firmware/source changes, ran no generator/emulator/build, and staged or committed nothing.
