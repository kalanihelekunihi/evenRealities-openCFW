# R1 EP RAM-ring flush and sector preparation in C

`native_ep_ring_flush.c` implements stock flush `0x3ec78` and conditional sector preparation `0x3ed0c`. It shares the existing status-ring read/write indices and sixteen eight-byte records through `native_status_ring.h`. The existing owner translation unit now includes that header; its compiled object remains identical.

Each iteration enters a critical section. An empty ring exits the section and returns. Otherwise it copies the packed record and timestamp, advances the read index modulo 16, and exits the critical section before storage work. It then reloads the flash cursor, derives its sector and 512-record position, prepares the sector at position zero and writes eight bytes. Success advances the cursor modulo 1024 and prepares the other sector after position 511. A failed write does not restore the popped record or advance the cursor. Provider-side changes to the cursor are retained on failure and overwritten by the cached cursor increment on success, as in stock.

Sector preparation initializes a one-byte marker to `0xff`, reads the sector's first byte, and erases only when the read result is nonzero and the marker is not `0xff`. Read/write/erase operations remain explicit storage providers rather than assumed flash-port behavior.

The new cursor halfword at `0x2000693e` starts at zero, authenticated by actual stock startup execution, independent RW decoding and compiled-object comparison. It occupies the gap immediately after the existing dropped-count halfword and before the export semaphore handle; no existing owner is enlarged. See [initialization evidence](ep-flush-initialization.json).

The two C functions, existing C export guard/poll/force paths and actual persistence-then-poll event adapter pass 3,808 stock/C comparisons. Cases cover empty and full usable ring depth, index wraparound, cursor sector boundaries and high halfword values, read/write outcomes, marker values, provider mutations, timeout paths and repeated guard sequences. Checks compare provider order/arguments, all eight record bytes, guarded shared state/record memory, preserved registers, stack pointer and interrupt masks. Reconstructed execution may not enter stock instruction addresses. Private scratch, caller-clobbered registers and void returns are excluded; ring input indices remain within their native valid 0–15 range.

Eight compiled defects are rejected: wrong pop-index wrap, swapped record words, wrong cursor wrap, wrong sector boundary, advancing on failure, wrong next sector, wrong marker seed and inverted marker gate. The normal implementation was rerun afterward.

REA returned both complete instruction spans and they match the official raw application. See [flush evidence](ep-flush-c-rea.json), [sector evidence](ep-sector-prepare-c-rea.json) and [structured verification](ep-flush-c-review.json).

All 767 R1 units compile and both payloads compose without duplicate strong symbols. All 766 prior object hashes are identical. Application imports change from 127 to 129: the ring-flush import closes and `r1_ep_record_read`, `r1_ep_record_write`, and `r1_ep_sector_erase` become explicit. Bootloader imports remain 34. R1 source coverage passes. Global coverage retains the existing G2 `resident_rom_thumb_set.S` manifest omission.

Storage operations, critical sections, plan initialization, queue/semaphore operations, clock, persistence and logs are modeled boundaries. No physical storage writes, real semaphore contention, asynchronous IRQ/concurrency, complete firmware linking or device operation is established. Byte identity is not required for this implementation route.
