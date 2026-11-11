# R1 stress mode and enable event adapters in C

The two naked assembly bodies in `native_event_callbacks.c` at stock entries `0x422c8` (mode) and `0x42474` (measurement enable) are now ordinary C. Both retain the length-1 gate, short-circuit logging-mode reads, exact text objects, ring ID `0x0c400000` and SDK ID `0x001c0003`. The mode event truncates its payload to a byte; the enable event converts the full payload word to a boolean. They call the existing C stress services, whose unused length parameter is passed as zero. No public dependency on the unused incoming register value is introduced.

The combined C adapters and stress controller pass 2,772 stock/C comparisons. These cover direct services, both adapters, modes and raw payloads including 128, 255, 256 and 257, rejected lengths, individual logging bits and changing logging modes, timer creation success/failure, existing timers, authorization return values, provider mutations and mixed enable/mode/timer sequences. Checks compare provider order/arguments, guarded state, public direct authorization return, preserved registers, stack pointer and interrupt masks. Private scratch, caller-clobbered registers and void adapter returns are excluded.

Sixteen compiled defects are rejected, eight for each adapter: wrong length gate, wrong payload conversion, wrong ring bit or ID, wrong SDK bit or ID, and wrong service value, plus raw enable forwarding or boolean mode conversion as applicable. The normal implementation was rerun afterward.

REA returned the complete instruction spans of both adapters, verified against the raw official application. See [mode evidence](stress-event-422c8-c-rea.json), [enable evidence](stress-event-42474-c-rea.json) and [structured verification](stress-events-c-review.json).

The normal license-free source build compiles all 760 R1 units and composes both payloads without duplicate strong symbols. All 759 other objects remain identical. In the shared event object, only these two adapter bodies and their associated relocations change. There is no new state or import: 128 application and 34 bootloader dependencies remain. R1 source coverage passes. The global source check still reports the existing G2 `resident_rom_thumb_set.S` manifest omission.

Authorization, timer services and logs are modeled boundaries. Timer callback identity and direct execution are checked, but asynchronous scheduling and physical sensing are not. Relocatable composition does not prove complete image linking or device operation. Byte identity is not required for this build route.
