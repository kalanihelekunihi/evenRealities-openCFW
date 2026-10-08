# P2-20933 independent review

Status: **partial / unaccepted**.

Fresh replay against the locked image passed for 82 bytes at 0x47DDAC..0x47DDFE. Candidate and fresh instruction, pseudocode, and reference artifacts match exactly.

The first 443484 result is compared full-width to zero. Nonzero writes zero to SP0 and calls 47E7B0 with `(fresh pointer word, 4, 2000, 0)`; the final POP R0 returns SP0, subject to callee stack effects. If the first result is zero, the code calls 48EB90 and tests that full result. A zero second result skips the count logic and returns saved entry R7. A nonzero second result loads the counter pointer, reads its word, and applies a signed `>=10` guard. Values with the sign bit set therefore pass this comparison. Below the guard, it independently reloads the counter, increments modulo 2^32, stores it, writes zero to SP0, and calls 47E7B0 with `(fresh pointer word, 4, 5000, 0)`. There is no second guard on the increment-source read. All paths converge on POP R0/PC; helper returns are not returned directly.

External helper behavior remains unresolved. Candidate status is partial/unaccepted; no source or gate files changed.
