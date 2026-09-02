# G2 bootloader System PLL minimum-VCO source closure

The bootloader interval `[0x00427040, 0x0042714c)` is the AmbiqSuite 5.1.0
`am_hal_syspll_config_generate_minFVCO` routine.  The identification is bound
to the stock 268-byte body
`7fc066eeef20eeb8b3bf91c3746fdeac37b6eaabc66d004de1757ad005436422`,
the 50-byte post-divider table at `0x00431e70`, and the byte-comparable
Apollo-main analogue at `0x00539674` (260 of 268 bytes identical).  The four
two-byte differences are address-coupled literal loads.

The upstream source is `mcu/apollo510/hal/mcu/am_hal_syspll.c` at official
Ambiq HAL commit `e8baebd44008dfec7197d40d53c8a62f3a36b38b`, which imports AmbiqSuite
SDK 5.1.0.  It is BSD-3-Clause licensed.  The reviewed upstream file is 48,933
bytes with SHA-256
`b2ac1b4a89ff7c2e17f57f199998688e9de4a67ca9035d5dbf8063b94da18b28`.

`runtime_syspll_min_fvco_427040.c` retains the authenticated behavior as
ordinary C: it applies the fractional-mode 10 MHz PFD floor, chooses the
smallest achievable pair of post-dividers, rejects total dividers above 49,
generates the VCO configuration through the source-owned floating selector,
checks the mode-dependent PFD minimum, and publishes the post-dividers only
after all checks succeed.  It calls the source-owned common-divisor helper and
selector rather than retaining their stock executable bodies.

The compiled function occupies the reclaimed stock body interval
`[0x00427048, 0x0042713c)`.  The generated entry redirect at `0x00427040`
routes both authenticated callers (`0x0042717c` and `0x00427198`) into that
leaf. Apple clang 21 emits a 244-byte leaf at `[0x00427048, 0x0042713c)` with
`2f01d112c0d1cdf4c0fa10048d434dd69d2331f84494f9949b6491a3dcff43f3`;
Linux clang 22 emits a 248-byte leaf at `[0x00427048, 0x00427140)` with
`8f45b7a2175a9b9a1a99c07f96320b28ebacfa74b7a94e8bca19c876e50af358`.
The profile-specific relocation contracts contain only the two reviewed
Thumb calls.  The post-divider table remains typed, authenticated retained
data rather than executable code.

This evidence is software-only.  It performs no MMIO, signing, packaging,
flashing, reset, or device communication.  System PLL electrical behavior and
clock lock on a physical Apollo510B target remain `blocked by unavailable
physical evidence` until an authorized device and measurement record exist.
