# G2 bootloader introspective qsort source closure

The introspective sort core at `[0x00423A48,0x00423D08)` is 704 bytes with
SHA-256
`9c13dd0e980154026e6c64019ce90997dcbd5abafb79aabbbf7d3def82215bb8`.
The public qsort wrapper at `[0x00423D08,0x00423D20)` is 24 bytes with SHA-256
`ebab1f26584cfab24667fa6bd4a9c63641d5676a46affda15c6478a5d697d474`.
Maintained source `runtime_memory_qsort_423a48.c` is 10,745 bytes with SHA-256
`3b3057bcebaaa64f6f9dda25140cf4f2ff3497f8aeef479199022cde5655f461`.

Apple Clang 21.0.0 and Homebrew Clang 22.1.8 both reproduce all 728 final
bytes. The core's unrelocated SHA-256 is
`ca1c3b23c25bd6ea03b4f55da5095479c486168f5ff0d21583cbe8f3871fa929`;
17 strict call relocations bind the source-owned sort-three, rotate-three,
swap, memcpy, heap-sift, and rotate-to-front helpers. The wrapper is
relocation-free and carries its authenticated fixed-address call back to the
core. Self-recursive core calls resolve locally and are byte-pinned.

The recovered algorithm uses sampled median selection and three-way
partitioning while its recursion budget remains, falls back to heap sort at
the budget boundary for partitions of at least 33 elements, and uses an
insertion strategy for smaller partitions. Six host tests pin the core,
wrapper, and 56-byte successor identities; null/no-op behavior; whole-record
movement; duplicates; deterministic randomized arrays on both sides of the
33-element threshold; and both target toolchains.

Canonical provider accounting is 24,861 source-owned, 16,528 generated patch,
16 alignment, and 122,435 retained official bytes across 293 source-owned
functions, 179 relocated leaves, five caves, and 90 exact in-place leaves.
The provider remains 163,840 bytes with SHA-256
`3ae28d27b81ca70d96fd5846d04fa1a4f0add5a8514cee21f9f34bdaa1455eac`.
The byte-identical 4,745,418-byte package retains SHA-256
`3c8cdcdb4bc56b1a76b5ddabe6eb1bc79810aa6a99cf35acaec6bd019179c785`.
The deterministic 4,650,270-byte flash plan has SHA-256
`34f78e0fc343ebf1daee9a127dee83f548bc03226d8711e8b4774ed1b07eda0b`
with 6,681 placed, zero unresolved, six container-only, and six protected
regions.

No signing, flashing, reset, boot, device, SRAM, or MMIO operation occurred.
The qsort runtime is fully qualified offline, but firmware-wide completeness
is not claimed. The earliest retained executable remains `0x0042308E`; the
sequential frontier is the retained 56-byte service at `0x00423D20`.
Physical qualification remains blocked by unavailable authorized responsive
right-temple evidence.
