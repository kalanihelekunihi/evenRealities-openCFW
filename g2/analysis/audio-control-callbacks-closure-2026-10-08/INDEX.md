# Current audio control, cleanup and scheduler evidence

**Stop-handshake correction remains authoritative:** manager requests thread flag0x800000; audio posts event8 before timer/queue cleanup. That event is acknowledgment of the exit path, not producer quiescence or cleanup completion. Older sealed “initial request” wording remains preserved and superseded by the [stop-handshake report](../audio-stop-handshake-closure-2026-10-08/REPORT.md).

| Newly explained layer | Evidence and limit |
| --- | --- |
| [Type0/type1 control callbacks](REPORT.md) | 576 comparisons. Authenticated dispatcher0x20003FBC; low-byte value aliases, role/variant routing; active marker clears before later stop providers. IRQ44 disable executes; clock/PDM/DSP providers remain boundaries. |
| [Diagnostic codec/PDM deinit](../audio-diagnostic-deinit-closure-2026-10-08/REPORT.md) | 64 comparisons. Disable queued before owner gate; owner error does not undo publication. Recorder/encoder dependencies are first-instruction cuts. |
| [Timer command consumer](../audio-timer-commands-closure-2026-10-08/REPORT.md) | 32 comparisons. Enqueue leaves timer intact; daemon stop/delete unlinks, clears active or frees dynamic object. No callback concurrency or expiry. |
| [Pending-ready resume](../audio-pending-resume-closure-2026-10-08/REPORT.md) | 84 comparisons. Final resume transfers ownership and requests yield for equal/higher priority. Stops before yield, pendingTicks0. |

Related completed evidence: [authentic dispatcher initialization](../audio-dispatch-initializer-closure-2026-10-08/REPORT.md), [static audio task and dynamic queue configuration](../audio-task-configuration-closure-2026-10-08/REPORT.md), [notification wait](../audio-notification-wait-closure-2026-10-08/REPORT.md), [queue delete ownership](../audio-queue-delete-closure-2026-10-08/REPORT.md).

Next actionable source leads: clock/power/DMA stop provider completion; DSP/PDM disable internals; file-close and LC3 setup; CMSIS timer auxiliary callback allocation/free and callback cancellation; notification blocking/nonzero pending ticks/PendSV; deinit caller ordering and remaining boot task configuration. None requires assuming a stop acknowledgment is a release fence. Live ISR/DMA/preemption ordering remains a missing trace boundary, not a claim of global source exhaustion.
