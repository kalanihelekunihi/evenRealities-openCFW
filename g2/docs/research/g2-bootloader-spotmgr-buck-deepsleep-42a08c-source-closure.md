# G2 bootloader SPOT-manager SIMOBUCK deep-sleep classifier source closure

Date: 2026-09-01

## Result

The 272-byte function at `[0x0042A08C,0x0042A19C)` is BSD-3-Clause production
C in `runtime_spotmgr_buck_deepsleep_state_42a08c.c`, grounded in Ambiq's
Apollo510 `spotmgr_buck_deepsleep_state_determine` at commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`.

Both reviewed compilers reproduce the exact stock body after one strict call
relocation at offset `0x30` to the STIMER-running provider `0x0041F3F0`.
Linked SHA-256 is
`d6be1f893c0f78437db76208bb71ae7bf478411acb3ec307430709cd3dfe2e67`;
unrelocated SHA-256 is
`6e729b8c3c563a543f80219483d16ec5b38f5f31bb9afdf0d5869f7b3f70869c`.
The direct caller is `0x0042AA7A`; the Apollo-main analogue at `0x005A410C`
shares 253 of 272 bytes, with all differences confined to address-coupled
loads and the provider call. Five external literals are authenticated.

The portable model passes 100,000 randomized snapshots covering temperature,
peripheral masks, SYSPLL state, STIMER state/clock, and all sixteen timer
enable/global-enable/clock predicates.

Actual deep-sleep entry, clocks, timer activity, SIMOBUCK behavior, rail
stability, reset, and cold-boot qualification are **blocked by unavailable
physical evidence**. No hardware operation or firmware-wide completeness
claim occurred.
