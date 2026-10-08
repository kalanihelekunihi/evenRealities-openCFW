# P2-20963 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for the 198-byte span 0x47E320..0x47E3E6. Candidate and fresh instruction, pseudocode, and reference artifacts match exactly.

The 40-byte frame saves the full request value in R5, then applies three full-result gates: 4487AC must equal 1 to continue; 443484 must be nonzero; 4434D0(16, live args) must equal 1. The template's three words are copied into SP12/16/20, while SP16 is then replaced by the request's LOW8 as a full word. 4A8368 receives `(0, SP+12, live R2, live R3)` and its full result selects success or error diagnostics.

Each diagnostics arm has separate calls to 43D0CE: first for bit1 and, after any optional first logger call, another for bit0, then potentially a third for bit2. Stack logger tuples use constants 81 or 83 and literal arguments; the mask logger uses masks 0x10400000 or 0x04400000 and a destructively narrowed LOW8 request in R3. Neither arm explicitly normalizes R0: it returns the last helper/logger result live. SP+=28 discards 24 local bytes plus saved entry R3, then POP restores R4/R5/PC. Helper results, stack writes, and status observations are not collapsed.

Candidate remains partial/unaccepted; no source or gate files changed.
