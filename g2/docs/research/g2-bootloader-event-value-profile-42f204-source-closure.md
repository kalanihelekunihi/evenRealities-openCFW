# G2 bootloader event-value hardware-profile source closure

The authenticated entry `[0x0042F204,0x0042F2FA)` is a 246-byte event-value
profile publisher. Outside the active hardware state it saves two register
fields, applies the mode-two and saturating six-bit adjustments, and delays 15
cycles. In the active state, when the retained enable byte permits it, it
temporarily disables the register-power service, applies two saturating
seven-bit fields and two feature masks, restores power, and delays 15 cycles.
It always returns zero. Its sole caller is `0x0042F3C0`; no interior or stored
entry exists.

`runtime_event_value_profile_42f204.c` is first-party MIT clean-room source.
Apple clang 21 and Homebrew clang 22 reproduce all 246 stock bytes under five
strict call relocations. Relocated SHA-256 is
`501f73cf98677984aeedc3b9d60df3775a99c7e68520f23d6bd11c8b0e342317`;
unrelocated SHA-256 is
`afc00b5ad826855d562f2c1f82f67b728ea5144b92754578cc319e35fcb10b0d`.
The Apollo-main analogue at `0x0059FBAC` shares 234 of 246 bytes. Portable tests
cover both branches, both saturation boundaries, the retained gate, event
normalization, all published fields, and invalid model input.

No hardware operation occurred. Live SRAM, MMIO, clock, power, timing,
peripheral, reset, and cold-boot qualification is blocked by unavailable
physical evidence. Firmware-wide completeness is not claimed.
