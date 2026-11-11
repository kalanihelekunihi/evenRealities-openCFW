# Native Goodix release, free-space query and bin helpers in C

`native_heap_free.c` implements the native release API, free-space query, control getter and three bin helpers. It shares the canonical pool cell from the initializer. No new persistent state is introduced. These providers supersede portable API symbol hints; the portable heap implementation remains unchanged.

Release preserves null/control/range/allocated-bit gates, top-block coalescing, merging with adjacent free blocks, circular bin metadata and boundary tags. Bin insertion compares encoded headers in stock order. Bin selection returns zero only for sizes 8 through 1,032 inclusive. The free-space query preserves the stock unsigned calculation rather than substituting a portable-model capacity calculation.

The stock release body has 118 bytes at `0x2d460` and a 176-byte private continuation at `0x37480`. Public thunks share a single C implementation with their bodies. Across wrappers and helpers, 484 instruction bytes are accounted for and 480 execute. The four unexecuted bytes at `0x93e26..0x93e29` increment a bin index on a path made unreachable by the preceding size guard.

Checks pass for 4,613 release transitions, 2,054 bin inputs and 500 mixed operations containing 251 C releases. Release scenarios cover all four-block free orders across six allocation profiles, two alignments, terminal guards, both masks and explicit invalid pointers. The mixed run allocates using stock code after C releases, checking compatibility of the resulting metadata. Write width/order/value, complete pool images, query results, saved integer/FP state, SP, masks, FPSCR and guards match. Nine compiled defects are rejected.

Stock initialization/allocation prepare fixture data and test interoperability. The C release phase is forbidden from executing stock code. This establishes no source-only allocation, reallocation, exhaustion or complete algorithm-teardown implementation. Bin helpers assume valid descriptors and bin indices zero or one. Caller scratch, void returns, private frames, APSR, concurrent mutation, malformed lists and physical memory behavior are excluded.

The normal serial build compiles all 865 units with no duplicate strong symbols. Imports remain unchanged at 62 application and 22 bootloader symbols. The tested object equals its normal-build object; all 854 prior nongenerated objects remain identical. Two differing generated objects are recorded separately. The manifest adds one unit, and the source plan/cache layout remain unchanged. Final linking, startup/scatter integration, physical sensors and boot remain unverified.

The [machine-readable receipt](goodix-native-heap-free-c-review.json) records hashes, code ranges and results. Probes are under `build/goal-r1-goodix-native-heap-free-c/`; the normal report is `build/sources-goal-r1-goodix-native-heap-free-c/report.json`.
