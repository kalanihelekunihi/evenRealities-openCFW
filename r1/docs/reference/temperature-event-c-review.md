# R1 temperature measurement event adapter in C

The inline assembly at `r1_event_callback_00042514` in `native_event_callbacks.c` is replaced by ordinary C. This stock entry accepts only length 1, converts the entire incoming payload word to a boolean, logs according to the existing short-circuit mode reads and calls the C temperature one-shot service. All original text objects and other event bodies remain in place.

The combined adapter and temperature one-shot controller pass 1,240 stock/C comparisons. Cases cover individual logging bits, changing logging modes, raw nonzero payloads including 256, invalid lengths, registration success/failure, existing handles, provider mutations and repeated enable/disable calls. Provider order/arguments, guarded shared memory, preserved registers, stack pointer and interrupt masks match. Private scratch, caller-clobbered registers and void return values are excluded.

Eight compiled defects are rejected: inverted length gate, byte-truncated boolean conversion, raw payload forwarding, wrong ring bit, wrong ring ID, wrong SDK ID, wrong SDK bit and inverted service value. An initial defect probe showed the combined-bit cases could miss a wrong ring bit; individual-bit cases were added before accepting the verification. The normal implementation was rerun successfully afterward.

REA returned all 86 instruction bytes and they match the official raw application. See [REA receipt](temperature-event-c-rea.json) and [structured verification](temperature-event-c-review.json).

The normal source build compiles all 760 R1 units and composes both payloads without duplicate strong symbols. All 759 other objects are byte-for-byte unchanged. In the shared event object, only this adapter's allocated sections and relocations change. Imports stay at 128 application and 34 bootloader; there is no new state. The R1 source check passes. Global source coverage still reports the existing G2 `resident_rom_thumb_set.S` manifest omission.

The probe models stream registration, teardown, memory clearing and logging. Sample callback identity is checked; physical sensor delivery and asynchronous scheduling remain unverified. This is relocatable composition, not proof of a complete firmware image or device operation. Byte identity is not required for this implementation route.
