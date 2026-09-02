# G2 bootloader SPOT-manager state-transition effects source closure

Date: 2026-09-01

## Result

The 84-byte function at `[0x0042B014,0x0042B068)` is BSD-3-Clause
production C in `runtime_spotmgr_state_transition_effects_42b014.c`. Both
reviewed compilers reproduce the exact stock body with no relocations; its
SHA-256 is
`b3da01a94a3c08eb7eb0d7d344b6760d929296878e2dfbf9c4770373aedd3d88`.
The Apollo-main body at `0x005A0D44` is byte-for-byte identical. Direct calls
are authenticated at `0x0042BCB0` and `0x0042BD26`, with no stored or interior
ingress.

The leaf records one gated transition flag when moving from state 2 to state
1. When moving from state 0 to state 1, it clears bits 16, 6, and 3 of the
power-control register and clears the paired pending flag. The three boot
literals resolve to `0x200271B2`, `0x200271B0`, and `0x4002037C`; corresponding
Apollo-main literals independently preserve the same topology. The portable
model exhaustively tests all 65,536 low-byte state pairs with both flag gates.

Physical rail transitions, retained-flag observation, reset behavior, and
cold-boot qualification are **blocked by unavailable physical evidence**. No
hardware operation or firmware-wide completeness claim occurred.
