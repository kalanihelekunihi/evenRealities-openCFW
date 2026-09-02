# G2 bootloader hardware-handle command source closure

Date: 2026-09-01

The complete 32-byte service at `0x0042EFF4` is MIT production C. It validates
the masked handle magic `0x01AFAFAF`, returns error two for an invalid handle,
and writes command `0x37` to `0x40038008` on success. Both reviewed compilers
and the Apollo-main analogue at `0x0055E070` are byte-for-byte exact.

Portable tests cover valid and invalid routes. Live peripheral command effects
are **blocked by unavailable physical evidence**. No MMIO, flashing, reset, or
completeness claim occurred.
