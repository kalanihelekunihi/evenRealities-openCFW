# R1 temperature mode event adapter in C

The naked assembly body at stock entry `0x42350` in `native_event_callbacks.c` now uses ordinary C. It preserves the length-1 gate, payload byte truncation, short-circuit logging-mode reads, original text objects, ring ID `0x0c400000` and SDK ID `0x001c0003`, then calls the existing C temperature mode setter.

The adapter and existing temperature mode/transition/timer helpers pass 4,152 stock/C comparisons. Cases cover all logging flag combinations, changing logging modes, raw payloads including 128, 255, 256 and 257, rejected lengths, existing stream handles and timers, timer creation outcomes, health gating and provider mutations. Checks compare provider order/arguments, provider-boundary and guarded final state, preserved registers, stack pointer and interrupt masks. Private scratch, caller-clobbered registers, APSR and void returns are excluded.

Eight compiled adapter defects are rejected: inverted length gate, missing byte truncation, boolean mode conversion, wrong ring bit or ID, wrong SDK bit or ID and wrong service value. Defect probes select the adapter cases; the normal implementation is rerun across the full case set afterward.

REA returned all 80 instruction bytes, verified against the official raw application. See [REA evidence](temperature-mode-event-c-rea.json) and [structured verification](temperature-mode-event-c-review.json).

All 760 R1 units compile and both payloads compose without duplicate strong symbols. All 759 other objects remain identical. Within the shared event object, only this adapter body and its associated relocations change. No state or imports are added: 128 application and 34 bootloader dependencies remain. The R1 source check passes. Global coverage still reports the existing G2 `resident_rom_thumb_set.S` manifest omission.

Logging, streams, timer services, health mode and memory clearing are modeled providers. Callback identity is checked; physical sensing, asynchronous timers, complete image linking and device operation remain unverified. Native unchecked old-mode indexing is retained over the mapped test addresses. Byte identity is not required for this build route.
