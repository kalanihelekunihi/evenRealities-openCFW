# G2 bootloader per-instance descriptor-initializer source closure

The authenticated body at `[0x00422DC6,0x00422E28)` now compiles exactly from
maintained MIT C under both reviewed Cortex-M55 profiles. The
98-byte installed body has SHA-256
`a8cfef03c32750c788e9226d7ed587f8c6e04a3a7202970f613c5737eb7a755a`;
its unrelocated image has SHA-256
`6a47b40b24695bbd2b4ad04b618f7a284670ac68f5979545abe8b4df3dbe3cc6`.
The source `runtime_hw_descriptor_init_422dc6.c` is 3,041 bytes with SHA-256
`7d72d0e2e102ff74f9fe1b0ce453269226654aed94fd4df83b635a2c7820e653`.

The function validates the nullable instance and its low-25-bit
`0x01EA9E06` header, then clears the two publication flags at offsets `0xDC`
and `0xDD`. Each nonzero argument pair independently initializes and publishes
a 24-byte descriptor at instance offset `0x34` or `0x4C`. The retained
constructor at `0x004275EA` zeroes the first three words and stores the pair's
value, constant enable word `1`, and buffer argument in words three through
five. Two strict `R_ARM_THM_CALL` relocations at body offsets 62 and 90 bind
that reviewed seam. The sole direct caller is at `0x0041F6AC`; the signature
literal is retained at `0x00423830`.

Six focused tests pin the body, caller, literal, retained constructor, and
successor; cover null and mismatched headers without mutation; cover every
absent-pair gate; verify both exact descriptor layouts and publication flags;
verify call order; admit authenticated high header flags; and cross-compile
both reviewed target profiles.

Canonical provider accounting becomes 21,713 source-owned, 16,528 generated
patch, 16 alignment, and 125,583 retained official bytes, including 362 cave
bytes and 6,126 exact in-place bytes across 265 source-owned functions and 201
patch sites. Provider and byte-identical unsigned-package hashes remain
unchanged. The 4,623,670-byte flash plan has SHA-256
`e15b1575d93968f623450c3ea1a021aff473beb74969b6b99ce452ebd6204590`
with 6,643 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. The next authenticated executable body begins
at `0x00422E28`. Live SRAM/MMIO descriptor ownership, DMA/controller timing,
buffer lifetimes, interrupt interaction and cold-boot qualification are
explicitly blocked by unavailable authorized responsive G2 evidence;
firmware-wide functional completeness is not claimed.
