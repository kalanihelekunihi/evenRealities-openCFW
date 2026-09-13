# GCC binary64 remainder preservation

`gcc-fp-bit-sticky-rounding.patch` modifies GCC `libgcc/fp-bit.c` from the
repository's pinned C-SKY GCC revision
`1e9b70447a8417f5c692370de4533e43d754e8fa`. It is a local correction, not a claimed
upstream commit. The original source retains its GPL and GCC Runtime Library
Exception notices; the build creates a separate patched copy and records hashes.

Multiplication and division must preserve a nonzero discarded remainder as a
sticky bit in the intermediate significand. Rounding to normal precision before
`pack_d` shifts a subnormal can round twice, and discarding the remainder can turn
an above-halfway value into an exact tie. This patch replaces the intermediate
rounding blocks with sticky-bit accumulation; `pack_d` performs final rounding.

Reproductions (binary64 bit patterns):

- `0x000fffffffffffff * 0x3fefffffffffffff`: expected
  `0x000fffffffffffff`; unmodified source returns `0x000ffffffffffffe`.
- `0x0018000000000000 / 0x4000000000000001`: expected
  `0x000bffffffffffff`; unmodified source returns `0x000c000000000000`.

The unchanged upstream build and diagnosis remain available for comparison.
The corrected build is experimental until the numerical, reference, container,
and hardware checks appropriate to firmware integration have been completed.
