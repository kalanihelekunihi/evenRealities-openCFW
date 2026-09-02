# G2 bootloader register-profile transfer closure

The authenticated entry `[0x0042F020,0x0042F14E)` is a 302-byte validated
hardware register-profile capture/apply service. It validates the retained
handle magic, accepts operations 0, 1, and 2, captures or applies thirteen
profile words, preserves the control low bit, maintains the profile-valid byte,
and returns explicit invalid-handle, invalid-profile, provider, and unsupported-
operation statuses. Direct callers are `0x00430068` and `0x004301BE`.

`runtime_register_profile_transfer_42f020.c` is first-party MIT clean-room
source. Both reviewed compilers reproduce all bytes under four strict calls.
Relocated SHA-256 is
`2e6cca806f60cc19024673c46f635245eaea0c8e7aff23580b1a8cf15e487a73`;
unrelocated SHA-256 is
`7019743d54c61b4d148d591856d90a4c23d482770fc7938db8b4b374ef53278c`.
The Apollo-main analogue at `0x0055E09C` shares 292/302 bytes. Portable tests
cover validation, all operations, capture/apply, provider failure, low-byte
operation semantics, and disabled paths.

No hardware operation occurred. Live SRAM, MMIO, clock, peripheral, reset, and
cold-boot qualification is blocked by unavailable physical evidence.
Firmware-wide completeness is not claimed.
