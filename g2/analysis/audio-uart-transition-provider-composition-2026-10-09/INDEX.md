# Successor access/source ledger

| Evidence | Current validated boundary |
| --- | --- |
|[Transition-child composition](REPORT.md)|32cases:24strictread/write matches;8extra source timer read; all32ordered writes/relevant state/defined provider args match. Not full-equivalence PASS|
|[Codec deadline](../audio-codec-uart-deadline-2026-10-09/REPORT.md)|112comparisons; actual tick wrapper plus synthetic kernel/delay/arrival; bounded wrap/sign-extension cuts|
|[ISR notifier](../audio-uart-rx-notifier-2026-10-09/REPORT.md)|1476comparisons/compositions; readiness lists and software yield flag, no actual switch|
|[Codec drain](../audio-codec-uart-rx-drain-2026-10-09/REPORT.md)|320copies/wrap/drains; actual UART3 codec role|
|[Prior source transition family](../audio-transition-producers-closure-2026-10-08/REPORT.md)|All27bodies already recovered; current composition reuses them and exposes extra-read limit|

Authoritative [interrupt-clear correction](../audio-uart-group-power-2026-10-09/interrupt-clear-difference.json): stock/source BOTH writeIEC thenreadMIS and fault on unmappedNULL; old inferred mismatch remains superseded. UART3 belongs to codec, not temple-sync.

Next useful source leads: explicit cached-timer read successor forsequence0, codec response parser57C1FC including CRC and distinct elapsed-time arithmetic, actual ISR-exit/resume handling after software yield flags. Do not turn missing scheduling/device traces into a hardware-patch safety claim or call source searches exhausted.
