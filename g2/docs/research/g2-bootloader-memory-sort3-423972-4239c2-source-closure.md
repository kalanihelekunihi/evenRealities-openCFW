# G2 bootloader three-element comparator/exchange source closure

> **Superseded temple-status premise:** Treat temple nonresponse/unavailability
> claims below only as history. The case was bumped during lunch and caused the
> disconnect, not firmware or flashing; exclude it from feasibility conclusions.
> Hardware testing remains blocked by unavailable physical evidence.

The 80-byte helper at `[0x00423972,0x004239C2)` has exact SHA-256
`b6ec5384c9fd2cd9f993179c74e4993b5d85e6a0ea5c1b1533842d11fe4b76ff`.
Maintained source `runtime_memory_sort3_423972.c` is 1,980 bytes with SHA-256
`cd4a90eb7eeae787ea18f661b2c9499f6da79bef1e70c03593b806d13df3a528`.
Both reviewed Clang profiles reproduce the body; the unrelocated SHA-256 is
`5080e5a64c0863549b89e41fcf6a87faf5f9ec9ab16b9898ac0ac42276c5f6fa`.

The helper executes the three comparisons `(second, first)`, `(third,
second)`, `(second, first)`, exchanging on negative results. Two strict calls
and the authenticated fixed-address 16-bit tail branch bind the source-owned
exchange helper at `0x00423864`. Four host tests cover all distinct
permutations, duplicates, comparison order, the 134-byte successor, and dual
target compilation.

Canonical accounting is 23,999 source-owned, 16,528 generated patch, 16
alignment, and 123,297 retained official bytes across 290 source-owned
functions, five caves, 87 exact in-place leaves, and 201 patch sites. The
4,648,165-byte flash plan has SHA-256
`17bc9a9a59b2902f8b25aa42a209f536c8e26be48ba051a17ab0b627a4a83606`
with 6,678 placed and zero unresolved regions. The byte-identical package is
4,745,418 bytes with SHA-256
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`.

No signing, flashing, reset, boot, device, SRAM, or MMIO operation occurred.
This software-only helper is fully qualified offline. Firmware-wide
completeness is not claimed: the earliest retained executable remains
`0x0042308E`, the sequential frontier is the 134-byte heap helper at
`0x004239C2`, and physical qualification remains blocked by unavailable
authorized responsive right-temple evidence.
