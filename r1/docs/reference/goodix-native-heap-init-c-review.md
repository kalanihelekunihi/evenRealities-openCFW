# Native Goodix pool initialization ABI in C

`native_heap_init.c` provides `goodix_mem_init` at stock entry `0x6dfd6` and the separate descriptor initializer at `0x2d4f4`. Their 46 and 78 instruction bytes were previously combined under a portable heap symbol hint. The firmware frontier now selects the native provider. The portable heap utilities keep their separate APIs and unchanged implementation.

The wrapper rejects null pointers and nonpositive signed sizes before clearing. Positive-size input is cleared before descriptor validation, including positive invalid sizes. The descriptor accepts sizes from 1,024 through 0x40000000 inclusive, publishes the canonical pool cell, writes bin anchors, and records top, end, available size and the encoded initial block size. Top alignment depends on the actual address: `(base + 51) & ~7`. These rules differ from the portable model's size policy and relative-offset representation.

All 124 native instruction bytes execute in 3,520 checks with fill modeled and 560 checks with the actual C fill body. The C fill body and relocations match the normal-build function. Descriptor writes match in width, order and value; independent range and layout checks, full observed pool bytes, reserved bytes, guards, saved integer/FP state, SP, masks and FPSCR are checked. Nine compiled defects are rejected.

A further 288 comparisons execute the existing initialization hook, reset getter, algorithm configuration/memory entries, new native initializer, C fill and register-list loader. Full 30,016-byte pool contents and shared state match. The deinitializer and final virtual-register writer remain modeled. The loader body has the normal-build bytes and relocations verified in the preceding configuration review.

The normal serial build compiles 864 units with no duplicate strong symbols. Application imports fall from 63 to 62 with `goodix_mem_init` resolved and no new imports; the bootloader retains 22. The tested object equals the normal-build object. All 853 prior nongenerated objects remain identical; two differing generated objects are recorded separately. The manifest adds one unit and one four-byte canonical active-pool cell. The existing algorithm pool is reused. Source plan and cache layout are unchanged.

Only four-byte-aligned pool addresses are tested. Large clear requests are modeled with a bounded observed arena; actual-fill tests use mapped pool sizes. SRAM fill transaction widths, caller scratch, private frames and APSR are excluded. Out-of-arena clearing, memory faults, interrupts, allocation/release/exhaustion behavior, physical sensors, final linking, startup/scatter integration and boot remain unverified.

The [machine-readable receipt](goodix-native-heap-init-c-review.json) contains hashes and results. Probes are under `build/goal-r1-goodix-native-heap-init-c/`; the normal report is `build/sources-goal-r1-goodix-native-heap-init-c/report.json`.
