# G2 bootloader secondary configuration-latch source closure

The authenticated body at `[0x00422F4C,0x00422FA2)` now compiles exactly from
maintained MIT C under both reviewed Cortex-M55 profiles. The
86-byte installed body has SHA-256
`99c1945b3def3fccc0f8f5abc12e6233e33ef41ed6121b2e4fe5f465bfe99bb2`;
its unrelocated image has SHA-256
`c1ec1f68e0623f215e0c3865c318d2278ed5048174e7b9a7aa2c48b4f10437e0`.
The 3,138-byte source has SHA-256
`78b2d9500182d1b23d8b99fd8fb432cc47955546c1d9061bfe27d7dee6ed6e29`.

The service enters the retained critical section at `0x0041B8EC` and restores
the saved `PRIMASK` token on every return. An already-latched instance byte at
offset `0x11A` returns `0x08000005` without mutation. The first successful
latch sets that byte, copies configuration byte `0x34` to instance offset
`0x98`, copies seven words from configuration offsets `0x00..0x18` to instance
offsets `0x64..0x7C`, clears the runtime word at `0x9C`, and returns zero. One
strict `R_ARM_THM_CALL` relocation at body offset 8 binds the retained critical
provider.

Five focused tests pin the body, sole caller, busy-status pool, retained
provider and successor; cover exact first-latch mutation and preservation,
duplicate fail-closed behavior, critical-token restoration on both paths, and
both reviewed target compilers.

Canonical provider accounting becomes 22,091 source-owned, 16,528 generated
patch, 16 alignment, and 125,205 retained official bytes, including 362 cave
bytes and 6,504 exact in-place bytes across 268 source-owned functions and 201
patch sites. Provider and byte-identical unsigned-package hashes remain
unchanged. The 4,625,886-byte flash plan has SHA-256
`7b4d686e47a731844e2639c5b5546512fc8c5d22c56a526b1835745fe30e3a6c`
with 6,646 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. The next authenticated executable body begins
at `0x00422FA2`. Live interrupt atomicity, concurrent secondary-latch
ownership, SRAM and MMIO consumers, peripheral activation and cold-boot
qualification are explicitly blocked by unavailable authorized responsive G2
evidence; firmware-wide functional completeness is not claimed.
