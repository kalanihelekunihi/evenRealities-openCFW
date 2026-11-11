# R1 explicit activity refresh in C

Stock event handler 0x49068 now has C source, exported as r1_activity_explicit_refresh_accumulator and the existing registration symbol r1_event_service_00049068 at the same address. It reuses the canonical 24-byte activity accumulator state with no new allocation.

Unlike the periodic sample path, explicit refresh uses the latest cached counters and publishes immediately in health mode two. It neither tests nor changes the periodic sent flag, and has no offset-595 gate. The day provider still runs, even though its result is unused. The event packs three 16-bit deltas, offset within the 600-second bucket and timestamp into 12 bytes on topic 11. After publishing it reloads the cached counters before rebasing.

Activity mode one or health mode zero rebases immediately. The non-two health mode retains the existing pause/greater-than-900-second rule. Counter rollback rebases and logs; padding and the periodic sent flag remain intact.

The stock/C replay passes 822 direct/repeated and 72 mixed periodic/explicit sequences. It covers mode combinations, timeout equality, wrapped timestamps, rollback/equal counters, provider mutation, shared-state aliases and logging order. Eight compiled behavioral defects are rejected. Checks compare event payloads, call order and call-time state snapshots, guarded state/input buffers, preserved registers, SP and masks.

All 749 R1 units compile with no failures or duplicate strong symbols. All 748 prior objects retain their hashes. Relocatable composition has 137 application and 34 bootloader imports; the registered activity event import closes with no new imports. The R1 manifest check passes. The global source check currently flags a concurrent G2 resident_rom_thumb_set.S manifest gap; that work was preserved.

Clock, mode, logging and event providers are modeled; tests use synchronous mapped SRAM and normalized private event payload addresses. Asynchronous operation, physical accelerometer input, persistence/delivery and complete firmware linkage remain unproved. The separate app-timer counter backend remains unresolved because clock-route and unit evidence is insufficient.

See [machine-readable evidence](activity-explicit-c-review.json) and [REA event packing confirmation](activity-explicit-c-rea.json).
