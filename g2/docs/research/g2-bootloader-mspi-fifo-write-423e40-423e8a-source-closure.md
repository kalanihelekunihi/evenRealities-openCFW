# G2 bootloader MSPI FIFO-write source closure

The complete 74-byte `mspi_fifo_write` body at
`[0x00423E40,0x00423E8A)` is source-owned by
`runtime_mspi_fifo_write_423e40.c`. The MIT clean-room source is
2,466 bytes with SHA-256
`3594fe14cc673e58032785ab9f5fbacb0479db9d0187b7b49610734fdbe31f48`.
Both reviewed Clang profiles emit the same 74-byte unrelocated section,
SHA-256 `aac9e4aa3174a187885885bcffef4eaa8fb5d7f2a3a7557925f22f4becd41b50`.
After the single `R_ARM_THM_CALL` relocation at offset `0x3A` binds the
retained status checker at `0x0041D246`, the body is byte-identical to stock,
SHA-256 `8ea56d5bbd1d671d999791ea24b747f4083048a9bfe169360470ebf4d36914d1`.

The typed host model preserves four-module validation, MSPI base/stride,
TXFIFO and TXENTRIES offsets, partial-word rounding, timeout arguments, and
last-status return behavior. The software identity also closes against the
BSD-3-Clause AmbiqSuite 5.1.0 source at commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`.

No device or MMIO operation occurred. Physical FIFO, timeout, register, and
cold-boot validation is blocked by unavailable physical evidence; future qualification
still requires authorized G2 evidence and is not treated as software completeness evidence.
