# G2 bootloader System PLL postdivider source closure

The bootloader interval `[0x00427160, 0x004272ac)` is the AmbiqSuite 5.1.0
`am_hal_syspll_config_generate_with_postdiv` routine. The identification is
bound to the 332-byte stock body
`7f3f9f3bbe5797d7db00b7ec229994ebd4a5e96e8a37889214e1d058de50558f`
and the same-size Apollo-main analogue at `0x00539794`, whose SHA-256 is
`a436b072488dc3f19e2bab81b60a33b352b49f2ff86b5363337a98a7811ceffd`.
The bodies differ at only eight two-byte address-coupled literal/call fields;
the other 316 bytes are identical.

The upstream source is `mcu/apollo510/hal/mcu/am_hal_syspll.c` at official
Ambiq HAL commit `e8baebd44008dfec7197d40d53c8a62f3a36b38b`, which imports AmbiqSuite
SDK 5.1.0. It is BSD-3-Clause licensed. The reviewed upstream file is 48,933
bytes with SHA-256
`b2ac1b4a89ff7c2e17f57f199998688e9de4a67ca9035d5dbf8063b94da18b28`.
The official PTS-A and PTS-B tables remain retained typed data at
`0x00433cb8` and `0x00433cc8`; their 16-byte SHA-256 values are respectively
`8dc1585615ae5ce6a2b8fe2fcde6d582d5b704c59382cc1d2b3bd953b8383d28`
and `b71376a2c8f8bd0dde154022f58cb7e61872ce85a4622ac436b92c16cdf45930`.

`runtime_syspll_postdiv_427160.c` retains the authenticated behavior as
ordinary C. It requests both the 60 MHz low-VCO and 240 MHz high-VCO
candidates from the source-owned minimum-VCO provider, computes Ambiq's
mode/VCO-indexed PTS score with 32-bit arithmetic, selects the lower-score
candidate (high-VCO on a tie), preserves the caller-owned reference selector,
and returns out-of-range when neither candidate is valid.

The generated entry redirect at `0x00427160` enters a 268-byte source cave at
`[0x00427168, 0x00427274)`. Apple clang 21 emits SHA-256
`37392e154a61d40029493ea8d68e384968a3923a95cfc5b20f7a8fcc33009a89`;
Linux clang 22 emits SHA-256
`d006d16c7a05df73f368051d52c662ddd10fe15be369ee3b1a27de80bf308e1b`.
Each profile has exactly two reviewed Thumb-call relocations to
`open_cfw_bootloader_syspll_min_fvco_427040` at `0x00427048`. The remaining
56 bytes of the replaced stock function are generated unreachable NOP fill.

Host tests cover low-only and high-only validity, score selection, tie
selection, field publication, preservation of `reference_select`, and the
no-valid-candidate error. This evidence is software-only and performs no MMIO,
signing, packaging, flashing, reset, or device communication. System PLL
electrical behavior and clock lock on a physical Apollo510B target remain
`blocked by unavailable physical evidence` until an authorized device and
measurement record exist.
