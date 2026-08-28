# G2 bootloader `mspi_device_configure` source closure (`0x00424120`–`0x0042488E`)

Status: production-routed exact dual-profile source; physical validation is
blocked by unavailable physical evidence.

The official 1,902-byte function has SHA-256
`3b95c5af6c3c2140cc4e1522a1f284ae31825e4e35ae6c2427e0edba41774818`
and direct callers at `0x00425012` and `0x004258E4`. It matches AmbiqSuite
5.1.0 `mspi_device_configure` and covers every device enum value 0–25:
serial, dual, quad, octal, octal DDR, hex DDR, mixed-width modes, and 3-wire
serial variants.

Authenticated state fields are module `+0x04`, clock-on-D4 `+0x09`, and device
configuration `+0x0A`. The complete register behavior covers `PADOUTEN +0x44`,
`DEV0CFG +0x84`, and `DEV0XIP +0x90` relative to
`0x40060000 + module * 0x1000`.

The BSD-3-Clause candidate in
`research/admission/bootloader_mspi_device_configure_424120/` includes a typed
host model for all 26 configurations and both clock-on-D4 states. The target
adapter emits the authenticated body without relocations. Apple clang 21 and
Homebrew clang 22.1.8 both produce the official bytes exactly. The production
leaf is compiled from
`components/bootloader/core_overlay/runtime_mspi_device_configure_424120.c`.

Component accounting after admission is 27,771 source-owned bytes, 12,184 of
them exact in-place, and 119,525 retained official bytes. The next function is
`mspi_piomixed_configure`, 232 bytes at `[0x0042488E, 0x00424976)` with SHA-256
`e8323e8e0ac6f59465ce1d30087eb6f4a2e3de336c45bff3e6954325a2e32fee`.

This software-only source wave performed no flash, reset, signing, or MMIO
operation. Live all-mode MSPI register, pad, XIP, clock-on-D4, and cold-boot
qualification is blocked by unavailable physical evidence; this source closure does not
by itself declare firmware functional completeness.
