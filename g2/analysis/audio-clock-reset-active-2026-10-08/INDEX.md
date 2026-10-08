# Updated startup source closure

- [Prior variant/capture](../audio-trim-initialization-closure-2026-10-08/REPORT.md):1,310 comparisons, sealed and reused.
- [Prior common suffix/reset](../audio-common-startup-closure-2026-10-08/REPORT.md):3,784 comparisons, sealed and reused.
- [Prior clock gate/epilogue](../audio-clock-reset-gates-2026-10-08/REPORT.md):392 comparisons, retained write semantics explicitly checked.
- [Active clock and full initializer](REPORT.md):1,392 comparisons; native full control flow with original external providers and explicit incoming-R5 semantics.

Next source-backed dependency families: INFO1 population0x47F954; memory configuration0x47F204/0x47F46A; oscillator/microcontroller control0x4809C4; GPIO pin get/config0x480EEE/0x480F0C. SDK source is available, so no source-exhaustion claim is justified. Hardware calibration/clock readiness and live scheduler/IRQ traces remain separate external boundaries.
