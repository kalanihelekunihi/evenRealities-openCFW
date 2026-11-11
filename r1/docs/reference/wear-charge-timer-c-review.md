# R1 wear/charge timer callback in C

`native_wear_charge_timer.c` implements stock callback `0x4c3d0` using the existing wear/charge status byte, timer word and health-mode byte. No new state is introduced. The setter now registers this C callback.

Each invocation reads the native charger state and logs the result with the original short-circuit mode reads, strings and IDs. Only charge state zero with stored wear/charge status exactly 1 continues. It publishes the current nonzero health state on topic 4, reads the battery level independently for the phone report and glasses tag, sets battery task flag 4096, releases a nonzero timer before clearing its cell, then clears the stored status last. Provider calls can mutate shared state, so state reads and clear ordering remain explicit.

The callback, existing C setter and actual event adapter pass 7,864 stock/C comparisons. They cover all relevant status bytes, raw requests, charge/health values, rejected event lengths, timer presence, creation success/failure, individual and changing logging modes, provider mutations and mixed setter/adapter/callback sequences. Provider order/arguments, the two distinct level reads, copied event bytes, guarded shared state, preserved registers, stack pointer and interrupt masks match. Private scratch, caller-clobbered registers and void returns are excluded.

Eight compiled defects are rejected: wrong charge gate, wrong status gate, early status clearing, cached level read, wrong battery-report state, wrong task flags, early timer clearing and missing final status clear. The normal implementation was rerun afterward.

REA returned all 152 instruction bytes and they match the official raw application. See [REA receipt](wear-charge-timer-c-rea.json), [structured verification](wear-charge-timer-c-review.json) and [existing state initialization proof](wear-charge-initialization.json).

All 762 R1 units compile and both payloads compose without duplicate strong symbols. All 761 prior objects are identical. Application imports decrease from 128 to 127 with no new imports; bootloader imports remain 34. The R1 source check passes. Global source coverage still reports the existing G2 `resident_rom_thumb_set.S` manifest omission.

Charger-state and battery-level reads, battery-report/tag transport, task flags, wear-probe operations, timer services, event transport and logs are modeled boundaries. The nonzero-state helper, setter, callback and event adapter execute their actual C bodies. No physical charging/sensing, asynchronous scheduling, complete firmware linking or device operation is established. Byte identity is not required for this build route.
