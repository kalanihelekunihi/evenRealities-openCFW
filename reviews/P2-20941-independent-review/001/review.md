# P2-20941 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for 98 bytes at 0x47DF8A..0x47DFEC. Candidate and fresh instruction, pseudocode, and reference artifacts match exactly.

The routine allocates a 32-byte frame with 16 local bytes that are not explicitly initialized here. A 474550 full-zero result exits with R0=0. Otherwise 474634 receives `(SP,1,16,R4)`, its full result is saved in R5, and 4745F4 cleanup runs regardless. A non-16 R5 result returns the cleanup's live R0. For exact 16, a fresh SP0 must equal the literal at 0x47E2B0; then DDFE runs and its full result must equal a distinct SP12 load. Any mismatch leaves the corresponding live R0 value for the shared epilogue. Only after these guards does the code write SP4 to the global word at 0x47E2A4. It then reads SP8 unsigned: values below 2 write constant 1 to 0x47E2A8 and return 1; otherwise it separately reloads SP8, writes that value, and returns the full value.

The epilogue adds 20 to SP, discarding local storage and saved entry R3, then restores R4/R5/PC. Distinct stack observations and path-dependent return values are preserved. Helper and literal ownership remain unresolved; no source or gate files changed.
