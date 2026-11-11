# R1 flash-log initialization in C

`native_log_bin_initialize.c` implements stock entry `0x590ac` using the existing writer owners, sector-count accessor and pinned FAL finder symbols. It looks up `log.bin`, stores its partition, then locates the flash device using the name at partition offset 28. A missing partition returns after logging. A missing device logs and clears the partition pointer afterward. Other state, including the initialized flag, is not reset on failure.

With both descriptors present, initialization resets sector and offset, obtains the byte-truncated sector count, and scans the word at offset 4 in each sector. The first `0xffffffff` marker selects that sector with offset zero. An empty scan or fully occupied ring retains sector zero. The marker scratch word is initialized once and retained between reads, including reads that do not overwrite it. Sector diagnostics run regardless of log mode, and the initialized byte is set only after the final diagnostic call.

The actual C initializer, writer and sector-count accessor pass 2,992 stock/C comparisons. Cases cover lookup failures, existing state, empty/occupied/erased rings, sector count truncation, per-read marker retention, provider failures, provider-side descriptor/state changes, lazy initialization during writes, write/erase bounds and repeated writer operations. Checks compare provider order/arguments, flash data hashes, guarded shared state, marker scratch initialization, sector-count return, preserved registers, stack pointer and interrupt masks. Initializer/writer incidental return values, caller-clobbered registers and private scratch are excluded.

Eight compiled defects are rejected: wrong partition name, wrong device-name offset, missing failure-path partition clearing, wrong initial offset, inverted erased-marker gate, wrong selected sector, missing initialized flag and resetting marker scratch between reads. The full normal probe was rerun afterward.

REA returned all 258 instruction bytes, verified against the official raw application. See [REA evidence](log-init-c-rea.json), [structured verification](log-init-c-review.json) and [existing owner initialization proof](log-writer-initialization.json).

All 765 R1 units compile and both payloads compose without duplicate strong symbols. All 764 prior objects remain identical. Application imports decrease from 127 to 126 without new imports; bootloader imports remain 34. No state owners are added. R1 source coverage passes. Global coverage still reports the existing G2 `resident_rom_thumb_set.S` manifest omission.

FAL finder operations, logging and indirect flash callbacks are modeled boundaries. The existing C writer and count accessor execute directly. Physical flash reads/writes, actual FAL lookup execution, concurrency, complete firmware linking and device operation remain unverified. Zero-divisor UDIV coverage retains the prior default DIV_0_TRP-clear scope. Byte identity is not required for this build route.
