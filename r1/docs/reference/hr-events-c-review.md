# R1 heart-rate mode and measurement event adapters in C

The naked assembly bodies at stock entries `0x421c4` (mode) and `0x42128` (one-shot measurement) in `native_event_callbacks.c` now use ordinary C. They retain the length-1 gate, short-circuit logging-mode reads, original text objects, ring ID `0x0c400000` and SDK ID `0x001c0003`. Mode truncates its payload to a byte, whereas measurement enable tests the entire word for zero. Each calls the existing C service with zero for the unused length argument.

The mode adapter and actual mode-transition/setter/teardown helpers pass 6,534 stock/C comparisons. The measurement adapter and actual one-shot controller/teardown helpers pass another 2,952. Cases cover individual logging bits and changing reads, rejected lengths, high-byte payloads, five HR stream slots, shared HRV timing/session state, timer creation success/failure, registration outcomes, provider mutations and mixed control/teardown sequences. Provider order/arguments, guarded state, preserved registers, stack pointer and interrupt masks match. Private scratch, caller-clobbered registers and void returns are excluded.

Sixteen compiled defects are rejected, eight for each adapter: wrong length gate, wrong payload conversion, wrong ring bit or ID, wrong SDK bit or ID and wrong service value, plus raw enable forwarding or boolean mode conversion as applicable. Both normal probes were rerun after defect testing.

REA returned all instructions in both adapters and the bytes match the official raw application. See [mode evidence](hr-event-421c4-c-rea.json), [measurement evidence](hr-event-42128-c-rea.json) and [structured verification](hr-events-c-review.json).

The license-free build compiles all 760 R1 units and composes both payloads without duplicate strong symbols. All 759 other objects are identical. Only these two adapter bodies and their associated relocations change within the shared event object. No state or imports are added: 128 application and 34 bootloader dependencies remain. R1 source coverage passes. Global coverage still reports the existing G2 `resident_rom_thumb_set.S` manifest omission.

Providers for stream registration/teardown, timers, memory clearing, authorization and logging are modeled. Registered producer/result/timer callbacks are checked by identity rather than asynchronously invoked. Physical HR sensing, IRQ concurrency, complete image linking and device operation remain unverified. Byte identity is not required for this build route.
