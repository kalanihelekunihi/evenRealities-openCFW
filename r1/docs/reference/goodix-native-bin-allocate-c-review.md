# Native Goodix bin allocation core in C

`native_heap_allocate.c` implements the bin-only allocator at `0x982c2`, including its private continuation at `0x3df80`, as one ordinary C function. It accepts a valid native pool and an adjusted block size. It shares the existing native bin-selection, removal and insertion helpers and introduces no state.

The core preserves the own-bin largest-fit check, higher-bin fallback and ordered node search. It unlinks the selected node, splits only when at least 16 bytes remain, updates boundary tags and allocated/previous-used bits, and reinserts any remainder. It returns null when bins cannot satisfy the request. Wilderness allocation, payload clearing and fatal policy belong to the public wrapper and remain separate work.

All 22,272 stock comparisons pass across six allocation profiles, two alignments, optional terminal guards, all 16 initial free masks, 29 adjusted requests and both masks. Metadata write width/order/value and full pool bytes match. A further 1,000 mixed operations contain 501 bin allocation calls and 499 releases; 147 calls fall back to the stock public wrapper. Nine compiled defects are rejected.

The stock body accounts for 246 instruction bytes: 126 head bytes and 120 continuation bytes. Tests execute 244. The two unexecuted bytes at `0x9831c..0x9831d` update the lower search bound, a branch not selected by valid two-bin metadata. Malformed descriptors and bitmaps are outside the test contract.

Source core and release execution are forbidden from entering stock code. Stock initialization/allocation/release prepare fixtures, and explicit stock-wrapper fallback is used in the mixed run. This demonstrates interoperability; it is not a source-only public allocator. Saved integer/FP state, SP, masks, FPSCR and guards are checked. Caller scratch, private frames, APSR, concurrent mutation, physical pool placement, final linking, startup and boot remain unverified.

The normal serial build compiles 866 units with no duplicate strong symbols and unchanged imports (62 application, 22 bootloader). The tested new object equals its normal-build object. All 855 prior nongenerated objects remain identical; two differing generated objects are recorded separately. The manifest adds one unit. Source plan and cache layout remain unchanged.

The [machine-readable receipt](goodix-native-bin-allocate-c-review.json) contains hashes and results. Probes are under `build/goal-r1-goodix-native-bin-allocate-c/`; the normal report is `build/sources-goal-r1-goodix-native-bin-allocate-c/report.json`.
