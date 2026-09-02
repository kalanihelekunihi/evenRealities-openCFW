# G2 bootloader hardware-profile publisher source closure

The authenticated entry `[0x0042EA68,0x0042EAF6)` is a 142-byte validated
seven-field profile encoder and register publisher. Its sole caller is
`0x004300B6`; no interior or stored entry exists. The Apollo-main analogue at
`0x0055DAE4` shares 140 of 142 bytes.

`runtime_hw_profile_apply_42ea68.c` is first-party MIT clean-room source.
Apple clang 21 and Homebrew clang 22 reproduce every stock byte after the sole
strict mode-route call at offset `0x2E`. Relocated SHA-256 is
`1e62bb87b3abb1f8918525f1f3064c366982fc0afa075a018925d8f21376d686`;
unrelocated SHA-256 is
`2c8b1283be5ea34c8b2ca392315cea78f713d89ada1ebf6587dca17bdc7eab4e`.
Portable tests cover handle and type validation, route-status propagation,
all seven field masks, low-bit clearing, and publication to the authenticated
`0x40038000` register model.

No hardware operation occurred. Live MMIO, clock, peripheral timing,
concurrency, reset, and cold-boot qualification is blocked by unavailable
physical evidence. Firmware-wide completeness is not claimed.
