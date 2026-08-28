# G2 bootloader per-instance register-clear source closure

Two authenticated relocation-free leaves at `[0x00422D20,0x00422D7A)` now
compile exactly from maintained MIT C under both reviewed
Cortex-M55 profiles. The 44-byte primary clear has SHA-256
`74e3724ef4d0b99489a9c3ca805c8c3c8603f6cc8bd483acf3d836829980e0d9`;
the 46-byte secondary clear has SHA-256
`c037d8b13a19cbc61ee88209bac5b8e5ef628aed1363424bb66a80ce2cf24559`.

Both leaves select a `0x1000`-stride bank from the instance index and clear
register offset `0x48`. The primary leaf clears bits `0x10` and `0x20` in
register offset `0x04`. The secondary clears bit `0x20` there and clears the
low twelve bits of register offset `0x50`. The shared authenticated bank base
is `0x40039000`. Direct ingress is pinned at `0x004237FC` for the primary and
`0x00423056`/`0x004237D2` for the secondary.

`runtime_hw_register_clear_422d20.c` is 2,405 bytes with SHA-256
`dd8212cb402cffe1f63df3456197126bb34d47f3c685d5445c8164fe6cb6d97c`.
Four focused tests pin both bodies, callers/pools/boundary, exercise all four
banks and exact bit preservation, and cross-compile both target profiles.

Canonical accounting becomes 21,543 source-owned, 16,528 generated patch, 16
alignment, and 125,753 retained official bytes, including 362 cave bytes and
5,956 exact in-place bytes across 263 source-owned functions and 201 patch
sites. Provider and byte-identical package hashes remain unchanged. The
4,621,559-byte flash plan has SHA-256
`d0bbd6e98171006d3dab51f657e739747995851acfb10da4d53c704177d87fb4`
with 6,640 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. A retained four-byte datum occupies
`[0x00422D7A,0x00422D7E)` and the next executable body begins at
`0x00422D7E`. Live MMIO effects, bank ownership, peripheral state and cold-boot
qualification are explicitly blocked by unavailable authorized responsive G2
evidence; firmware-wide functional completeness is not claimed.
