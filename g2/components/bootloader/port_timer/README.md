# Bootloader timer port

`opencfw_bl_port_timer_configure()` is a readable reconstruction of the
authenticated bootloader startup function at `0x0041b6fa`. Its tested source
and link recipe live in
[`upstream-worker/port-timer`](../../../analysis/bootloader-completion-2026-10-06/upstream-worker/port-timer/REPORT.md).

Compile `port_timer.c` and link it with definitions for `clock_request()` and
`clock_release()`. Those two private clock-manager services remain explicit
platform dependencies; the verification stubs in the analysis directory are
test-only and do not implement clock-tree effects. Call the configure hook
without using its return value: stock leaves R0 equal to an incoming, otherwise
unspecified R3 value.

The source preserves the literal interval value `0x20` separately from the
NVIC interrupt index 32. It does not assign time units to that value. STIMER,
NVIC, and the compare-shadow locations are fixed to the recovered target
addresses.
