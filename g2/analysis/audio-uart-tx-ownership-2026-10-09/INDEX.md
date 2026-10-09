# UART dependency-source ledger successor

[Current batch](REPORT.md) resolves logger source-buffer consumption through selected TX providers and actual initialized channel defaults. [Earlier ledger](../audio-logger-stock-provider-closure-2026-10-09/INDEX.md) remains sealed; its pending UART ownership/initialization row is superseded within these explicit limits.

| Family | Artifact and boundary |
|---|---|
| UART TX / HAL initialize / queue | Eleven unchanged selected SDK bodies;650 direct,6sink,4marker,3lifetime and1channel-init source compositions. Physical readiness/delay/IRQ delivery and peripheral setup remain synthetic or stubbed. |
| Main initialized SRAM | Full17752byte record matches original instruction-stepped decoder; partial reset/scatter only. |
| Logger registration / trace disable | [Prior batch](../audio-logger-stock-provider-closure-2026-10-09/REPORT.md): actual UART sink installer recovered from raw call evidence missing in decomp;681source +9prefix cases. |
| Pool/heap, formatter, semaphore and PCM | [Prior cumulative index](../audio-logger-stock-provider-closure-2026-10-09/INDEX.md), with exact per-batch counts/reuse and limits. |

Next source-ledger leads, grounded in current logger path:

1. UART RX0x58E618 and callback0x5415E6 / channel0x55E4EC: caller storage, ISR-to-stream copy and event ownership.
2. UART configuration0x58E09E and power0x58DBB8; pinned source available, physical state remains outside offline proof.
3. UART channel3 TX queue default1024B: app-facing routing/interrupt/drain behavior distinct from logger's directFIFO path.
4. Shared formatter buffer reentrancy requires actual task/preemption evidence or a validated scheduler model; no speculative lifetime patch.

Whole-image/source-complete/byte-equality gates are unestablished. Function/case counts are not coverage completeness; author validation is not independent review. Static source leads are not exhausted.
