# G2 bootloader hardware register-profile restoration source closure

The authenticated entry `[0x0042F2FA,0x0042F38E)` is a 148-byte
mode-sensitive register restoration, power-toggle, and finalization service.
Its sole caller is `0x0042F3B8`; no interior or stored entry exists. The
Apollo-main analogue at `0x0059FCA2` shares 144 of 148 bytes.

`runtime_hw_register_profile_restore_42f2fa.c` is first-party MIT clean-room
source. Apple clang 21 and Homebrew clang 22 reproduce every stock byte after
two strict power-toggle calls and one finalizer call. Relocated SHA-256 is
`b1b11b9cae5d09e8bd59aae4099ed288cbd5d1e55980dbdda910c89282b7af40`;
unrelocated SHA-256 is
`fbc38be724a162f01ab84627f97fa0843a969e4fedd792f00e1f2783fd13314a`.
Portable tests cover the non-mode-three two-field restoration path,
mode-three inactive finalization, and active restoration with ordered power
toggles and control-bit clearing.

No hardware operation occurred. Live MMIO, clock, power, peripheral timing,
concurrency, reset, and cold-boot qualification is blocked by unavailable
physical evidence. Firmware-wide completeness is not claimed.
