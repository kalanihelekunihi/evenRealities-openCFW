# R1 flash-log sector-ring writer in C

`native_log_bin_write.c` implements stock writer `0x59670` and sector-count accessor `0x5908c`. `native_log_bin.h` describes the observed partition base/length and flash read/write/erase callback offsets, with compile-time layout checks. The periodic controller's declaration is corrected to the writer's void contract; its generated object remains identical.

The writer initializes lazily, checks both partition and flash pointers, rejects null/empty or oversized input, rotates sectors when offset plus length exceeds 4096, and checks partition bounds before erase/write operations. It reads the marker at sector offset 4 to avoid redundant erases, writes the payload, advances the offset using its value after the callback, then checks and conditionally erases the next sector. Stock's diagnostic logging and callback ordering are preserved, including unconditional SDK erase/write messages. Flash callback return values do not gate the native state updates.

Sector count is the low byte of partition length shifted right by 12. Sector advance preserves the stock division/remainder and byte-truncation behavior. The zero-count case is compared under native default DIV_0_TRP-clear execution; no changed trap configuration is claimed.

Narrow RW owners cover initialized byte `0x20006904`, sector byte `0x20006907`, partition pointer `0x2000690c`, flash pointer `0x20006910` and offset word `0x20006914`. They exclude the existing export byte at `0x20006906` and do not claim intervening bytes. Stock startup execution and independent RW decoding confirm zero initial values; the compiled object agrees. See [initialization proof](log-writer-initialization.json).

The writer and accessor pass 1,972 stock/C comparisons, including missing descriptors, lazy initialization, null/empty/oversized data, exact sector boundaries, byte-truncated counts, zero counts, arithmetic wraparound, marker patterns, callback failures, changing log flags, provider-side state/descriptor changes and repeated writes. Checks compare provider order/arguments, write-data hashes, marker scratch initialization, guarded state, the sector-count return, preserved registers, stack pointer and interrupt masks. The writer's incidental R0, caller-clobbered registers and private scratch are excluded.

Eight compiled defects are rejected: wrong rotation boundary, wrong sector advance, missing rotation offset reset, wrong maximum length, inverted pre-erase marker gate, missing write offset advance, lost write bound and inverted next-marker gate. The normal implementation was rerun afterward.

REA returned the complete instruction spans of the writer and accessor; both match the official raw application. See [writer evidence](log-writer-c-rea.json), [accessor evidence](log-sector-count-c-rea.json) and [structured verification](log-writer-c-review.json).

All 764 R1 units compile and both payloads compose without duplicate strong symbols. All 763 prior object hashes remain identical. Application imports remain 127: `r1_log_bin_write` closes and `r1_log_bin_initialize` becomes explicit. Bootloader imports remain 34. R1 source coverage passes. The global check retains the existing G2 `resident_rom_thumb_set.S` manifest omission.

Initialization, logging and indirect flash callbacks are modeled boundaries. No physical flash erase/write, initialization-body execution, concurrency, complete firmware linking or device operation is established. Byte identity is not required for this build route.
