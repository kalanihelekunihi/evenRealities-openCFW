# OpenCFW rescan — 2026-10-08 18:41 UTC

Compared with the [17:34 scan](../rescan-2026-10-08T173422Z/REPORT.md), component C/header/assembly inventory grew **587 → 600 files: 13 added, none modified or removed**. **532 are in the Git index, 68 untracked, zero ignored.** This includes scaffolds and historical implementations, not a source-completeness measure.

## New source and recorded validation

| Batch | Recorded comparisons | What it establishes / boundary |
|---|---:|---|
| [Encoder setup](../audio-encoder-setup-closure-2026-10-08/REPORT.md) | 181 | Selector validation and in-place reset; not encode-body/workspace lifetime completeness |
| [I2S stop](../audio-i2s-stop-closure-2026-10-08/REPORT.md) | 1,296 | Stop and selected matching-source reconfiguration; passive MMIO |
| [Clock release](../audio-i2s-clock-release-closure-2026-10-08/REPORT.md) | 88 | Last-client power command; command write is not physical completion |
| [File close](../audio-file-close-closure-2026-10-08/REPORT.md) | 48 | Actual mutex/TLSF and clean/error-marked close paths; dirty block I/O remains untested |
| [Delayed block](../audio-delayed-block-closure-2026-10-08/REPORT.md) | 96 | Ready-to-delayed/suspended list ownership; no completed blocked-call return |
| [PendSV](../audio-pendsv-closure-2026-10-08/REPORT.md) | 32 | Selected integer/FP context save/restore under M33-compatible profile; stops before exception return |
| [I2S power/uninitialize](../audio-i2s-power-closure-2026-10-08/REPORT.md) | 868 | Snapshot/restore, rollback, software uninitialize; eight separate original-only delay probes reach unavailable ROM0x40 |
| [Tick expiry](../audio-tick-expiry-closure-2026-10-08/REPORT.md) | 576 | Timeout list transfer and switch request; readiness does not imply notification received |
| [Pending-tick resume](../audio-resume-ticks-closure-2026-10-08/REPORT.md) | 432 | Pending-ready transfer precedes accumulated tick replay |
| [Timer daemon](../audio-timer-daemon-closure-2026-10-08/REPORT.md) | 40 + 1 static creation | Iteration order, actual entry0x47E878, priority54 and16KiB static stack; no live scheduling |
| [Timer wrap](../audio-timer-wrap-closure-2026-10-08/REPORT.md) | 128 | Expiry/autoreload precedes list swap; nonempty old-list tests stop at callback entry |
| [Restricted queue wait](../audio-timer-queue-wait-closure-2026-10-08/REPORT.md) | 96 | Timer receiver/event/state list ownership; no context handover |
| [Delete/waiter integration](../audio-timer-delete-wake-closure-2026-10-08/REPORT.md) | 48 | Reuses existing source: higher-priority wake reaches yield before auxiliary free |

The timer auxiliary batch that was unsealed at the previous scan now has [sealed evidence](../audio-timer-aux-lifetime-closure-2026-10-08/REPORT.md), including its previously recorded50 lifecycle and38 sizing comparisons. These are not newly rerun tests. The existing [provider index](../dependency-followup-audio-providers-2026-10-08/INDEX.md) aids navigation; its “next leads” are historical and several are now covered by the successors above.

## Material implications

The stock timer task priority54 exceeds audio47. Constructed sender47/blocked receiver54 delete tests publish the queue command then stop at actual yield entry while callback auxiliary storage remains allocated. Lower/equal-priority or absent receivers allow dynamic auxiliary release. Consequently, queued deletion alone does not establish a live lifetime defect. Earlier late-callback/reuse demonstrations remain synthetic. Task PC/wait state and actual scheduling are needed to settle live ordering.

Uninitialize clears software marker/module fields without proving DMA quiescence or physical power completion. Power retry reaches resident ROM0x40 absent from the OTA; executing that dependency requires authenticated ROM bytes or a defensible external contract. Dirty-close validation requires coherent mounted filesystem/cache/block state. Exception-return and real scheduler/device timing remain explicit limits.

## Preservation and visibility

All **1,157 sealed entries**, **110 audit inputs**, and **four candidate checkpoints** match their recorded hashes:147 additional sealed entries since the preceding scan. HEAD is unchanged at36ff5930a4e832156f9ee3111e83480756ebef37. No behavioral suites, generators or firmware were executed during this scan. Existing source, index and campaign state were preserved; only this new report/snapshot were written.

`git check-ignore -v --no-index` matches none of the600 source files. `.gitignore:15:build/` continues to hide `g2/build/probe.elf`; one worktree is registered and no configured global excludes file was returned. **Gitignore is not hiding the new source.** Committed-only views miss untracked additions.

These are bounded reconstructed source and knowledge artifacts, not a complete source-built or byte-identical firmware bundle. Validation counts are existing author-recorded comparisons under synthetic state and specified child boundaries; this scan independently verified file preservation, not behavioral correctness. [Exact source delta, hashes, Git state and checkpoints](snapshot.json).
