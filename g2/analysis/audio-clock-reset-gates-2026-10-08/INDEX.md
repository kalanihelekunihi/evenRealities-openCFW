# Current bounded source closure

- [Variant initialization/capture](../audio-trim-initialization-closure-2026-10-08/REPORT.md): 1,310 comparisons; native complete variant/no-op bodies and bounded one-time capture.
- [Common startup suffix/reset](../audio-common-startup-closure-2026-10-08/REPORT.md): 3,784 comparisons; composed native capture/TON/LP callbacks, actual original dependencies, PCM2.2 reset.
- [Clock reset gates](REPORT.md): 392 comparisons, including31 complete gated original-function paths; explicit retained-state writes now checked.

Open source leads: active clock recovery0x44B1D0..0x44B4DC and common initializer prefix0x47FAE8..0x47FC14. Pinned source is available; no external input prevents static/native analysis. Physical clock/rail readiness and authentic factory/retained state remain needed for hardware conclusions. Source exhaustion is not reached. No whole-firmware completeness metric is claimed.
