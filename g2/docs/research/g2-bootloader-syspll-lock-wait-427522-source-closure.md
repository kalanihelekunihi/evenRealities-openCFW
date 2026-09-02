# G2 bootloader System PLL lock-wait source closure

The complete 102-byte stock entry at `[0x00427522, 0x00427588)` is routed to
reviewable BSD-3-Clause C implementing AmbiqSuite 5.1.0
`am_hal_syspll_lock_wait()`. A generated `B.W` and one alignment NOP occupy
`[0x00427522, 0x00427528)`, the compiled function occupies
`[0x00427528, 0x00427580)`, and an unreachable generated NOP tail occupies
`[0x00427580, 0x00427588)`.

## Authentication

- Stock body: 102 bytes, SHA-256
  `978d2a48a7b3971bfb7e0d4f2006836aeacb4c137467dfead90d41377316be3e`.
- Direct stock caller: `0x00422202`.
- The stock `BL` at body offset `0x60` targets the retained delay/status
  provider at `0x0041D246`.
- Literal words authenticate the tagged-handle magic `0x01504C30`, PLLCTL0
  `0x400204D8`, PLLDIV1 `0x400204E0`, and PLLSTAT `0x400204E4`.
- The 102-byte main-image analogue at `0x00539B56` has SHA-256
  `e1998b485572e20fb3a2118c8c8f01427e112d268308baf41299ace6849d8a11`;
  96 of 102 bytes are identical across the two images in six address-coupled
  difference runs.
- The semantic reference is AmbiqSuite commit
  `e8baebd44008dfec7197d40d53c8a62f3a36b38b`, file
  `mcu/apollo510/hal/mcu/am_hal_syspll.c`.

## Production behavior

`runtime_syspll_lock_wait_427522.c` validates the tagged handle before MMIO,
preserves the official PLLCTL0/PLLDIV1/PLLCTL0 volatile-read order, rejects a
disabled PLL, selects the 1000- or 1875-cycle lock budget from VCOSELECT,
computes `(cycles * refdiv + 11) / 12`, and forwards the exact PLLSTAT address,
mask, expected value, and equality policy to the retained status-check
provider.

Both reviewed compiler profiles emit the same 88-byte relocated body with
SHA-256
`9c751242434d7fd769e8e36600f944014899537ff9613fce57cdc500fc71d629`.
The unrelocated body SHA-256 is
`2fd5a60b6794c0bcb8836a1b80d858d8fc70e6c91a7e1e77180b3cd350790b9b`;
its sole relocation is `R_ARM_THM_CALL` at offset 70 to `0x0041D246`.

Host tests cover invalid handles, ordered reads, disabled-state rejection,
low- and high-VCO timeout boundaries, exact polling arguments, and provider
status propagation. No hardware operation is performed by this closure.

## Hardware evidence

Live PLL lock acquisition, timeout behavior under real reference clocks, and
register-side effects require authorized G2 hardware and instrumentation.
Their validation is **blocked by unavailable physical evidence**.
