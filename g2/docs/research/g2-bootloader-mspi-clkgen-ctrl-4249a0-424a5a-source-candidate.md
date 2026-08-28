# G2 bootloader clock and XIP-delay closure (`0x004249A0`–`0x00424A5A`)

The 120-byte `mspi_clkgen_ctrl` and adjacent 66-byte
`mspi_get_xip_off_min_delay` are production-routed exact dual-profile
BSD-3-Clause source. The delay selector preserves the complete authenticated
frequency mapping: enum values 6–9 map to 8, 10–13 to 4, 14–15 and 18–19 to 2,
20–23 to 1, and other values preserve the current delay.

Host models cover clock enable/disable/configure ordering, PRIMASK restoration,
10-microsecond settling delay, and every XIP-delay selection class. Target
adapters compile to the official 120- and 66-byte bodies under both reviewed
profiles.

This software-only source wave performed no hardware operation. Live clock,
XIP timing, power-transition, and cold-boot qualification is deferred by
project direction; this source closure does not by itself declare firmware
functional completeness.
