# Native Goodix resize ABI in C

`native_heap_reallocate.c` implements stock entry `0x2d5c0` using the existing C native allocator and release path. It is a private firmware API, not a replacement for libc `realloc` or the portable heap model. It introduces no state.

Null input delegates to public allocation and its minimum payload rule. Existing input with a null pool or failed range check returns null quietly. Existing blocks use the native unclamped rounding calculation: zero size can shrink a block to an eight-byte header-only allocation. Shrink preserves the old low flag bits, splits only when at least 16 bytes remain, and releases the tail. Growth allocates a replacement, reloads the old header, copies the full old payload capacity including padding, and releases the old allocation afterward.

All 152 native instruction bytes execute across 20,928 comparisons, including 3,072 terminal growth failures. Another 36 pointer/null-pool cases pass. Seeded nonzero payload capacities check the copy boundary and padding. A further 1,000 C-only allocator operations contain 295 resizes, with no stock-code fallback on the source side. Pool images and metadata/copy write width, order and value match. Ten compiled defects are rejected.

Returning paths check saved integer/FP state, SP, masks, FPSCR and guards. Failure paths inherit the preserved non-returning allocation policy; status/log/watchdog/RTOS/delay ports are modeled and observation stops after three delays. Terminal checks exclude private frame depth and active private register assignments. The mixed sequence resizes to at least eight bytes; zero-size behavior is checked in isolated comparisons.

Malformed headers, arbitrary interior pointers, near-wrap huge physical copies, concurrency, real manager reset, physical memory, final linking/startup and boot remain unverified. Caller scratch, private frames and APSR are excluded. Native deinitialization and the complete algorithm lifecycle remain separate work.

The normal serial build compiles all 868 units with no duplicate strong symbols and unchanged imports (62 application, 22 bootloader). The tested object equals its normal-build object. All 857 prior nongenerated objects remain identical; two differing generated objects are recorded separately. The manifest adds one unit. Source plan and cache layout remain unchanged.

The [machine-readable receipt](goodix-native-reallocate-c-review.json) contains hashes and results. Probes are under `build/goal-r1-goodix-native-reallocate-c/`; the normal report is `build/sources-goal-r1-goodix-native-reallocate-c/report.json`.
