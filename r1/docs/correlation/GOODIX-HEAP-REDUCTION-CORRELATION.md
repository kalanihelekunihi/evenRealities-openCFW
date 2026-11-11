# Goodix heap reduction correlation

Status: owner-authorized clean-room reconstruction, 2026-08-14. This is not Goodix source.

The locked application reference has SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`. The historical portable Goodix `goodix_mem` / `GdMem` model compiles from transparent C in
`r1/src/vendor/goodix_heap/`; native ABI admission is described separately below. The
restrictively licensed binary remains evidence only.

## Native firmware initialization ABI — 2026-10-28

The [native initializer review](../reference/goodix-native-heap-init-c-review.md) supersedes the portable `goodix_heap_initialize` symbol hint for stock entry `0x6dfd6`. The firmware now uses `goodix_mem_init` plus the separate descriptor initializer at `0x2d4f4`, backed by the existing C byte-fill helper. The table splits the earlier combined 124-byte account into 46 and 78 instruction bytes.

The native descriptor accepts sizes 1024 through 0x40000000 inclusive. The public wrapper rejects null and nonpositive signed sizes before filling, but clears positive-size input before descriptor range validation. It uses absolute 32-bit pool words and alignment based on the actual pool address. These differ from the preserved portable heap API's checked relative-offset representation and minimum-size policy. The remaining table rows are historical portable-model correlations, not blanket admission of native allocation APIs. Future firmware allocation entries must share the canonical `r1_goodix_native_heap_pool` cell. Deinitialization and device behavior remain separate work.

## Native release and free-space query — 2026-10-28

The [native release review](../reference/goodix-native-heap-free-c-review.md) admits firmware `goodix_mem_free`, `goodix_mem_get_free_size`, the global control getter, and native bin selection/removal/insertion. These use the existing canonical pool cell and absolute descriptor words. They replace the old portable symbol hints for those entries; portable utilities remain separate APIs. The free routine includes the private continuation at0x37480. The query's public thunk and30-byte body are now listed separately.

Strict write-order and complete-pool comparisons cover stock-prepared allocations, every four-block release order and mixed stock allocation/C release. Native allocation is fixture preparation/interoperability evidence; it is not a source-only allocation provider. Native bin selection returns0 only for sizes8..1032 inclusive. The four-byte increment path in its original loop cannot execute after its preceding size guard. Native deinitialization, final linking and physical operation remain open.

## Native bin allocation core — 2026-10-28

The [native bin allocation review](../reference/goodix-native-bin-allocate-c-review.md) admits the adjusted-block allocator at0x982c2 and its private continuation at0x3df80 as one C function. It shares the verified native bin helpers and pool descriptor. The public-wrapper review below subsequently recovers the wilderness path, payload clearing and exhaustion policy; the portable allocator is not used as a native ABI alias.

Stock-prepared bins cover both classes, empty/missing classes, higher-class fallback, ordered fit and split remainders around16 bytes. Full pool images and write order/width/value match across22,272 comparisons and1,000 mixed operations. Mixed tests still use the stock wrapper when bin allocation returns no block. This is interoperability evidence, not a source-only public malloc implementation.

## Native public allocation and exhaustion policy — 2026-10-28

The [public allocation review](../reference/goodix-native-malloc-c-review.md) admits `goodix_mem_malloc`, including minimum8-byte payload, four-byte rounding, wilderness allocation and payload clearing. It also recovers the real non-returning exhaustion path: free-space query, status publication, typed log, live sensor-watchdog feed, manager event0x200 and repeated osDelay(1000). Manager signaling uses the existing lifecycle thread slot through an admitted C bridge. No replacement trap or null-return policy is used.

The source test side executes only C initialization/allocation/release providers, with no stock allocation fallback. Stock is the separate reference side. Exhaustion tests observe three delay calls with external status/log/watchdog/RTOS ports modeled. The manager reset itself, scheduler behavior, physical memory and boot remain unverified. The resize review below subsequently recovers reallocation; deinitialization remains separate native ABI work.

## Native resize ABI — 2026-10-28

The [native reallocation review](../reference/goodix-native-reallocate-c-review.md) admits entry0x2d5c0 in ordinary C. It uses the canonical native allocation/release providers and supersedes the portable reallocation symbol hint. Null input delegates to malloc; an existing allocation with zero requested size follows the unclamped shrink calculation rather than libc semantics. Growth copies the full old block payload capacity, including padding, then releases the old block. Shrink splits only when at least16 bytes remain and releases the tail through the same native free path.

All152 native instruction bytes execute across20,928 comparisons, including3,072 terminal growth cases. Another36 boundary cases and1,000 C-only lifecycle operations (295 resizes) pass. Deinitialization, complete algorithm lifecycle reconstruction, final linking and physical boot remain separate work.

## Native HRV context teardown — 2026-10-28

The [HRV teardown review](../reference/goodix-native-hrv-teardown-c-review.md) recovers the concrete allocator consumer at0x6dad0/0x6db58 and its status adapter0x2cac6. Eleven nullable pointer cells are released then cleared, two further buffers are released, then the live context itself is released and its owner cleared. Every step reloads the native context owner. One canonical four-byte HRV cell is added for future initialization to share.

Direct comparisons cover all field masks, live owner changes, clear-after-release timing and late-null abort status. Actual C heap integration covers contexts before/after child allocations and an unrelated live guard. Native algorithm initialization/computation, remaining algorithm teardown providers and physical hardware behavior are separate work. The allocator header's goodix_mem_deinit declaration alone does not identify an executed stock implementation; no speculative pool reset is added. Observed pool-cell xrefs cover initialization and control lookup, with indirect-reference limitations retained.

## Reconstructed entries

| Stock entry | Bytes | SHA-256 | Reconstructed symbol |
|---|---:|---|---|
| `0x0002D460` | 294 | `a8e129fa871645cef4b3fb81905ec18d8547c61a0cd4f01cd44686021f018f28` | `goodix_mem_free` |
| `0x0002D54C` | 116 | `1d5c425841dc5df88d88d264b28e99e087ac9d6d2c2f7bb94449ced636f7e532` | `goodix_mem_malloc` |
| `0x0002D5C0` | 152 | `c3f676ec6c386354e1654696ec9fcc63760ea7979bcd40e2b017caea317c8635` | `r1_goodix_native_reallocate` |
| `0x00042D1C` | 6 | `579f66b93cd2bbcb53693929db18e36025cdc6e5d94aa3e7590989e1d8a117b1` | `r1_goodix_native_heap_control` |
| `0x0006DFC8` | 4 | `0bffb8b23eaedef5bb71bbecb723c77f97a7878e7b50f2e0b3e134ad129b9ad3` | `goodix_mem_free` |
| `0x0006DFCC` | 10 | `ec975c0f600955af00012f3f1360a6525e35b94aaed858a1a96084fc98e26e7c` | `goodix_mem_get_free_size` |
| `0x0002D4D6` | 30 | `6293f6e78d7514fbfbb0a1f96188ff04ed6a779d8dc1671b3d1f0d9cd5ce2e5c` | `goodix_mem_get_free_size` |
| `0x0006DFD6` | 46 | `9043f45d0bb0a82cd016e7497f082927a064c20ba39bd576673e8d0ea56bf23e` | `goodix_mem_init` |
| `0x0002D4F4` | 78 | `fdcd647a7bf811eca5fa2e25b638a1dd54a4f5af8903f68ec9cf4a18f4c4acce` | `r1_goodix_native_pool_initialize` |
| `0x0006E004` | 4 | `a40930b5c8c91fbbf34f343c83676cc599b033578a63baf90d12d7320aefd678` | `goodix_mem_malloc` |
| `0x00076A44` | 34 | `776ebb1dab7b2f3cee0720bcf13e594cac4a7f6287db22fd1e3b19802a1e4170` | `r1_goodix_native_bin_remove` |
| `0x00093E14` | 38 | `a4034e87968ea8710751b740fd92420bb40b25b47fad5a385c6d6e8609485f8b` | `r1_goodix_native_size_bin` |
| `0x00093E5E` | 68 | `59abaa52a4a02c67a5a3649840801e8fe1050da271c79756db3ffd0744cd3288` | `r1_goodix_native_bin_insert` |
| `0x000982C2` | 246 | `3841469090c0e0b0fc30cfc9848cc87a8d8fd49a6ef1e864f8641d45160e0a65` | `r1_goodix_native_bin_allocate` |

The extents total 1,126 executable bytes. Scatter-loaded bodies retain the exact segment lists in
`tools/evidence/summarize_r1_sensor_algorithm_heap.py`; hashes concatenate only executable spans.

## Complete call-site reduction

The heap boundary also contains twenty Goodix allocation/teardown helpers and one R1 pool
byte-fill. All twenty-one now compile through `reconstructed/goodix_primitives/`. The Goodix
helpers total 386 stock bytes; the R1 byte-fill is another 12 bytes. Eleven of those Goodix
helpers (180 bytes) were converted in the final call-site pass, together with the 12-byte R1
byte-fill; the other nine Goodix helpers (206 bytes) were already present in the primitive
reduction. The final pass maps:

| Stock entry | Bytes | Reconstructed symbol |
|---|---:|---|
| `0x00028EC0` | 10 | `goodix_primitives_release_context_pair` |
| `0x00056860` | 20 | `goodix_primitives_release_and_clear` |
| `0x00066276` | 20 | `goodix_primitives_release_and_clear` |
| `0x0006628A` | 20 | `goodix_primitives_release_and_clear` |
| `0x0006629E` | 20 | `goodix_primitives_release_and_clear` |
| `0x000662B2` | 20 | `goodix_primitives_release_and_clear` |
| `0x000662C6` | 20 | `goodix_primitives_release_and_clear` |
| `0x000667C0` | 6 | `goodix_primitives_release_if_present` |
| `0x00073154` | 22 | `goodix_primitives_release_two_and_clear` |
| `0x00092B58` | 2 | `goodix_primitives_byte_fill` |
| `0x00092B60` | 12 | `goodix_primitives_byte_fill` (R1 product code) |
| `0x00098FFC` | 20 | `goodix_primitives_release_two` |

Together with the twelve allocator-core entries, 33 of the 34 exact heap-boundary rows now have
direct compiled-C mappings. The remaining row, R1 terminal diagnostic `0x0002E952`, is represented
by the allocator's explicit exhaustion callback and remains product policy; it is not an opaque
allocator dependency. Tests cover free-and-null, multi-field release ordering, context-pair
release, and overlap-safe byte fill in addition to the allocator tests below.

## Recovered contract

- 44-byte pool-control prefix and two bitmap-selected, size-ordered bins;
- pools must exceed 1,024 bytes;
- eight-byte minimum request, four-byte request rounding, and eight-byte block headers;
- boundary tags recording prior block size and previous/current allocation bits;
- a wilderness/top block used before ordinary free-list search exhaustion;
- split only when at least 16 bytes remain;
- forward and backward coalescing on release;
- realloc shrink/split or allocate/copy/free growth; and
- an explicit exhaustion callback in place of the stock terminal product diagnostic.

The recovered target stored native pointers inside its pool metadata. The reconstruction uses
checked pool-relative offsets, so the same source is safe on 64-bit hosts and Cortex-M4 without
pointer truncation. Header words are encoded explicitly as little-endian bytes, avoiding a libc,
alignment, or opaque-address dependency.

`tests/test_reconstructed_goodix_heap.c` covers initialization errors, geometry, both bin
classes, zeroing allocation, split reuse, full coalescing, realloc shrink/grow, exhaustion, and a
deterministic 1,000-operation churn test. Host, ASan/UBSan, and freestanding Cortex-M4 builds use
the same source.
