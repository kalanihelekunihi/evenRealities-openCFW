# Startup/provider closure checkpoint

- [Clock recovery and common initializer](../audio-clock-reset-active-2026-10-08/REPORT.md): full native control flows; original providers and synthetic calibration/readiness.
- [GPIO/request providers](REPORT.md): four newly native functions;2,432 comparisons plus10 original-only caller assertions. GPIO native replacements execute in clock and common initializer callers.
- [Earlier reset/suffix](../audio-common-startup-closure-2026-10-08/REPORT.md): distinct PCM2.2 reset body and startup suffix.

Next concrete providers: INFO1 population0x47F954; MCU memory configuration0x47F204; SRAM configuration0x47F46A; oscillator control0x4809C4. Pinned source remains actionable. Source-search exhaustion has not been reached. Hardware/factory/live-state gaps remain separate from available-source inference.
