# Audio lifecycle evidence and corrected dispatcher address

**Use dispatcher table 0x20003FBC.** Locked literal 0x53CEB4 supplies this address to dispatcher 0x53C5AC. Earlier sealed DMA/PCM/thread-flags reports containing 0x20073FBC are superseded on this address only; they remain unchanged. [Authenticated startup decoding](../audio-dispatch-initializer-closure-2026-10-08/REPORT.md) now establishes all eight initial rows, including type2 → 0x53C6F3. Later runtime writes and scheduling remain unverified.

| Provider | Accepted successor evidence | Remaining boundary |
| --- | --- | --- |
| Set flags 0x449238 | [thread flags](../audio-thread-flags-closure-2026-10-08/REPORT.md), 1,440 comparisons | Nonwaiting fixture; its table address is corrected above. |
| Waiting ISR notify 0x455DC0 | [wake](../audio-notification-wake-closure-2026-10-08/REPORT.md), 864 comparisons | Pending-ready resume/context switch. |
| Wait 0x4492C2 / 0x455B84 | [wait](../audio-notification-wait-closure-2026-10-08/REPORT.md), 768 comparisons | 120 stop before blocking; no expiration. |
| Exit prefix 0x53CDC2 | [cleanup](../audio-exit-cleanup-closure-2026-10-08/REPORT.md), 20 comparisons | Event request is not a producer-stop acknowledgment; ISR rejection fixtures are not demonstrated hardware failures. |
| Queue delete 0x449BEC / heap 0x456210 | [valid deletion](../audio-queue-delete-closure-2026-10-08/REPORT.md), 64 comparisons | Actual queue configuration, pending tasks and producer quiescence. |

These are bounded offline reconstructed C providers and original-instruction evidence, not a complete kernel, safe firmware patch or source-complete bundle. Initialized dispatcher rows are now recovered; live lifecycle ordering remains an open question.
