# G2 bootloader MX25U25643G read-transfer source closure

The complete authenticated 170-byte entry `[0x004205F4,0x0042069E)` now
routes to `open_cfw_bootloader_mspi_read_transfer_4205f4` in maintained
clean-room C. The stock SHA-256 is
`7fe24d8d1ac2fda0dcce1f4e7d4364b2bbe3df283c05000ab32d357de04a6749`;
the 5,337-byte source SHA-256 is
`d310d632be00ea4c9c136b5e089340d83cecdeaa74be814b5864e9abf592a525`.

Stock and host evidence pin null-handle status 2, null-buffer/zero-length
status 6, addresses below `0x02000000` with status 5 otherwise, 16-bit
instruction truncation, conditional address publication, the exact 24-byte
Ambiq transfer descriptor, read direction, a 1,000,000-cycle blocking timeout,
HAL-status propagation, and failure-only diagnostics. Five authenticated
callers enter at `0x004205AE`, `0x00420766`, `0x00420818`, `0x00420C80`, and
`0x00420D92`. Retained seams are the handle word at `0x200270DC`, blocking
MSPI transfer at `0x004262E0`, and source-routed log dispatch at `0x00415FAE`.

Both toolchains emit the same relocation-free 172-byte leaf, SHA-256
`b7ab22593ca756879ce8f8dbdcf249806ec23beff8029959fecb39d3c2e784ed`.
Apple places it at offset 12,168/runtime `0x00437400`; Linux adds four alignment
bytes and places it at offset 12,152/runtime `0x004373F0`. Apple/Linux
overlay/provider identities are 12,340/160,940 bytes with SHA-256
`be335a86ffe63996e55bd9ec4bdb31cce331ede084216742ede71648c1e6e802` /
`5f1d63b5aa0e7c503627ac7df46adb2bd285c456a280cef8ecfea0413896c40c`
and 12,324/160,924 bytes with SHA-256
`1f088854ed5f15951790bc8fd9c81576884af1a4d922c29988abaf474f1dac9d` /
`09ff7f47e27791a28a6fe3d4740140df46297911ba743039b45c36ca69344301`.

Canonical accounting is 12,325 source-owned, 13,636 generated patch, 16
alignment, and 134,963 retained official bytes across 179 routed functions,
160 relocated leaves, and 177 patch sites. Unsigned Apple/Linux packages are
4,742,518 / 4,518,512 bytes with SHA-256
`afb351f7b54edc564b536155e90a8fff96f4f58cd7fda4cdeb6a54c6c9446a3d` /
`14f07a9d9a1e98a85efa7df661ec5b661ab8a64b5ddf492bd95aba551097bc74`;
their flash plans contain 6,509 / 3,455 placed regions and two unresolved
hardware regions.

Nothing was signed, flashed, installed, reset, booted, or sent to hardware.
Live descriptor ABI, HAL timeout/status behavior, external-flash reads,
JEDEC/MSPI/XIP behavior, and cold boot remain blocked by unavailable physical
evidence from an authorized responsive right G2 temple; the left temple must
remain stock. Executable bodies at and after `0x0042069E` remain software
gaps, so firmware-wide completeness is not claimed.
