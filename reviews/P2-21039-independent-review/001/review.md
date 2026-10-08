# P2-21039 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47F11C..0x47F204 (232 bytes), and instruction/reference outputs match. LOW8 mode gate, mode-3 word guard, helper result handling, and saved stack aliases match the disassembly. The equal branch performs a fresh read through FAC4 and a separate subsequent fresh byte read through R5; only the latter may be written to FAC4 target. Unequal flow orders flag/helper updates, word bit updates, byte write, then FAC4 read; mode-specific callbacks remain separate. PRIMASK restore occurs after the update helper path, and POP restores R1/R2 slots that may have been overwritten. No readback validation, ownership, MMIO, or timing claim inferred.
