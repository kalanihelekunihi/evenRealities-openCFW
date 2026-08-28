# G2 bootloader unsigned 64-bit divmod source closure

The complete 560-byte IAR-compatible unsigned 64-bit divide/modulo runtime at
`[0x0042287C,0x00422AAC)` now compiles from maintained MIT C at
its exact stock address. The installed body SHA-256 is
`76998e68a31e9f88c2e09a1c163b60f5b03f4d879dc135483c81f8b10edfe720`;
the unrelocated compiler output SHA-256 is
`615f580255dcc295d19a41e08ee885fde57f1e971eee2e2ca9ff2a2b6b13d79c`.
One strict tail relocation binds the retained divide-by-zero handler at
`0x004275E8`.

The implementation preserves the four-register ABI: quotient in `r0:r1` and
remainder in `r2:r3`. It covers zero/high-word divisor partitions, divisors
one and two, 16-bit and 24-bit digit fast paths, normalized multiword division,
quotient correction after multiply/subtract borrow, dividend-smaller-than-
divisor behavior, and the retained zero-divisor tail. The three direct callers
are `0x0041F1D0`, `0x0041F1EA`, and `0x00422E74`.

`runtime_u64_divmod_42287c.c` is 6,378 bytes with SHA-256
`a7ed8c37476c615d7ff6ad63bafe1348f02516be317d1de553b7bb10ecc620da`.
Five focused tests pin body, callers, tail and successor; exercise small,
power-of-two, high-word and normalized paths; compare 500 deterministic cases
against native unsigned arithmetic; and compile both reviewed Cortex-M55
profiles.

Canonical accounting becomes 20,827 source-owned, 16,528 generated patch, 16
alignment, and 126,469 retained official bytes, including 362 cave bytes and
5,240 exact in-place bytes across 256 source-owned functions and 201 patch
sites. Provider and unsigned-package hashes remain unchanged. The
4,615,803-byte flash plan has SHA-256
`41cbff6234a93834d9041c8303a23d4b4b2b36fb50be37c20800acb791a509bd`
with 6,632 placed, two unresolved, five container-only and six protected
regions.

No hardware operation occurred. Divide-by-zero trap state, register ABI and
caller integration require authorized Apollo510 evidence, unavailable because
no authorized responsive right temple exists and the left temple must remain
stock. Firmware-wide functional completeness is not claimed; the next
executable body begins at `0x00422AAC`.
