# G2 bootloader per-instance hardware-shutdown source closure

The authenticated body at `[0x00422FDE,0x0042308E)` now compiles exactly from
maintained MIT C under both reviewed Cortex-M55 profiles. The
176-byte installed body has SHA-256
`7241a63d66335d340551094ebc58d5aaf07bb7e88bb254c4e2dc8c9975701107`;
its unrelocated image has SHA-256
`924d56dfd5ca19efe150f455e0c814cdf352e2805a9037f0558de52ab059c8ff`.
The 4,166-byte source has SHA-256
`4b5766fe249a50797840f96f9cf1e930c2b3b01b39a24e884999daa19425f379`.

The service selects one of four `0x40039000` register banks from instance word
`0x28`, snapshots enable bit 14, conditionally clears bits 14 and 11, and
always clears bit 9 before shutdown. Status bit 3 at register offset `0x18`
causes a delay of `10000000 / instance[0x30] + 1`. Instance flag `0x11B`
optionally invokes the source-owned secondary register clear. The retained
shutdown provider and source-owned secondary configuration release then run in
order. The original bit-14 state is restored and bit 9 is always set; bit 11
remains cleared only when the original enable was set. Four strict
`R_ARM_THM_CALL` relocations bind the delay, register-clear, shutdown and
release services.

Six focused tests pin the body, sole caller, two literals, four providers and
successor; cover quiesce-time register state, provider ordering, conditional
clear and delay, restored masks, all four banks, and both reviewed target
compilers.

Canonical provider accounting becomes 22,327 source-owned, 16,528 generated
patch, 16 alignment, and 124,969 retained official bytes, including 362 cave
bytes and 6,740 exact in-place bytes across 270 source-owned functions and 201
patch sites. Provider and byte-identical unsigned-package hashes remain
unchanged. The 4,627,385-byte flash plan has SHA-256
`19065a0b5f07435bfe09e1257f50547952ddd21010f72a94a4920f89615d938f`
with 6,648 placed, two unresolved, five container-only, and six protected
regions.

No hardware operation occurred. The next authenticated executable body begins
at `0x0042308E`. Live MMIO masks, clock and peripheral state, delay accuracy,
interrupt/concurrency ordering, provider side effects and cold-boot shutdown
qualification are explicitly blocked by unavailable authorized responsive G2
evidence; firmware-wide functional completeness is not claimed.
