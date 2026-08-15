# Goodix heap reduction correlation

Status: owner-authorized clean-room reconstruction, 2026-08-14. This is not Goodix source.

The application image is the byte-exact rebuild with SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`. The complete
twelve-function Goodix-owned `goodix_mem` / `GdMem` core now compiles from transparent C in
`reconstructed/goodix_heap/`; the restrictively licensed binary remains evidence only.

## Reconstructed entries

| Stock entry | Bytes | SHA-256 | Reconstructed symbol |
|---|---:|---|---|
| `0x0002D460` | 294 | `a8e129fa871645cef4b3fb81905ec18d8547c61a0cd4f01cd44686021f018f28` | `goodix_heap_free` |
| `0x0002D54C` | 116 | `1d5c425841dc5df88d88d264b28e99e087ac9d6d2c2f7bb94449ced636f7e532` | `goodix_heap_zero_allocate` |
| `0x0002D5C0` | 152 | `c3f676ec6c386354e1654696ec9fcc63760ea7979bcd40e2b017caea317c8635` | `goodix_heap_reallocate` |
| `0x00042D1C` | 6 | `579f66b93cd2bbcb53693929db18e36025cdc6e5d94aa3e7590989e1d8a117b1` | `goodix_heap_control` |
| `0x0006DFC8` | 4 | `0bffb8b23eaedef5bb71bbecb723c77f97a7878e7b50f2e0b3e134ad129b9ad3` | `goodix_heap_free` |
| `0x0006DFCC` | 40 | `ca7bc8ec0c785670e410153de9e72674385950650e45c0d6c1b123c96331cc50` | `goodix_heap_available_bytes` |
| `0x0006DFD6` | 124 | `dab9a92e720146d0e0d0b9b3413112765ea4bb8ea404ec6c41b648f61b1f6208` | `goodix_heap_initialize` |
| `0x0006E004` | 4 | `a40930b5c8c91fbbf34f343c83676cc599b033578a63baf90d12d7320aefd678` | `goodix_heap_zero_allocate` |
| `0x00076A44` | 34 | `776ebb1dab7b2f3cee0720bcf13e594cac4a7f6287db22fd1e3b19802a1e4170` | `goodix_heap_unlink_free_block` |
| `0x00093E14` | 38 | `a4034e87968ea8710751b740fd92420bb40b25b47fad5a385c6d6e8609485f8b` | `goodix_heap_size_to_bin` |
| `0x00093E5E` | 68 | `59abaa52a4a02c67a5a3649840801e8fe1050da271c79756db3ffd0744cd3288` | `goodix_heap_insert_free_block` |
| `0x000982C2` | 246 | `3841469090c0e0b0fc30cfc9848cc87a8d8fd49a6ef1e864f8641d45160e0a65` | `goodix_heap_allocate_core` |

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
