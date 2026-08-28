# G2 bootloader per-instance configuration-latch source closure

The authenticated body at `[0x00422EE2,0x00422F4C)` now compiles exactly from
maintained MIT C under both reviewed Cortex-M55 profiles. The
106-byte installed body has SHA-256
`c29518455fcc8058de0a0c6be773227f0aa9eda462085fa39707f8708d6ce5b0`;
its unrelocated image has SHA-256
`0b447483de1bbfb8a48b51d441fe6e3c64a7c15d55d5551806d1acbe90ce8c6f`.
The 3,184-byte source has SHA-256
`6f43faf99f625d628a5642ecadc47dc63bf75b14f6d345fa8a14e8e69563acec`.

The service enters the retained critical section at `0x0041B8EC` and restores
the saved `PRIMASK` token on every return. An already-latched instance byte at
offset `0x119` returns `0x08000004` without modifying the instance. The first
successful latch sets that byte, copies configuration byte `0x34` to instance
offset `0xD4`, copies seven words from configuration offsets `0x00..0x18` to
instance offsets `0xA0..0xB8`, clears the runtime word at `0xD8` and byte at
`0xDE`, and returns zero. One strict `R_ARM_THM_CALL` relocation at body offset
8 binds the retained critical-section provider.

Five focused tests pin the body, caller, busy-status pool, retained provider
and successor; cover exact first-latch mutation and preservation, duplicate
latch fail-closed behavior, critical-token restoration on both paths, and both
reviewed target compilers.

Canonical provider accounting becomes 22,005 source-owned, 16,528 generated
patch, 16 alignment, and 125,291 retained official bytes, including 362 cave
bytes and 6,418 exact in-place bytes across 267 source-owned functions and 201
patch sites. Provider and byte-identical unsigned-package hashes remain
unchanged. The 4,625,116-byte flash plan has SHA-256
`0fdbc2c75564879fae344b05f343349cb88a34d23aaed73e530e3ada3daa8160`
with 6,645 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. The next authenticated executable body begins
at `0x00422F4C`. Live interrupt atomicity, concurrent latch ownership, SRAM and
MMIO consumers, peripheral activation and cold-boot qualification are
explicitly blocked by unavailable authorized responsive G2 evidence;
firmware-wide functional completeness is not claimed.
