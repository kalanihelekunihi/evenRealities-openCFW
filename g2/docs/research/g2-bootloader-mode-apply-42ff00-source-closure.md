# G2 bootloader mode-router source closure

The authenticated entry `[0x0042FF00,0x0042FFF2)` is a 242-byte
mode-to-service router. Modes 1, 2, 3, 4, and 8 publish normalized Boolean
values to service IDs `0x81`, `0x7D`, `0x80`, `0x8E`, and `0x92`. Modes 6, 7,
and 9 update a bit in the aggregate word at `0x200270D0` under the retained
critical-section provider and publish whether any aggregate bit remains set.
Other modes return without action. The sole caller is `0x0042FFF8`; there is no
interior or stored entry.

`runtime_mode_apply_42ff00.c` is first-party MIT clean-room source. Apple clang
21 and Homebrew clang 22 reproduce every stock byte under eight strict call
relocations. Relocated SHA-256 is
`2bf23ab0e4988009a2692db968a818ffeb5f010919982b1235db1b85d8735ae6`;
unrelocated SHA-256 is
`3f26b603da390864dd2be07c458566263a63400f78d428f98113b1540bc53d1d`.
Portable tests cover each direct service mapping, low-byte normalization,
aggregate set/clear transitions, aggregate publication, and ignored modes.

No hardware operation occurred. Live SRAM ownership, interrupt/concurrency,
peripheral behavior, reset, and cold-boot qualification is blocked by
unavailable physical evidence. Firmware-wide completeness is not claimed.
