# OpenCFW rescan — 2026-10-08 15:22 UTC

Compared with the previous 14:10 UTC scan, the identical `g2/components` inventory scope (`.c`, `.h`, `.S`) grew from **546 to 562 files: 16 added, none modified or removed**. All additions are C/header files. The count includes two files from a superseded UART test scaffold, so it is not a measure of distinct completed functionality. There are **532 files in the Git index and 30 untracked files**, with **zero ignored source files**. Index membership is not proof of committed content or matching index/disk bytes.

## What changed

| Added component | Files | Existing validation evidence and limits |
| --- | --- | --- |
| ILO power-management callback | `touch/ilo_pm_offline/pm.c,h` | Sealed, 342 PASS cases; readiness prevention/clear phases and installed callback. Physical oscillator/wake behavior remains outside the fixture. |
| Power-management callback registration/dispatch | `touch/pm_callbacks_offline/callbacks.c,h` | Sealed, 386 PASS cases; sorted registration, phase traversal/cancellation and installed-ILO sleep path. Sleep execution ends at WFI or refusal; actual wake is not tested. |
| UART RX/error handling, older scaffold | `case/uart_error_offline/uart.c,h` | Preserved and sealed, but its atomic masking implication is superseded. Do not use its PASS count as additional independent coverage. |
| Corrected UART RX/error handling | `case/uart_error_atomic_offline/uart.c,h` | Sealed, 6,768 PASS cases. Checks interrupt mask at register writes; rejects the older scaffold. RX/error IRQ prefix only, plus full EndRx helper; DMA and remaining IRQ branches excluded. |
| UART receive helpers | `case/uart_receive_offline/receive.c,h` | Sealed, 5,120 PASS original/independent/public-source comparisons. Completion callbacks are explicit execution boundaries. Selected v1.4.5 source matches where tested; this does not identify the entire SDK release. |
| UART receive-start API/helper | `case/uart_start_offline/start.c,h` | Sealed, 2,312 PASS cases. Recovers caller-buffer setup, validation, masks and plain/FIFO handler selection. Selected handler pointers are metadata here, not FIFO execution proof. |
| Product case frame callback | `case/frame_callback_offline/frame.c,h` | **Unsealed work in progress**, 4,830 PASS cases recorded. Includes parser prefix, resynchronization and DE predicate; bulk receive/event-post calls terminate tests before the child executes. Post-bulk continuation is reconstructed but not exercised by those boundary cases. |
| CMSIS event-flags wrapper | `case/event_flags_offline/events.c,h` | **Unsealed work in progress**, 336 PASS wrapper cases with explicit modeled kernel children. These are not actual queue/scheduler integration tests. |

The previously present ILO compensation batch now has its report and deliverable manifests; its recorded 1,489 cases are not newly added coverage in this scan.

## New useful understanding

UART receive setup retains the caller's buffer; selected receive helpers store masked bytes/halfwords and advance its pointer, without allocation or release. Completion restores ready state and clears the receive handler. The receive-start API rejects zero length and invalid pointers/alignment, but a direct synthetic receive-helper invocation with count zero wraps the count after writing. That fixture does not prove a reachable hardware overflow.

The case frame callback recognizes binary `5A A5` headers with type `7F` or `CF`, and a case-insensitive `DE` prefix completed by newline. The `7F` branch requests an 8-bit body length; `CF` requests a little-endian 16-bit length. Bulk-read arguments carry timeout literals 10/20; this scan does not establish physical elapsed units. Frame completion posts flag `0x08`; receive-rearm failure posts `0x40`. The reconstructed bulk-read path lacks a capacity check before issuing the request, but the current tests stop at that call and do not prove an actual overwrite or host acceptance.

The CMSIS wrapper rejects null handles and flags outside the low 24 bits. It chooses ISR/thread behavior using IPSR. On modeled ISR success stock returns the requested bits, differing in 24 selected comparisons from registered public v10.5.1 code that includes existing bits. Public v10.3.1/v10.4.6 selected wrappers agree under the explicitly supplied context/kernel models. This is a scoped version lead, not justification to re-pin the project or claim actual scheduler behavior.

**Correction:** the earlier UART scaffold used an inline-assembly output constraint that allowed the saved interrupt-mask register to overlap the input containing 1. Tests comparing only final state missed that it failed to mask interrupts during updates. The corrected successor uses an early-clobber constraint and checks PRIMASK at each atomic register write. This was a reconstruction/test error, not an observed stock firmware bug. The old files are deliberately preserved; the successor is the usable version.

## Preservation and visibility

All **761 sealed manifest entries**, **110 audit inputs**, and **four bootloader candidate checkpoints** match their recorded hashes. HEAD remains `36ff5930a4e832156f9ee3111e83480756ebef37`. No generator execution, test reruns, staging, commits, firmware edits or hardware actions occurred during this scan; PASS counts above were read from existing result files/reports.

`git check-ignore -v --no-index` finds no matching rule for any of the 562 inventoried source files. `g2/build/probe.elf` still matches `.gitignore:15:build/`. There are no nested component ignore files, `.git/info/exclude` is absent, `core.excludesFile` is unset, and one worktree is registered. **Git ignore rules are not hiding these new source artifacts.** Many are untracked and offline components rather than integrated firmware sources, which explains a difference between committed views and actual work on disk.

## Remaining boundaries and navigation

This is measurable progress in bounded offline source and firmware understanding, not a complete source-built or byte-identical bundle. Actual RTOS queue copy/consumer execution, scheduler configuration, timed bulk-receive behavior, remaining UART DMA/FIFO/IRQ paths, physical wake/analog behavior and whole-image completeness remain unproven. The two unsealed parser/event batches need final reports/provenance review; a PASS JSON alone does not make them complete. Public source leads remain actionable, so this scan establishes no global source-exhaustion claim.

- [Exact file delta, hashes, visibility and preservation checks](snapshot.json)
- [ILO compensation](../touch-ilo-compensation-closure-2026-10-08/REPORT.md)
- [ILO PM callback](../touch-ilo-pm-closure-2026-10-08/REPORT.md)
- [PM registration and dispatch](../touch-pm-callbacks-closure-2026-10-08/REPORT.md)
- [Corrected UART masking and error handling](../case-uart-error-atomic-closure-2026-10-08/REPORT.md)
- [UART receive helpers and version comparison](../case-uart-receive-closure-2026-10-08/REPORT.md)
- [UART receive start](../case-uart-start-closure-2026-10-08/REPORT.md)
- [Frame callback source, unsealed](../../components/case/frame_callback_offline/frame.c)
- [Frame results, unsealed](../case-frame-callback-closure-2026-10-08/results.json)
- [Event wrapper source, unsealed](../../components/case/event_flags_offline/events.c)
- [Event wrapper results, modeled children, unsealed](../case-event-flags-closure-2026-10-08/results.json)
