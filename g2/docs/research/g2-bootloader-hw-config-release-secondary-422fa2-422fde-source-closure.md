# G2 bootloader secondary configuration-release source closure

The authenticated body at `[0x00422FA2,0x00422FDE)` now compiles exactly from
maintained MIT C under both reviewed Cortex-M55 profiles. The
60-byte installed body has SHA-256
`9779bb01d8332c3219ab8dec41d5d6fc39a33ab7dda97cd14a61257fffb965f6`;
its unrelocated image has SHA-256
`88d577b0b9c4a4f58d68ebd4e027cc0681ac441da9d47d798e831fccf3caf386`.
The 2,234-byte source has SHA-256
`d240e67dd1dd23c0b339b374a79bac26da6620e5d7b32988d2b740cbb6fba5ae`.

The service enters the retained critical section at `0x0041B8EC` and restores
the saved `PRIMASK` token on every return. State byte `0x11A` must equal one;
otherwise it returns seven without mutation. A valid release clears the state,
uses the retained memset at `0x0041560C` to zero 56 bytes at instance offsets
`0x64..0x9B`, clears the word at `0x9C`, and returns zero. Strict
`R_ARM_THM_CALL` relocations at body offsets 6 and 36 bind those two retained
providers.

Five focused tests pin the body, sole caller, providers and successor; cover
the exact 60-byte secondary runtime reset, all noncanonical-state failures,
provider arguments, critical-token restoration on both paths, and both
reviewed target compilers.

Canonical provider accounting becomes 22,151 source-owned, 16,528 generated
patch, 16 alignment, and 125,145 retained official bytes, including 362 cave
bytes and 6,564 exact in-place bytes across 269 source-owned functions and 201
patch sites. Provider and byte-identical unsigned-package hashes remain
unchanged. The 4,626,654-byte flash plan has SHA-256
`2fc61fd11765948d78562547efacb50ff87efcb3ebead62e911ee8a2730d0581`
with 6,647 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. The next authenticated executable body begins
at `0x00422FDE`. Live interrupt atomicity, concurrent release/latch ownership,
retained memset ABI, SRAM/MMIO consumers, peripheral shutdown and cold-boot
qualification are explicitly blocked by unavailable authorized responsive G2
evidence; firmware-wide functional completeness is not claimed.
