# Delayed-event timer correlation

The 376-byte function `0x00065F84..<0x000660FC`, SHA-256
`85425913877b78226afdccf4570d9e082d9c4bd8ed47736da3d98531fc50402f`,
is the R1 firmware-event-loop delayed timer callback. Its two direct callers
are the delayed-event insertion tail call at `0x00065C78` and the cancellation
reschedule call at `0x00065E40`. Its disposition is `r1_product_specific` /
`clean_room_behavior_only`.

The callback manages 64 logical slots held in three parallel 256-byte arrays:
event UInt32, context UInt32, and remaining-milliseconds UInt32. A normal timer
callback subtracts the previously programmed delay. Direct calls carry an
elapsed override by setting the top byte to `0xFF`; the callback then uses only
the low 24 bits. Countdown subtraction saturates at zero.

Due entries are processed in ascending slot order. The event field is cleared,
the context and event are handed to the adjacent queue producer with timeout
`0xFFFFFFFF`, and stale context/countdown fields are left untouched. A second
64-slot scan finds the minimum remaining delay. The callback stores that delay,
starts the CMSIS one-shot timer, samples the CMSIS kernel tick, and converts it
to milliseconds with the recovered 1,024-Hz expression
`uint32(kernel_tick * 1000) >> 10`.

The binary also preserves a noteworthy sentinel mismatch: the minimum starts
at `0xFFFFFFFF` but restart suppression compares it with `0x7FFFFFFF`. Thus an
empty table requests a `0xFFFFFFFF` timer, while an exact `0x7FFFFFFF` remaining
delay suppresses restart. The clean-room `r1_delayed_event_timer_step` exposes
both outcomes and returns due events and the timer action; it performs no live
queue, mutex, timer, tick, critical-section, or logging operation.

CMSIS-RTOS2, authenticated FreeRTOS critical sections, the adjacent event queue,
and Nordic logging remain independently owned providers. No provider source is
copied into this policy model.

The pure step is retained in the unsigned Nordic SDK image at `0x0003B84C`.
That image contains 127,124 bytes of text, 276 bytes of data, and 150,100 bytes
of BSS; its standalone BIN is 127,400 bytes. The HEX and BIN SHA-256 values are
`b93d632817043161e138e97987d4f595520f87b3849e7126922b4e8d4c1eacbb` and
`4bb7ad7cc81ab6030d027c495327719612ea7a32139ba757c06a6c8d3d2d0c36`.
Since 2026-08-14 the SDK connection-control composition also drives the step
from a CMSIS one-shot timer and fires the due disconnect through Nordic
`sd_ble_gap_disconnect` (see `CONNECTION-CONTROL-CORRELATION.md`); the platform
driver owns the live timer, mutex, and tick, while the portable step remains
pure.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_delayed_event_timer.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
