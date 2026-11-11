# Motion IRQ cache lookup uses ordinary C

`r1_motion_interrupt_input_lookup` now accesses the existing volatile IRQ cache directly after calling the bus binder. Fixed-R4 variables, empty assembly and artificial context-base arithmetic are removed. The complete `native_peripheral_bindings.c` unit now uses ordinary C without register constraints or inline assembly. No new cache owner or surrounding context allocation is introduced.

The [receipt](motion-cache-pure-c-review.json) records 1,296 stock/C sequences with three invocations each: 3,888 paired calls. Both bus-only and IRQ-through-bus paths cover empty/warm caches, NULL/non-NULL registry returns, raw handle values, repeated misses, incoming register seeds and callbacks that change either cache. Registry-call order, returned handles, ordered four-byte cache writes, final cache/context bytes, stack balance, saved registers and masks agree. Three controls with skipped bus binding, a stale IRQ read before bus binding or an omitted cache store are rejected.

The IRQ byte range remains owned by the existing four-byte cell at `0x200076b0`; bus storage remains `0x200076b4`. A bus callback can fill the IRQ cache, and the subsequent live read must observe it. A registry callback's write to the cache it is resolving is still overwritten by that call's returned handle, matching stock.

REA raw-byte observations identify entries `0x50128` and `0x50150`. Replay uses code/write hooks without memory-read hooks. The registry provider is modeled. Private frame layout, active provider saved-register contents and caller-clobbered registers are excluded from this C status/handle API proof. Physical motion IRQ/bus operation, arbitrary aliases/faults and concurrency remain unverified.

The normal report is `build/sources-goal-r1-motion-cache-pure-c/report.json`: 727 compiled units, no failures or duplicate strong symbols, 178 application imports and 34 bootloader imports. Only the peripheral-binding object changed; 726 objects are unchanged. Bus-only, LED/LDO, PPG and touch binding instruction sections are byte unchanged. Both source manifests pass `make sources-check`.
