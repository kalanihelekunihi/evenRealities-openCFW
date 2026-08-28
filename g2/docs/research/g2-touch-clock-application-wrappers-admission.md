# G2 Touch clock/application wrapper admission (batch 22)

This batch reduces six authenticated Touch prefix functions to freestanding
MIT C: `0x12AC`, `0x12D0`, `0x1434`, `0x17BE`, `0x1904`, and `0x1C54`.
Together they account for 316 authenticated instruction bytes.

The clock functions preserve divider validation, fault routing, the ordered
clock transition, rounded measurement, and derived frequency state. The
application functions preserve preflight/reset/status/finalize order, the
descending three-object aggregate, and the descending pointer-update wrapper.
Every resident or platform call is injected. Register mutations operate only
on caller-supplied volatile views; this batch contains no fixed-address
dereference and executes no MMIO itself.

Host behavior tests cover operation order, result propagation, object-state
filtering, derived clock values, and null-contract behavior. The same source
also compiles as freestanding Cortex-M0+ C with warnings treated as errors.

The source remains an isolated candidate and is not production-routed. Live
clock, CapSense, object-table, timing, and electrical behavior is blocked by
unavailable physical evidence because no authorized responsive G2 Touch
hardware is available. No flash, reset, signing, DFU, or MMIO operation was
performed.
