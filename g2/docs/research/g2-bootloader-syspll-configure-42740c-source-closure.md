# G2 bootloader System PLL configuration source closure at `0x0042740C`

## Result

The complete 278-byte stock entry at `[0x0042740C, 0x00427522)` is routed to
reviewable BSD-3-Clause C implementing AmbiqSuite 5.1.0
`am_hal_syspll_configure()`. A generated `B.W` occupies the first four bytes,
the compiled 240-byte implementation occupies authenticated reclaimed body
space at `[0x00427410, 0x00427500)`, and 34 bytes of generated NOP fill close
the bounded replacement region.

The implementation validates the tagged handle and disabled state; enforces
the reference-divider, integer/fraction feedback-divider, and ordered
postdivider bounds; preserves unrelated fields while programming `PLLCTL0`,
`PLLDIV0`, and `PLLDIV1` in the official order; calls the retained reference
clock update provider; and publishes the four final output-power fields in
the official order. Host tests cover every error class, inclusive boundary
values, the integer and fractional paths, register-field preservation, write
ordering, retained-provider arguments, and the final register state.

## Authentication

- stock body: 278 bytes, SHA-256
  `61aad9e2393f589de90e10cd74396e589ee4aa1547947732738abb105a1ba2af`;
- Apollo-main analogue `[0x00539A40, 0x00539B56)`: 278 bytes, SHA-256
  `952498aa439122aadd5548d9bb261e5fcee1bae570e7b71931464f86c69ac010`;
  267/278 bytes are identical in six address-dependent difference runs;
- direct bootloader caller: `0x00422170`;
- retained stock provider edge: offset `0xEE` (`0x004274FA`) to
  `0x0041AC92`, the reference-clock update service;
- stock literals: handle magic `0x01504C30` at `0x004275AC`, `PLLCTL0`
  `0x400204D8` at `0x004275B4`, `PLLDIV0` `0x400204DC` at `0x004275B8`,
  and `PLLDIV1` `0x400204E0` at `0x004275BC`;
- official source: AmbiqMicro `ambiqhal_ambiq` commit
  `e8baebd44008dfec7197d40d53c8a62f3a36b38b`, file
  `mcu/apollo510/hal/mcu/am_hal_syspll.c`.

Apple Clang 21 emits 240 relocated bytes with SHA-256
`916771eadfbe45eb61d244376c14bb1354fe5bc7162003d6c5951189e8e8c876`;
Homebrew LLVM 22 emits 240 relocated bytes with SHA-256
`d8ae9445de5140e0eaaf0015769ce6ad1cd6a5ad20bc2b5770b2932eabbf07f8`.
Each compiler emits exactly one authenticated `R_ARM_THM_CALL` relocation to
`0x0041AC92`; neither source path uses raw instruction encodings.

The resulting raw bootloader providers are independently pinned as Apple
Clang 21 SHA-256
`d1e7151591adc15f43e7ef3efeab8d0fdf2eb1901c3035bfa62efe21a6de1489`
and Homebrew LLVM 22 SHA-256
`d04cb44cb802e742ecffb576d85722c8cea4bb69c35522751906020aff7e2683`.

## Hardware boundary

No authorized G2 hardware or physical register trace is available. Live PLL
divider behavior, reference-clock switching, lock timing, output-phase power
state, current draw, and downstream clock behavior are therefore **blocked by
unavailable physical evidence**. This closure performs compilation, host
semantic testing, and immutable-image analysis only; it does not read live
MMIO, flash, reset, sign, or communicate with a device.
