# Checkout rescan

Compared with the 2026-10-05T23:58:02.260865+00:00 snapshot, foundation C/header files increased from 77 to 83 (+6). Changed prior source hashes: 0; removed: 0. HEAD remains 4ab13514d. This is a read-only inspection of source/build evidence; this scan writes only this report and snapshot.

New source files:

- `g2/components/foundation/audio_cache_handoff/handoff.c`
- `g2/components/foundation/audio_cache_handoff/handoff.h`
- `g2/components/foundation/cache_maintenance/cache_maintenance.c`
- `g2/components/foundation/cache_maintenance/cache_maintenance.h`
- `g2/components/foundation/power_domain/power_domain.c`
- `g2/components/foundation/power_domain/power_domain.h`

These implement a 34-row power-domain descriptor lookup, two raw cache-maintenance functions, the I2S selected-buffer query and fixed 3200-byte audio receive handoff. Audio also has a separately labeled new capacity-check policy; those checks are not reconstructed stock firmware behavior. The raw getter invalidates before publishing a borrowed buffer pointer and length, copies no PCM, and establishes no exclusive ownership or DMA reuse guarantee. Its observed returned R0 is the selected pointer. A corrected return-value candidate and rejected checked-output alias candidate remain preserved as diagnostics.

Current saved comparisons: power descriptor 246 cases/92 traced bytes; cache 768/384; audio 282 original/source cases/160 traced bytes plus 1,157 separate new-policy cases. All report PASS; every recorded source-manifest hash, ELF hash and firmware hash matches the current files. No comparisons, builds or tests were rerun for this scan. Actual physical cache effects, DMA coherence and scheduling remain outside the fixtures.

Independently recalculated from 23 saved evidence inputs: **6816 distinct payload/address instruction bytes** ({'touch': 234, 'apollo_main': 6582}), up 526 from 6,290. Increments are power 58, cache 384, audio 84; overlapping callee bytes agree. The cumulative inventory now matches both total and per-payload breakdown, correcting the stale breakdown observed in the preceding scan. These are bounded execution traces, not source completeness or byte equality. Foundation file types: 37 implementation C, 35 headers, 11 simulator C.

Saved aggregate: 44 completed modules, 228 method tests, 222 passed, 6 method skips and 1 setup skip, 0 failures/errors. Affected log records 15 passing tests. Power and cache have independent review packets; audio review finished during this scan, bound the final source/ELF/result, and passed 13 independent native representative cases plus 4 inventory tests. Audio main REPORT, source README and SOURCE_PROVENANCE.json are still absent, so that delivery is not closed out despite source/build/comparison artifacts being present. Power preparation now has its narrative/provenance closeout.

Git views: {'tracked': 73, 'untracked': 10, 'ignored': 0}. All six additions are untracked and not ignored. `build/` at `.gitignore:15` hides simulator ELF and comparison JSON; it does not hide these source files or their analysis inventory. No global excludes are configured, no local info/exclude exists, and git reports one worktree at this checkout. No staged changes exist. The packer, manifest and workflow state still match their prior identities. No new commit was made.

The prior huge-positive cache-length failure is now classified as an **execution-budget limit**, not a demonstrated stock/source mismatch or unsupported input. Twelve retained stock/source prefix runs agree before the 30,000-instruction caps; full huge-length completion is explicitly unverified. This does not count as completed-path coverage. The optimized tick Unicorn instrumentation-sensitive blocker remains. Complete power timing still requires authenticated resident ROM at 0x40 and the clock/register contract; actual audio buffer liveness needs initialized DMA state and producer/interrupt/consumer evidence. No fully source-complete payload or source-built byte-identical bundle is established.
