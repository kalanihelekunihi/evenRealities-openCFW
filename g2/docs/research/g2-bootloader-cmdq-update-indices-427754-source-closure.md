# G2 bootloader command-queue index update at `0x00427754`

## Result

The complete authenticated body `[0x00427754,0x00427794)` is AmbiqSuite
Apollo510 command-queue `update_indices()` and is now production-routed to
reviewable BSD-3-Clause C. The earlier census boundary at `0x00427790` split
the four-byte PRIMASK restore from the function; the terminal pop at
`0x00427792` proves the corrected 64-byte boundary.

## Upstream and binary authentication

The authoritative source is
`mcu/apollo510/hal/mcu/am_hal_cmdq.c` at immutable Ambiq commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`. The 35,930-byte source has
SHA-256 `60aa2126ca01cd72f746a92d6f34a13e909fdab24ebfab6d6b0a70b026d8fa83`
and Git blob `0a286e565cad27cef801c389b5dedae826a2669a`. The vendored command-queue
header is 10,496 bytes, SHA-256
`0113aed2f109c5f022d38055b83a75c2cf141e8621177296757fc8315926762f`.

- Stock body: 64 bytes, SHA-256
  `8a2b2f4d159d6c4d3ec68b81c254a81c976d757dc1c9d57319649cacf6c65317`.
- Direct callers: `0x00427944`, `0x00427A7C`, and `0x00427AF2`; no stored
  entry pointer or interior direct caller exists.
- The sole provider edge is the critical-save call at body offset `0x04` to
  `0x0041B8EC`; the saved PRIMASK is restored exactly before return.
- Apollo-main has the independent 64-byte analogue at `0x00538D18`, SHA-256
  `b509adac0c08c9239aabb77c270b559aa76cd2b797bc473f2d0d01a22e3c2837`.
  It is identical in 61 of 64 bytes; both difference runs are confined to the
  image-local critical-provider branch encoding.

## Recovered behavior and ABI

The private state is the upstream 44-byte `am_hal_cmdq_t`: `head`,
`current_index`, `end_index`, and the register-table pointer are at offsets
12, 28, 32, and 36. The register table exposes the queue-address and hardware
current-index pointers at offsets 4 and 8. Within one critical section the
source:

1. masks the hardware index to eight bits;
2. combines it with the high 24 bits of the monotonic software end index;
3. subtracts `0x100` when signed modular comparison selects the prior epoch;
4. snapshots the hardware queue-address register into `head`; and
5. restores the exact saved PRIMASK.

Apple clang 21.0.0 and Homebrew clang 22.1.8 each emit a 44-byte leaf with
one strict `R_ARM_THM_CALL` relocation at object offset 4. Their relocated
SHA-256 values are respectively
`e585f8d2fb16a83c80a7f76234bfe30e7ff3002e2837d8a7bb0475765cf4b160`
and `c8d7d16687b05815d24d6e0492e6ad500bb4845b9ce070db8c8063a294628911`.
The leaf occupies reclaimed body space at `[0x00427758,0x00427784)` behind a
four-byte redirect; the remaining 16 bytes are deterministic generated NOPs.

## Hardware boundary

Live register reads, interrupt/concurrency behavior, wrap timing, downstream
command-queue callers, and cold boot are **blocked by unavailable physical
evidence**. No flash, signing, reset, live MMIO, or hardware mutation was
performed.
