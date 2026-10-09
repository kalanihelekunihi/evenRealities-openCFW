# UART/codec/RTOS successor source ledger

**Superseded interpretation:** [complete interrupt-clear instruction/MMIO check](../audio-uart-group-power-2026-10-09/interrupt-clear-difference.json) shows stock/source BOTH writeIEC, readMIS, fault on unmappedNULL. Earlier sealed mismatch claim was incorrect; historical files remain unchanged.

**Transport correction:** UART3 staging/drain belongs to GX8002 codec, per actual58FB2A callers and existing protocol reference. It is not the temple-sync stream. Earlier tentative UART3-to-sync next-lead wording is superseded.

| Evidence | Actual scope |
| --- | --- |
|[Native planners/apply routing](REPORT.md)|116comparisons;77complete,39real child-entry cuts; PCM2.2 native routing, PCM2.1 apply not completed|
|[ISR notifier and logger composition](../audio-uart-rx-notifier-2026-10-09/REPORT.md)|1440direct+36integrated; ready/pending lists and software yield flag; no context-switch delivery|
|[Codec drain](../audio-codec-uart-rx-drain-2026-10-09/REPORT.md)|320comparisons; UART3 retained-byte caller copy, no physical response|
|[Receiver/staging](../audio-uart-rx-consumer-2026-10-09/REPORT.md)|391receiver+216ring source cases;4originalprefix checks; scheduler cuts, synthetic loss/eviction|
|[Existing calibration/callback/ITCM](../audio-platform-callbacks-closure-2026-10-08/REPORT.md)|Startup sentinel/getter and authenticated initialized transition DATA reused|

Unexercised previous before-planner aliases for PCM2.1 classifier/PCM2.2 apply are corrected in current successor build. Counts describe fixtures and bounded source contracts, not whole-image completion or byte equality.
