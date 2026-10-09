# Successor evidence index

**Authoritative correction:** [complete instruction/MMIO check](../audio-uart-group-power-2026-10-09/interrupt-clear-difference.json) and [executable checker](../audio-uart-group-power-2026-10-09/verify_interrupt_clear_difference.py) supersede the interrupt-clear statements in the sealed [UART power/configuration report](../audio-uart-power-config-2026-10-09/REPORT.md) and pseudocode. The inferred stock/source mismatch was incorrect: both performIECwrite thenMISread and both fault on unmappedNULL before validation. This index is additive; sealed historical files remain unchanged. The checker binds the exact prior power/config ELF hash and executes unchanged stock bytes.

| Evidence | Scope and limit |
| --- | --- |
|[Current enclosing composition](REPORT.md),[408 cases](results.json)|UART11..14; source native providers plus retained original PCM2.0 action3 no-op; synthetic power status/delay|
|[Actual registrar traces](registration-results.json)|16 supplied chip/trim fixtures; stops before initializer callback; selection also documented in prior platform-callback source work|
|[Grouped helpers](../audio-uart-group-power-2026-10-09/REPORT.md)|240 MMIO/dispatch/poll comparisons; generic callback body cut|
|[Power/configuration](../audio-uart-power-config-2026-10-09/REPORT.md)|265 state comparisons; interrupt-clear interpretation superseded above; quotient-only division support|
|[RX ownership](../audio-uart-rx-stream-ownership-2026-10-09/REPORT.md)|582 cases; prefix copy and staging discard under synthetic pressure, no measured hardware loss|
|[TX ownership](../audio-uart-tx-ownership-2026-10-09/REPORT.md)|665 cases; borrow/copy/FIFO acceptance distinct from physical output|
|[Platform callbacks/trim getter](../audio-platform-callbacks-closure-2026-10-08/REPORT.md)|Existing registrar/calibration/source family evidence; supplied INFO values and retained dependency cuts|
|[PCM pending/temperature](../audio-early-pcm-pending-closure-2026-10-08/REPORT.md)|Existing postpone/drain/temperature source reused unchanged in this composition|

No count here implies whole-firmware completeness, independent review or byte-identical build.
