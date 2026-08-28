# G2 bootloader MSPI FIFO-read source closure

The complete 158-byte `mspi_fifo_read` body at
`[0x00423E8A,0x00423F28)` is source-owned by
`runtime_mspi_fifo_read_423e8a.c`. The MIT clean-room source is
4,381 bytes with SHA-256
`d82f43ac56e65dd0cd4072828a6566d3ec6cc34008572704f26d1d72f9efc274`.
Both reviewed Clang profiles emit the same 158-byte unrelocated section,
SHA-256 `e6a327fa4c600e41273694a52a6bc7c1faf77f01020ccf3272d9304d1d0f51f1`.
Two `R_ARM_THM_CALL` relocations at offsets `0x4E` and `0x72` bind the retained
status checker at `0x0041D246`; the linked body then matches stock exactly,
SHA-256 `9bb93dd67b7844ce1e9d75d6a165667cc38f27b45ad937ea7815c357d8ce4a7b`.

The typed host model covers four-module validation, zero-length behavior,
full-word and little-endian remainder copying, both timeout short-circuits,
RXFIFO/RXENTRIES address derivation, and preservation of bytes after a failed
remainder poll. The software identity also closes against BSD-3-Clause
AmbiqSuite 5.1.0 commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`.

No device or MMIO operation occurred. Physical FIFO, timeout, register, and
cold-boot validation is blocked by unavailable physical evidence; future qualification
still requires authorized G2 evidence and is not treated as software completeness evidence.
