# P2-20931 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for 74 bytes at 0x47DD62..0x47DDAC. Candidate and fresh instruction, pseudocode, and reference artifacts match exactly.

At 0x47DD62, the first helper's full result selects two paths. Nonzero explicitly writes zero to SP0 (overwriting saved R7) before calling 47E7B0 with the fresh pointer value and arguments `(4, 2000, 0)`; the epilogue then pops SP0 into R0, so the local word—not the child result—is the return, subject to helper stack effects. A zero first result instead calls 448F98 and returns the saved entry R7 through POP R0/PC. At 0x47DD8A, a separate frame calls the first wrapper and then returns its own saved R7, discarding the inner return. At 0x47DD92, the pointer word is freshly loaded and tested; nonzero causes a zero store through the second literal pointer before the nested call, while either route returns the outer saved R7. The frames' stack slots are distinct under ordinary local writes.

The external callees and literal ownership remain unresolved. Status remains partial/unaccepted; no source or gate files changed.
