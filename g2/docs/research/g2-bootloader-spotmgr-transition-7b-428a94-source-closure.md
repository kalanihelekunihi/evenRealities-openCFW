# G2 bootloader SPOT-manager transition 7b source closure

Date: 2026-09-01

## Result

The 276-byte function at `[0x00428A94,0x00428BA8)` is BSD-3-Clause
production C in `runtime_spotmgr_transition_7b_428a94.c`. It is grounded in
Ambiq's Apollo510 `transition_sequence_7b` at commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`, with the authenticated G2
five-microsecond delay retained where current upstream uses ten microseconds.

Apple clang 21.0.0 and Homebrew clang 22.1.8 emit the same 276-byte body after
five strict `R_ARM_THM_CALL` relocations: four calls to the delay provider at
`0x0041D1C0` and one status-delay call to `0x0041D21C`. The linked SHA-256 is
`1e0e7ddb0036670d692a97a50f6cc821d2a2358e741b72d502e943d31bb0b351`;
the unrelocated SHA-256 is
`b9d0e8cfa43d1d1a1514e2ff0fda56c2b0d50511f816d53894b19f7feb3975d8`.
The exact caller is `0x0042A068`, and twelve external shared literals are
authenticated.

The portable form passes 50,000 deterministic randomized states, including
trim restore, LP/HP switching, bounded 20-iteration polls, HFRC2 forcing and
release, power-switch changes, and terminal sequence 26.

No authorized G2 hardware is available. Live MMIO ordering, rail stability,
oscillator switching, timer/status timing, reset, and cold-boot qualification
are **blocked by unavailable physical evidence**. No hardware operation or
firmware-wide completeness claim occurred.
