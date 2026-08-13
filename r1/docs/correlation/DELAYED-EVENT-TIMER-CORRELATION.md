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

The pure step is retained in the unsigned Nordic SDK image at `0x00035D2C`.
That image contains 94,804 bytes of text, 236 bytes of data, and 132,544 bytes
of BSS; its standalone BIN is 95,040 bytes. The HEX and BIN SHA-256 values are
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf` and
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_delayed_event_timer.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
