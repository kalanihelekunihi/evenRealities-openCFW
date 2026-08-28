# G2 bootloader MSPI command-queue init source closure

The production admission for `[0x00423F28,0x00423F54)` uses the
MIT clean-room target implementation documented and analyzed in
`g2-bootloader-mspi-cq-init-423f28-423f54-boundary.md`. Its 44 linked bytes
have SHA-256
`8e2e5409620c3c1b334d8c3ede2ea19b20a31471e40a0c8b0c88f6550a7e9b05`
and are byte-identical to the authenticated stock interval. The only target
relocation is an `R_ARM_THM_CALL` at offset `0x26` to the typed retained
`am_hal_cmdq_init` provider at `0x00427794`.

The exact source identity and semantics derive from AmbiqSuite 5.1.0
`mspi_cq_init` at upstream commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b` under BSD-3-Clause. The
clean-room implementation, rather than the unmodified upstream compiler
candidate, is admitted because both reviewed Clang profiles reproduce the
stock linked bytes and relocation contract. The retained provider remains an
official-package boundary; corresponding official binary redistribution
authority is unresolved and is not inferred from the upstream source license.

The subsequent CQ-term, CQ-control, CQ-pause, and high-priority DMA-programming
admissions move the current retained frontier to `0x004240AA`. Hardware validation is deferred by project
direction; future authorized physical qualification remains required. No
hardware, MMIO, flashing, signing, or publishing operation was performed.
