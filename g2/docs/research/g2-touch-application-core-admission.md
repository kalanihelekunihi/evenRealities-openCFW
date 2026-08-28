# G2 Touch application core admission (batch 23)

This batch reduces four authenticated application functions to freestanding
MIT C: `0x17F4`, `0x18A8`, `0x1B6C`, and `0x2638`. They account for 706
authenticated instruction bytes.

The source preserves the top-level initialization, retry, timeout, cleanup,
and three-object update flow; per-object lifecycle and mode policy; coefficient
passes; and sample prepare/process/finalize aggregation. Object memory is
represented by caller-owned typed views. Every resident algorithm or platform
operation is injected, and no resident body, fixed-address dereference, live
MMIO, flash, reset, signing, or DFU action is included.

Host tests cover order, flags, coefficient offsets, mode state, result OR-ing,
timeout behavior, cleanup on preflight failure, and null-contract behavior.
The same source compiles as freestanding Cortex-M0+ C with warnings as errors.

The source is not yet production-routed. Physical CapSense, timing, object
layout, and electrical behavior remain blocked by unavailable physical
evidence because no authorized responsive G2 Touch device is available.
