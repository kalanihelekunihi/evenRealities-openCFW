# Goodix algorithm configuration and memory front end in C

`native_algorithm_config.c` implements three stock entries: configuration setup at `0x29f58` (38 instruction bytes), memory-size setup at `0x2a090` (32), and memory initialization at `0x2a0b4` (38). The latter two are distinct entries; the older 70-byte account combined them.

Configuration setup optionally publishes the frame-table pointer, configures 0x7540 memory bytes, and loads one of four register lists for a byte index below four. Register loading proceeds even if memory setup fails. Memory-size setup rejects zero before deinitializing; otherwise it deinitializes all function bits, stores the full requested size, and initializes. Initialization bypasses any nonzero status byte. For zero status it reads size before publishing the static pool pointer, rejects zero size or a nonzero allocator result, and writes status 1 only on success.

The new unit owns the active frame pointer, a 12-byte memory state, a 30,016-byte pool, and four typed register lists containing 48, 1, 1 and 1 address/value pairs. Their arrays and descriptors match all 238 native bytes, including alignment, under native probe placement. Future lifecycle entries must share these owners.

All 108 native instruction bytes execute across 41,216 direct comparisons. Another 36,864 comparisons execute the existing initialization hook and actual reset getter, with the loader modeled. A further 36,864 execute those entries and the register-list loader; its extracted C section has bytes and relocations identical to the normal-build section. These checks model the deinitializer, allocator and final virtual-register writer. Nine compiled defects are rejected. Shared-state access widths, order and values match, including callback mutations; saved integer/FP state, SP, masks, FPSCR, reserved bytes and guards are checked.

The full serial build compiles all 863 units with no duplicate strong symbols. All 852 prior nongenerated objects remain identical, and the tested new object equals its normal-build object. Two existing generated objects differ between build directories and are recorded separately. The manifest adds one unit; the source plan and cache layout are unchanged.

The application still has 63 imports, but the set changed: `GH3X2X_AlgoCallConfigInit` is now implemented and `goodix_mem_init` is exposed instead. The bootloader retains 22 imports. The existing portable heap API is not treated as a verified native allocator ABI.

Native addresses are probe placement only. Caller scratch, void returns, private frames, APSR and non-byte indices are excluded. Arbitrary requested sizes are forwarded in modeled tests; physical allocator writes, pool capacity/placement, deinitializer behavior, virtual register application, sensor operation, concurrency, final application linking, startup and boot remain unverified.

The [machine-readable receipt](goodix-algorithm-config-c-review.json) contains hashes and results. Probe scripts/logs are under `build/goal-r1-goodix-algo-config-c/`; the normal report is `build/sources-goal-r1-goodix-algo-config-c/report.json`.
