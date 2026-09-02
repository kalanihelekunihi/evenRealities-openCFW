# G2 bootloader System PLL disable source closure at `0x004273DC`

## Result

The complete 48-byte stock entry at `[0x004273DC, 0x0042740C)` is replaced
in place by reviewable BSD-3-Clause C implementing AmbiqSuite 5.1.0
`am_hal_syspll_disable()`. Apple Clang 21 and Homebrew LLVM 22 both emit an
exactly fitting 48-byte body, so this admission requires no redirect, source
cave, generated fill, or relocation.

The implementation rejects a null or incorrectly tagged handle without MMIO,
clears only `SYSPLLPDB` in `PLLCTL0`, then clears the handle's enable bit after
the volatile register write. Host tests cover invalid handles, enabled and
already-disabled state, preservation of unrelated register and prefix bits,
and the official unconditional read/write behavior for every valid handle.

## Authentication

- stock body: 48 bytes, SHA-256
  `18fb22183427c03dff67cd845829f31b77a1cf974c0c91eda17e83308934dc73`;
- Apollo-main analogue `[0x00539A10, 0x00539A40)`: 48 bytes, SHA-256
  `f45a5402b99d6dad3fc6f6549fbf6b229ecb2d30de69ac3e08e77b133d25e132`;
  44/48 bytes are identical in two address-dependent difference runs;
- direct bootloader callers: `0x00422260` and `0x0042733C`;
- stock literals: handle magic `0x01504C30` at `0x004275AC` and `PLLCTL0`
  `0x400204D8` at `0x004275B4`;
- official source: AmbiqMicro `ambiqhal_ambiq` commit
  `e8baebd44008dfec7197d40d53c8a62f3a36b38b`, file
  `mcu/apollo510/hal/mcu/am_hal_syspll.c`.

Both reviewed compilers emit the same 48-byte body with SHA-256
`6ea444f7edb5ff562b81963683ff048002e7d916ef89cb87dd1a333dd955aecb`,
with no relocations or raw instruction encodings.

## Hardware boundary

No authorized G2 hardware or physical register trace is available. Live PLL
power-down, lock-state decay, timing, current draw, and downstream clock
consumer behavior are therefore **blocked by unavailable physical evidence**.
This closure performs compilation and immutable-image analysis only; it does
not read live MMIO, flash, reset, sign, or communicate with a device.
