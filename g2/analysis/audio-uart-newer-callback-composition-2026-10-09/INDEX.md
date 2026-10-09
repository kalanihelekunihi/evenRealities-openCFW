# UART/RX successor evidence ledger

**Correction supersedes sealed UART power/configuration mismatch interpretation:** [complete unchanged instruction/MMIO trace](../audio-uart-group-power-2026-10-09/interrupt-clear-difference.json) confirms both stock and source writeIEC thenreadMIS and both fault on unmappedNULL. The inferred stock/source mismatch in earlier sealed report is incorrect; history remains unchanged.

| Current evidence | Proven scope / boundary |
| --- | --- |
|[Newer callback composition](REPORT.md)|96comparisons:72complete gate/timeout;24stop before actual planner; no fabricated planner result|
|[RX consumer and UART3 staging](../audio-uart-rx-consumer-2026-10-09/REPORT.md)|391receiver+216ring source comparisons;4originalprefix checks; scheduler stubs/cuts; synthetic pressure only|
|[UART power enclosing](../audio-uart-power-composition-2026-10-09/REPORT.md)|408comparisons+16registration traces; PCM2.0 source pre/post, original no-op groupcallback|
|[Existing platform callbacks](../audio-platform-callbacks-closure-2026-10-08/REPORT.md)|Revision producer/registrar/initializedITCM reused; supplied INFO, no live revision inference|
|[Existing protocol reference](../../docs/reference/protocols.md)|UARTsync task/parser already mapped; generic receiver source and staging ownership newly validated here|

Next source leads: compose reused PCM2.1/2.2 planners/apply within supported cuts, verify actual UART3 staging-drain-to-sync callback chain, receive completion notifier/task scheduling, and channel3TX IRQdrain. Counts are fixtures, not whole-image source/byte coverage or independent review.
