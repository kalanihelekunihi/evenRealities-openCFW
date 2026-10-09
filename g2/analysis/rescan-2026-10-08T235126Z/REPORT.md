# OpenCFW change scan

Compared with the [23:09 scan](../rescan-2026-10-08T230918Z/REPORT.md), component C/header/assembly inventory grew **661 → 671 files: ten added, none modified or removed**. There are **654 indexed and 17 untracked sources; zero ignore matches**. Counts include partial and historical helpers, not firmware completeness.

## New source and understanding

| Batch | Newly recorded native bodies | Recorded direct validation | What changed |
| --- | ---: | ---: | --- |
| [SYSPLL generator](../audio-syspll-generator-closure-2026-10-08/REPORT.md) | 6 | 2,530 comparisons | Divider selection, integer/fractional limits, partial-write failures and malformed-input behavior |
| [Clock dispatch](../audio-clock-public-dispatch-closure-2026-10-08/REPORT.md) | 6 | 1,584 comparisons | Low-speed ownership and public clock/user byte narrowing |
| [Float runtime](../audio-float-runtime-closure-2026-10-08/REPORT.md) | 4 | 13,920 comparisons | Exact floor/round/ceil/fmod bit behavior, signed zero, NaNs and errno |
| [Timing/IRQ](../audio-clock-timing-closure-2026-10-08/REPORT.md) | 5 | 1,598 comparisons | IRQ mask preservation, delay arithmetic and poll-budget boundaries |
| [Timer ordering](../audio-timer-daemon-order-closure-2026-10-08/REPORT.md) | 5 | 62 comparisons | Due-before-command-drain selection under constructed timer/queue states |

These five batches record **26 native function bodies** in five C/header pairs. The counts and validation are delivered author records; this scan checked artifact hashes and inspected receipts, without rerunning tests or independently reviewing correctness. Reused regression counts overlap and must not be summed as distinct firmware coverage.

The timing batch's final combined ELF records **23,035 comparisons**, zero original executable aliases and zero unresolved symbols. Every reached source instruction was guarded to remain in the native code region. This closes the exercised clock software chain, replacing previously retained math/timing executable dependencies. Authenticated initialization/scalar data and synthetic MMIO remain inputs: this is not a complete firmware source build or proof of physical timing/PLL readiness.

## Timer evidence needs a narrower interpretation

The new timer batch proves conditional due-before-drain selection, but its pre-due fixture allows the port-yield helper to return with exception delivery unmodeled. Its reported completed drain after that yield is therefore a passive-emulator continuation, not verified task handover. The fixture field named `scheduler_suspended` reads task-count address0x20074A30; actual suspension state is0x20074A58. Prior sealed artifacts are preserved; this scan records the qualification additively.

Existing [task configuration](../audio-task-configuration-closure-2026-10-08/REPORT.md), [daemon configuration](../audio-timer-daemon-closure-2026-10-08/REPORT.md) and [delete wake](../audio-timer-delete-wake-closure-2026-10-08/REPORT.md) evidence establishes stock audio priority47 and timer priority54. A waiting timer receiver can request a yield before the delete wrapper frees auxiliary storage. A daemon already blocked in the wait path resumes toward command drain before its next expiry-selection iteration. Thus the constructed freed-auxiliary/due-entry cases do not establish a reachable live hardware fault. Actual task PC, queue/timer/tick state and exception/scheduling trace remain required to settle live reachability or patch safety.

## Visibility and preservation

All ten new source files are untracked and visible to Git. Root ignore rules hide build trees, object/ELF output and decompiler databases, not these sources. One registered worktree remains; HEAD is unchanged at36337d9b39ff36d318b0531f2968ca7e0554a7b1.

All **2440 dictionary-form seal entries**, **110 audit inputs** and **four prior candidate checkpoints** match. Three other manifest formats are outside this seal-check scope and listed in the snapshot. The index hash stayed unchanged during this scan. No source, existing evidence, shared state, staging, firmware or device was changed; only this report and snapshot were added.

The workflow still records P2 executing; whole-corpus completion/freeze and source-complete/byte-identical-build gates remain not run. Real source progress is visible, but complete reconstructable firmware and OTA byte equality remain unestablished.

[Exact added paths, hashes, validation receipts and preservation results](snapshot.json).
