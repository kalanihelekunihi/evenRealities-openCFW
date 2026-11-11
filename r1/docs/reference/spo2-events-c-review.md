# R1 oxygen mode and measurement event adapters in C

The naked assembly bodies at stock entries `0x42244` (mode) and `0x423d8` (one-shot measurement) in `native_event_callbacks.c` now use ordinary C. Both preserve the length-1 gate, short-circuit logging-mode reads, original text objects, ring ID `0x0c400000` and SDK ID `0x001c0003`. Mode selection truncates the payload to a byte; measurement enable tests the entire word for zero. Both call the existing C SpO2 services with zero for their unused length parameter.

The combined adapters, one-shot controller, mode transition/setter and lifecycle helpers pass 2,244 stock/C comparisons. Cases cover raw payloads, invalid lengths, individual logging bits and changing mode reads, three stream slots, timer teardown, registration success/failure, provider mutations and mixed wear/tick/measurement/mode sequences. Checks compare provider order and arguments, guarded shared state, preserved registers, stack pointer and interrupt masks. Private scratch, caller-clobbered registers and void returns are excluded.

Sixteen compiled defects are rejected, eight for each adapter: wrong length gate, wrong payload conversion, wrong ring bit or ID, wrong SDK bit or ID and wrong service value, plus raw measurement forwarding or boolean mode conversion as applicable. The normal implementation was rerun afterward.

REA returned the complete instruction spans and they match the official raw application. See [mode evidence](spo2-event-42244-c-rea.json), [measurement evidence](spo2-event-423d8-c-rea.json) and [structured verification](spo2-events-c-review.json).

The normal license-free build compiles all 760 R1 units and composes both payloads without duplicate strong symbols. All 759 other objects are identical. Within the shared event object, only these two adapter bodies and their associated relocations change. No state or imports are added: 128 application and 34 bootloader dependencies remain. R1 source coverage passes; global source coverage still reports the existing G2 `resident_rom_thumb_set.S` manifest omission.

Stream registration/teardown, timers, logging and the timing-start plan are modeled providers. The result callback is checked by identity, not invoked. Physical oxygen sensing, asynchronous delivery, complete image linking and device operation remain unverified. Byte identity is not required for this build route.
