# P2-20949 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for 118 bytes at 0x47E0C8..0x47E13E. Candidate and fresh instruction, pseudocode, and reference artifacts match exactly.

The routine allocates 112 bytes total, including 96 local bytes. After a successful E090 guard, it reads the counter global twice: the first observation is retained in R4 and a second is incremented/stored with wrapping arithmetic. DF28's full result gates the rest. DE0A formats the local buffer at SP+32 with count 64 and R4; its result is ignored. The 474550 result is stored to the global handle word, which is then freshly reloaded for the zero test. Zero returns -5 without cleanup. A nonzero handle is freshly loaded with the global word at E2A4 and passed with R4 to 48ED00, then the global handle is freshly reloaded for the `(SP,1,32,handle)` call. Only a full result exactly 32 succeeds; other results invoke E06A cleanup and return -5. Success stores R4 and 32 to the two output globals and returns zero.

The epilogue adds 100 to SP, discarding the 96-byte local area and saved entry R3, then restores R4/R5/PC. Local initialization and helper contracts remain unresolved. No source or gate files changed; status remains partial/unaccepted.
