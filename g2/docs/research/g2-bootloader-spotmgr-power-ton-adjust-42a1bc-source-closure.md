# G2 bootloader SPOT-manager Ton-trim selector source closure

Date: 2026-09-01

## Result

The 232-byte VDDC/VDDF Ton-trim selector at
`[0x0042A1BC,0x0042A2A4)` is BSD-3-Clause production C in
`runtime_spotmgr_power_ton_adjust_42a1bc.c`, grounded in Ambiq's Apollo510
`spotmgr_power_ton_adjust`.

Apple clang 21.0.0 and Homebrew clang 22.1.8 reproduce the exact body without
relocations, SHA-256
`8964efd235151acf974a0248acac460c57de14ed8effbb879293a54d97f6dfd0`.
All 19 direct callers and four external shared literals are authenticated.
The Apollo-main analogue at `0x005A423C` shares 218 bytes, with its 14 changed
bytes confined to twelve address-coupled difference runs.

The portable model passes 50,000 randomized trim states. It preserves the
power-state-8 override to Ton state 7, selects the exact five-bit fields for
states 0 through 7 and the default case, and writes VDDC at bits 25–29 and
VDDF at bits 8–12 without disturbing neighboring bits.

Actual regulator timing, Ton efficacy, temperature/power transitions, reset,
and cold-boot qualification are **blocked by unavailable physical evidence**.
No hardware operation or firmware-wide completeness claim occurred.
