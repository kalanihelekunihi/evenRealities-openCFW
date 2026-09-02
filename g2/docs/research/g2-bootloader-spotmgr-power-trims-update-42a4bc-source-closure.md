# G2 bootloader SPOT-manager power/Ton trim router source closure

Date: 2026-09-01

The 138-byte `spotmgr_power_trims_update` body at
`[0x0042A4BC,0x0042A546)` is BSD-3-Clause production C grounded in AmbiqSuite
SDK 5.1.0 commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`.

Apple clang 21.0.0 and Homebrew clang 22.1.8 reproduce the exact linked body,
SHA-256 `7bc6936adbff287072bfdcdac3b453214f98f9604c11239abef5a15f63b5e9bb`,
after four strict provider relocations: Ton adjust, two stepwise temperature
dispatches, and state-sequence selection. The unrelocated SHA-256 is
`aed144230a794fe7b562c45bd45f9ba4afa02f2f1a9437c4635fd08402f60ec4`.
The sole caller is `0x0042AB52`; the authenticated callback-table pointer is
`0x20000158`. The Apollo-main analogue at `0x005A453C` shares 136 of 138 bytes.
Host tests cover 800 power/Ton route combinations, including no-op, Ton-only,
same-group temperature, mixed temperature/group, valid, and invalid routes.

Physical trim efficacy, rail stability, callback execution, reset, and boot
qualification is **blocked by unavailable physical evidence**. No signing,
flashing, reset, or live hardware access occurred.

