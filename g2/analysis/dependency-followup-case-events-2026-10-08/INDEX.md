# Case event dependency follow-up — bounded source progress

This resumes source/knowledge work after the15:22 rescan. Inventory counts are not completion. Four completed batches below have new rebuilt/rerun evidence; preceding UART/ILO counts are navigation only and were not rerun in this follow-up.

| Batch | Readable source | Newly validated scope |
| --- | --- | --- |
| [Frame parser](../case-frame-callback-closure-2026-10-08/REPORT.md) | [frame.c](../../components/case/frame_callback_offline/frame.c) |4830 comparisons; actual ordinary rearm, mask-at-write checks; timed receive/event post are explicit stop boundaries.|
| [CMSIS wrapper](../case-event-flags-closure-2026-10-08/REPORT.md) | [events.c](../../components/case/event_flags_offline/events.c) |336 modeled-kernel-child comparisons; mask preservation/PendSV-write mask;24 newer-version return controls differ.|
| [Deferred queue/producer](../case-deferred-event-closure-2026-10-08/REPORT.md) | [deferred.c](../../components/case/deferred_event_offline/deferred.c), [ABI](../../components/case/deferred_event_offline/deferred.h) |1936 comparisons; actual kernel queue/copy path, inline16-byte command ownership, stack poisoning, full-queue failure, critical writes, copy-from leaf.|
| [Negative-command consumer](../case-deferred-consumer-closure-2026-10-08/REPORT.md) | [consumer.c](../../components/case/deferred_consumer_offline/consumer.c) |189 drain comparisons; real original indirect event callback/event-set/suspend/resume peers, expected bits and callback order; synthetic empty-wait-list kernel state.|

Do not silently promote336 modeled-wrapper cases into original-kernel coverage. The later680 queue-integrated wrapper comparisons prove a separate empty-wait-list scope. The189 consumers execute real event mutation, but no suite observes a real daemon task schedule or lifetime interleave. Original disassembly windows can contain alignment/literals and unexecuted branches; they are not whole-function code-coverage counts.

Useful earlier source: [corrected UART IRQ/error](../case-uart-error-atomic-closure-2026-10-08/REPORT.md), [receive helpers](../case-uart-receive-closure-2026-10-08/REPORT.md), [receive setup](../case-uart-start-closure-2026-10-08/REPORT.md), [ILO measurement](../touch-ilo-compensation-closure-2026-10-08/REPORT.md), [ILO callback](../touch-ilo-pm-closure-2026-10-08/REPORT.md), [PM registration/dispatch](../touch-pm-callbacks-closure-2026-10-08/REPORT.md). The older uart_error_offline scaffold is preserved but superseded for masking; use uart_error_atomic_offline.

## Dependency leads remain actionable

- Official CMSIS-FreeRTOSv10.3.1/v10.4.6 selected event wrappers agree in the explicit model environment; registeredv10.5.1 differs in ISR return composition. Full IRQ-context configuration/release attribution remains open. No project gitlink re-pin performed.
- Official FreeRTOS-KernelV10.5.1 selected copy/producer algorithms agree under disclosed ABI scaffolds. Full public queue FromISR has task-count-capped lock increments; stock selected body increments directly. Source revision/configuration discrimination can continue without requiring hardware.
- Actual consumer wake/remove/wait-any/all/clear branches and event deletion/drain call paths are still available for bounded original-instruction analysis. ISR enqueue inline bytes are now owned by queue storage; borrowed event/callback lifetime remains the patch-design constraint.
- Timed case bulk-receive, parser post-return suffix, DMA/FIFO and positive timer commands are still analyzable. Missing runtime task traces limit scheduling conclusions; they do not exhaust available source work.

The broader dependency ledger includes Ambiq/ROM, Cordio/EM SDK, NationalChip, PDL, LVGL/Nema, storage/fonts, product glue/EvenHub and R1. Those areas were **not independently exhausted or freshly function-tested by this case follow-up**. See the existing [dependency follow-up](../dependency-followup-2026-10-08/REPORT.md), [dependency-interface ledger](../shortcut-batch-2026-10-05/dependency-interface-map.json) and [third-party registry](../../../third-party/README.md) for prior leads. No global source-exhaustion or complete-source/byte-identical claim.

No commits, index changes, production firmware edits or device writes. Prior761 sealed entries,110 audit inputs and4 candidate checkpoints were checked after new analysis; results remain additive offline artifacts.
