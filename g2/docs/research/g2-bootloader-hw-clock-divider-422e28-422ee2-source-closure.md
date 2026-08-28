# G2 bootloader per-instance clock-divider source closure

The authenticated body at `[0x00422E28,0x00422EE2)` now compiles exactly from
maintained MIT C under both reviewed Cortex-M55 profiles. The
186-byte installed body has SHA-256
`4a9a62072ca502be40f4c3ecf68b1ba3871f34be9258aa90ffdca7526f8378c4`;
its unrelocated image has SHA-256
`41b4bcc9a1111d46f05374d2d6aa2981ce0f74ace42d7027b22c51aa43fc9583`.
The 3,770-byte source has SHA-256
`a522934185c0668e7055ca282dd3e1e9c6c11351d17bc34c21ea0d9aadd53707`.

The service selects one of six authenticated reference clocks from bits
`[6:4]` of per-instance register offset `0x30`: 24, 12, 6, 3, 48, or 49.152
MHz. Modes zero and seven return `0x08000002` and zero the achieved-rate
output. Valid modes derive a four-bit integer divider and six-bit fractional
remainder from the requested rate, program register offsets `0x24` and `0x28`,
and return the achieved integer rate. An integer divider of zero returns
`0x08000003` without programming. One strict `R_ARM_THM_CALL` relocation at
body offset 76 binds the already source-owned exact unsigned 64-bit divmod
runtime at `0x0042287C`. The sole direct caller is `0x004231A8`.

Seven focused tests pin the body, caller, literal pools, divmod call and
successor; cover invalid modes, all six reference clocks, exact integer and
fractional programming, achieved-rate calculation, all four banks, zero-range
failure, divisor wrap/zero behavior in the safe host model, and both reviewed
target compilers.

Canonical provider accounting becomes 21,899 source-owned, 16,528 generated
patch, 16 alignment, and 125,397 retained official bytes, including 362 cave
bytes and 6,312 exact in-place bytes across 266 source-owned functions and 201
patch sites. Provider and byte-identical unsigned-package hashes remain
unchanged. The 4,624,387-byte flash plan has SHA-256
`bcfc9cba4e4f5e12fcb53c27a977f7c3b9d2a3a2df429d6cac2d4c86bc698788`
with 6,644 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. The next authenticated executable body begins
at `0x00422EE2`. Live reference-clock selection, divider register effects,
MMIO timing, peripheral rate accuracy and cold-boot qualification are
explicitly blocked by unavailable authorized responsive G2 evidence;
firmware-wide functional completeness is not claimed.
