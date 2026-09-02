# G2 bootloader SPOT-manager state-transition selector source closure

Date: 2026-09-01

## Result

The 390-byte Apollo510 SPOT-manager power-state transition-sequence selector at
`[0x0042A2B4,0x0042A43A)` is BSD-3-Clause production C in
`runtime_spotmgr_state_transition_sequence_42a2b4.c`. It is grounded in
AmbiqSuite SDK 5.1.0 commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`, function
`spotmgr_state_transition_sequence_determine`.

Apple clang 21.0.0 and Homebrew clang 22.1.8 both emit the exact stock body
after one `R_ARM_THM_CALL` relocation at offset `0x12` to the authenticated
aligned memcpy entry `0x004156AC`. The linked body SHA-256 is
`c02ca4144181ebe16c3dffc47e1bec89a89fbb832fa8bb134b38dd8bf287444f`;
the unrelocated SHA-256 is
`e0fad5fe49ce4fde2b8a7371bc7a03824d8a273e9003c735317b3bb7075a7cf7`.

The three direct callers are `0x0042A462`, `0x0042A492`, and `0x0042A524`.
The literal at `0x0042ACB4` points to the authenticated 28-byte 5x5 transition
table at `0x00433498`, SHA-256
`d83c73b1f5370cc6063489aedc4f0701bdec2ca34a492233caa521c0cf2ea5e8`.
The Apollo-main analogue at `0x005A4334` has SHA-256
`f1b71cff0ba9b9fd7bb37d87bbfd1dcde7293361c5bf97e46bec825641bcc623`
and shares 384 of 390 bytes; its only two difference runs are the table-literal
load and memcpy call displacement.

The host model exhaustively verifies all 400 valid current/target power-state
pairs, including invalid transitions, temperature boundaries, 0↔8, 8↔12, and
10↔11 special cases. Actual regulator, temperature, reset, and boot behavior is
**blocked by unavailable physical evidence**. No firmware was signed, flashed,
or executed on hardware.

