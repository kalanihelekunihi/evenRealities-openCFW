# R1 sleep low-power handler in C

Stock event handler 0x4a5bc now uses C, exported as r1_algo_sleep_low_power and its existing registered service alias. Decoded code ends at 0x4a652, establishing 150 bytes rather than the previous zero-size inventory entry.

The handler always logs the low-power event, then checks the canonical sleep-active byte for exactly one. When active, it logs the live status, clears the byte before temperature status zero and algorithm force-wake, then publishes topic 12 with a pointer to that same byte. It does not create or release a timer. Payload and length are ignored, matching stock.

Stock/C replay passes 1,576 direct, actual event-adapter and shared report/getter/default-mode/force-wake sequences. Tests cover all 256 active-state bytes, dynamic logging, provider mutation at successive calls, reserved/timer preservation and mutations through the published state pointer. Eight compiled defects are rejected. Checks compare provider order/arguments, live published byte, call-time state snapshots, full guarded shared state, public getter returns, preserved registers, SP and masks.

All 756 R1 units compile without failures or duplicate strong symbols. All 755 prior objects retain their hashes. The event-service import closes without new imports, leaving 133 application and 34 bootloader imports. No state owner or assembly was added. The R1 source check passes; the global check still flags the existing G2 resident_rom_thumb_set.S manifest gap, which remains untouched.

Temperature reporting, algorithm force-wake internals, event/multicast delivery, vivo probing, logging and timer services are modeled where reached by the mixed paths. No asynchronous IRQ/concurrency, physical low-power transition, complete firmware linkage or device operation is established. Private report payload addresses are normalized by contents; caller-clobbered registers and private stack are excluded.

See [machine-readable evidence](sleep-low-power-c-review.json) and [REA cleanup/publication receipt](sleep-low-power-c-rea.json).
