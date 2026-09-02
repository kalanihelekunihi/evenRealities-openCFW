# G2 bootloader sixteen-channel state/event classifier closure

The authenticated entry `[0x0042CFE0,0x0042D0F2)` is a 274-byte classifier.
After retained enable, mode, and state shortcuts, it scans sixteen enabled
channels and asserts the shared output for values in `[0,6)`, `[19,25)`, or
`[256,480)`. The sole caller is `0x0042D58C`; no interior or stored entry
exists.

`runtime_state_event_zero_42cfe0.c` is first-party MIT clean-room source. Both
reviewed compilers reproduce all bytes under one strict call. Relocated SHA-256
is `c03a0f379d7bbafb93e2c9074e4d754081699d39c63b4c2820765ffdab996624`;
unrelocated SHA-256 is
`01821e038de30d1a7e3cf1f0cb4e6124781b6860f1931800f3e89fe167b00e6a`.
The Apollo-main analogue at `0x005A0204` shares 271/274 bytes. Portable tests
cover all range boundaries, enable gates, shortcut paths, and invalid input.

No hardware operation occurred. Live SRAM, MMIO, peripheral, reset, and
cold-boot qualification is blocked by unavailable physical evidence.
Firmware-wide completeness is not claimed.
