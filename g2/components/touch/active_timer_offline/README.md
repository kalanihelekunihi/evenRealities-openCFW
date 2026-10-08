# Offline active interval and launch reconstruction

Independent source reconstructs setter5d90, active launch6bd4 and successful state1 budget tail3d7e. Interval input units are microseconds by pinned SDK semantic evidence; actual time depends on ILO compensation/hardware. Setter caches active interval, changes live AOS only for active status0x10, and never changes LP/WOT cache. Launch composes existing mode/GPIO/PDL/slot loader; failures may retain busy state. Budget decrement is a conditional software count with unsigned wrap, not a physical timer.

Evidence: ../../../analysis/touch-active-timer-closure-2026-10-08/REPORT.md.1160 bounded cases include three-way public/original/independent setter checks and LP→active/ISR/reuse composition. Public setter is behaviorally validated, not byte-exact attributed. Synthetic peripheral/IRQ/clock inputs and null callback limits apply; no production firmware patch or complete-image claim.
