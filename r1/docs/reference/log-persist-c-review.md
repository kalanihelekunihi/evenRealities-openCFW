# R1 periodic flash-log controller in C

`native_log_persist.c` implements stock entry `0x914a0` and its event-service alias. The existing event adapter at `0x42bb0` calls this controller and then its separate export-guard service; the probe executes that actual adapter.

An active log export suppresses persistence. Otherwise stock extracts 4096 cache bytes with peek zero before testing elapsed time. A failed extraction stops the path. A successful extraction obtains the kernel tick and requires `now > last_tick + 10000`, using unsigned 32-bit addition and comparison, including wraparound. It stores the new tick before the flash writer, then delays 80 ticks regardless of writer status. These ordering and boundary semantics are retained explicitly rather than changing to subtraction-based elapsed time.

The new last-tick word at `0x200068f0` and 4096-byte snapshot at `0x20018bc8` both start at zero. Actual execution of stock RW decompression and ZI initialization, an independent RW decoder and compiled-object comparison confirm their initial contents. See [startup proof](log-persist-initialization.json). The flash-file writer at `0x59670` remains the explicit unresolved `r1_log_bin_write` provider.

The controller and actual event adapter pass 1,998 stock/C comparisons. Cases cover export gating, cache return values, full/partial/no snapshot writes, thresholds on both sides of equality, counter wraparound, writer failures, provider mutations and repeated direct/adapter sequences. Provider order/arguments, consumed snapshot bytes, guarded shared state, preserved registers, stack pointer and interrupt masks match. Private scratch, caller-clobbered registers and void returns are excluded.

Eight compiled defects are rejected: wrong export gate, wrong peek mode, wrong extraction size, lost strict threshold, wrong interval, missing tick store, writer-failure short circuit and wrong delay. The normal implementation was rerun afterward.

REA returned all 66 instruction bytes, verified against the official raw application. See [REA evidence](log-persist-c-rea.json) and [structured verification](log-persist-c-review.json).

All 763 R1 units compile and both payloads compose without duplicate strong symbols. All 762 prior objects remain identical. Application imports remain 127: the periodic event service closes and the flash writer becomes explicit. Bootloader imports remain 34. R1 source coverage passes. The global check retains the existing G2 `resident_rom_thumb_set.S` manifest omission.

Cache extraction, clock, flash writer, delay and the adapter's subsequent export-guard service are modeled boundaries. No physical flash mutation, RTOS scheduling, complete firmware linking or device operation is established. Byte identity is not required for this build route.
