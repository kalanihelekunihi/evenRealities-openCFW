# G2 bootloader hardware-handle services source closure

Date: 2026-09-01

Four complete handle services at `0x0042EA32`, `0x0042EB74`, `0x0042EBAA`,
and `0x0042EBE2` are MIT production C in
`runtime_hw_handle_services_42ea32.c`. They validate the masked handle magic
`0x01AFAFAF`, reset handle state, encode a three-bit and ten-bit configuration,
gate enable on status bit zero, and set or clear command bit 31.

Both reviewed compilers reproduce all 206 bytes exactly without relocations.
The Apollo-main analogues are byte-for-byte exact. Shared literals pin the
magic and register addresses `0x40038000`, `0x4003800C`, and `0x40038040`.
Portable tests cover invalid handles, configuration masking, ready/not-ready
enable paths, reset behavior, and idempotent disable.

Live peripheral register behavior is **blocked by unavailable physical
evidence**. No MMIO, flashing, reset, or completeness claim occurred.
