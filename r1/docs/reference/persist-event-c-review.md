# R1 persistence/export event adapter in C

The naked assembly body at stock entry `0x42bb0` in `native_event_callbacks.c` now uses ordinary C. It ignores both incoming arguments, invokes periodic log persistence, then performs an ordinary EP export poll. The C services now establish that neither call consumes an incoming-register ABI contract. No payload/length gate or forced-flush behavior is introduced.

The log integration passes 924 stock comparisons with actual cache extraction, musl memcpy, export-state access, persistence, initialization and sector writing. The subsequent EP call is modeled in this probe. The EP integration passes another 1,024 comparisons with actual storage initialization, cursor scanning, storage wrappers, ring flushing, sector preparation and export guard; persistence is modeled there. These complementary probes check the adapter against both completed controller paths without claiming one unified physical-hardware test.

Cases include cache wraparound, timing thresholds, flash callback outcomes, lookup/allocation failures, cursor reconstruction and repeated event sequences. Additional cases refill the cache during the modeled delay: without that state change, a duplicate persistence call could be invisible because insufficient cache data remained. The refill cases distinguish the extra consumption and critical-section calls.

Eight compiled defects are rejected: missing persistence, missing poll, reversed order, double persistence, double poll, an added length gate, an added payload gate and forced flush instead of ordinary poll. Both normal probes were rerun sequentially after defect testing. Reconstructed execution is prohibited from entering stock instruction addresses. Provider order/arguments, guarded state, data/flash hashes, preserved registers, stack pointer and interrupt masks are compared; private scratch, caller-clobbered registers and void returns are excluded.

REA returned all 14 instruction bytes and they match the official raw application. See [REA receipt](persist-event-c-rea.json) and [structured verification](persist-event-c-review.json).

All 769 R1 units compile and both payloads compose without duplicate strong symbols. All 768 other objects remain identical. Only this adapter body and its associated relocations change in the shared event object. No state or imports are added: 125 application and 34 bootloader dependencies remain. R1 source coverage passes. Global coverage retains the existing G2 `resident_rom_thumb_set.S` manifest omission.

FAL lookup, heap/mutex allocation, flash callbacks, RTOS services, logging and the opposite controller boundary in each probe remain modeled. Physical flash programming, real queue contention, asynchronous scheduling, complete image linking and device operation remain unverified. Byte identity is not required for this build route.
