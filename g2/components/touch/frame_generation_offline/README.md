# Independent per-sensor frame generation

Interfaces in generator.h; [layouts, original-instruction comparisons and limits](../../../analysis/touch-frame-generation-closure-2026-10-08/REPORT.md).

`touch_generate_sensor` exposes a CDAC callback for comparison; `touch_generate_sensor_closed` uses independently recovered CDAC source. Full all-slot generation and analog acquisition are outside this module. Frame words contain packed register fields; they are not measured physical quantities.
