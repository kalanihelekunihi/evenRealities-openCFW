# G2 bootloader SPOT-manager internal-power-domain source closure

Date: 2026-09-01

## Result

The 22-byte helper at `[0x0042A19C,0x0042A1B2)` is BSD-3-Clause production C
in `runtime_spotmgr_internal_power_domain_42a19c.c`, grounded in Ambiq's
Apollo510 `spotmgr_internal_power_domain_set`.

Both reviewed compilers reproduce the exact body without relocations,
SHA-256
`34664d76a6022980a70a926ac4c1108f43d33974584a9cb854f8faa59a8ebacf`.
The direct caller is `0x0042AAF4`; the Apollo-main analogue is `0x005A421C`;
and the shared HP-to-deep-sleep flag is `0x200271B0`. The portable model
passes 100,000 randomized state pairs and sets the flag only for prior HP
state 1 transitioning to requested deep-sleep state 2.

Actual HP/deep-sleep transitions, override effects, reset, and cold-boot
qualification are **blocked by unavailable physical evidence**. No hardware
operation or firmware-wide completeness claim occurred.
