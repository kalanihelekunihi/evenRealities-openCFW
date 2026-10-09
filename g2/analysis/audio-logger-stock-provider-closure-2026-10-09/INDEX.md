# Dependency source ledger successor

This additive index supersedes pending memory-pool/formatter/logger-provider rows; prior seals remain immutable.

| Completed batch | Evidence and boundary |
|---|---|
| [Memory pool / main heap](../audio-cmsis-memory-pool-closure-2026-10-09/REPORT.md) |484 comparisons; allocation/free geometry and failure loop. Actual resumed scheduling remains unresolved. |
| [Main formatter](../audio-main-formatter-source-successor-2026-10-09/REPORT.md) |88 comparisons; scalar Thumb/VFP CortexA15 profile, not CortexM exception model. Synthetic sink only in that batch. |
| [Logger disable prefix](../audio-logger-disable-path-2026-10-09/REPORT.md) |5 original fixtures, child stubs; preserved predecessor. |
| [Original trace composition / zero-init](../audio-logger-provider-composition-2026-10-09/REPORT.md) |24 provider fixtures +1 real first zero-fill record. Partial scatter only. |
| [Native trace/debug/poll and actual UART sink](REPORT.md) |681 source comparisons +9 original prefix/driver-boundary cases. Ten selected unchanged SDK function texts; GPIO source reused. Delay/peripheral-power and UART TX completion are explicit limits. |
| [Semaphore/PCM corrected source chain](../dependency-source-ledger-semaphore-successor-2026-10-09/INDEX.md) |Previously sealed source and original-instruction evidence; historical memory-pool pending row superseded. |

Case counts include reused providers/fixtures and are not unique function or byte-coverage totals. No whole-corpus/source-complete/byte-identical build gate established.

Next: actual UART transfer child ownership/queue/interrupt semantics, rooted in discovered main logger sink and pinned am_hal_uart.c. Separate remaining leads: live scheduler handover; PCM common registration/cache/calibration/retention composition; computed writes to logger disable flag. Global searches are not exhausted.
