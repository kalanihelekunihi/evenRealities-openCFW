# P2-20953 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for 116 bytes at 0x47E178..0x47E1EC. Candidate and fresh instruction, pseudocode, and reference artifacts match exactly.

The entry preserves its first two arguments in R4/R5. A fresh flag-byte read controls the -2 early exit. The capacity guard uses a fresh global word plus R5 with 32-bit wrap, then unsigned-compares the sum against 32769; wrapped sums are evaluated as wrapped values. On the rejecting path, E06A cleanup runs before the global capacity word is cleared. The handle pointer is loaded and its word freshly tested. If absent, a fresh capacity observation chooses the E0C8 or E144 helper; nonzero helper return exits. Otherwise, or with a present handle, 474682 receives `(entry R0,1,entry R1, fresh handle)`. Only exact full-result equality with R5 succeeds. Mismatch invokes cleanup and returns -5. Success independently reloads capacity, adds R5 with wrapping arithmetic, stores it, and returns zero.

POP R1/R4/R5/R6/R7/PC restores R1 from the saved entry R3 slot, subject to any helper stack effects. External helper contracts remain unresolved. Candidate status stays partial/unaccepted; no source or gate files changed.
