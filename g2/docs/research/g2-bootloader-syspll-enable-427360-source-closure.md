# G2 bootloader System PLL enable source closure at `0x00427360`

## Result

The complete 124-byte stock entry at `[0x00427360, 0x004273DC)` is routed to
reviewable BSD-3-Clause C implementing AmbiqSuite 5.1.0
`am_hal_syspll_enable()`. The 84-byte dual-compiler-identical body occupies
authenticated reclaimed body space at `0x00427364`; a generated `B.W` at the
stock entry and bounded NOP fill replace the remainder of the original body.

The implementation validates the `0x01504C30` handle prefix, returns success
without MMIO when already enabled, preserves the four ordered volatile
SIMOBUCK readiness reads, returns invalid-operation status `7` if any required
bit is inactive, sets `SYSPLLPDB` in `PLLCTL0`, and publishes the handle enable
bit only after the register write. Host tests cover invalid, idempotent,
inactive-power, and successful enable paths.

## Authentication

- stock body: 124 bytes, SHA-256
  `0d2de1918fa403072986f15453ed612b3afd5383b89bdd95e8bf599ddb454280`;
- Apollo-main analogue `[0x00539994, 0x00539A10)`: 124 bytes, SHA-256
  `40618d8ed60a8a9e45079e8778a8e124d20fcfb5b317674574f21025b943963a`;
  118/124 bytes are identical in three address-dependent difference runs;
- direct bootloader caller: `0x0042217E`;
- stock literals: handle magic `0x01504C30` at `0x004275AC`, `VRCTRL`
  `0x40020060` at `0x004275B0`, and `PLLCTL0` `0x400204D8` at `0x004275B4`;
- official source: AmbiqMicro `ambiqhal_ambiq` commit
  `e8baebd44008dfec7197d40d53c8a62f3a36b38b`, file
  `mcu/apollo510/hal/mcu/am_hal_syspll.c`.

Apple Clang 21 and Homebrew LLVM 22 both emit the same 84-byte body with
SHA-256 `b34095d709ec4b90846d9882ee05a2ce47a181166de1e90cba70998e23d1bebe`
and no relocations or raw instruction encodings.

## Hardware boundary

No authorized G2 hardware or physical register trace is available. Live
SIMOBUCK readiness, PLL power-up, lock behavior, timing, current draw, and
downstream clock consumers are therefore **blocked by unavailable physical
evidence**. This closure performs compilation and immutable-image analysis
only; it does not read live MMIO, flash, reset, sign, or communicate with a
device.
