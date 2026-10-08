# P2-20939 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for 98 bytes at 0x47DF28..0x47DF8A. Candidate and fresh instruction, pseudocode, and reference artifacts match exactly.

The routine creates a 32-byte frame, calls 439C04 to prepare a 16-byte local area, then writes fresh global words to SP4 and SP8. It calls the DDFE wrapper with the local record and stores its full result at SP12; SP0 remains dependent on the unresolved initializer. The next 474550 call receives the literal address at 0x47E174. A zero full result returns -5. Otherwise 474682 receives `(SP,1,16,R4)` and its full result is retained in R5; 4745F4 cleanup always follows. Only exact R5==16 returns zero; all other results return -5, ignoring the cleanup result. The epilogue adds 20 to SP, discarding local bytes plus the saved entry R3, then pops R4/R5/PC. R1/R2/R3 are not restored.

No template-copy or initializer semantics are inferred beyond observed instructions. Status stays partial/unaccepted; no source or gate files changed.
