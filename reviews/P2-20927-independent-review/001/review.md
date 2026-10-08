# P2-20927 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for all 84 instruction bytes at 0x47DCB4..0x47DD08. Candidate and fresh instruction, pseudocode, and reference files match exactly.

The first entry saves R4/LR and calls 44906C. Only a full-width result exactly equal to 2 reaches 44A1EA. That full result is kept in R0 and added with wrapping arithmetic to the literal value at 0x47E280; an unsigned comparison against 0x47E284 determines the output byte (1 if below, otherwise 0). The function returns the full 44A1EA result, not the byte boolean. Other 44906C results write zero and return zero.

The frameless 0x47DCE4 leaf executes MRS PRIMASK, then CPSID i, then returns, so it captures the previous mask before disabling maskable interrupts. The 0x47DCEC entry allocates/overwrites a 16-byte local area, calls 43C0E4 then 4D3554, loads a signed halfword from the local area, discards 16 bytes, and restores R4/PC. Its return is the sign-extended local halfword, not the second helper's result. Helper semantics remain opaque beyond these instruction effects; candidate remains partial/unaccepted, with no source or gate changes.
