# P2-20915 independent review

Status: **partial / unaccepted**.

Fresh locked-image replay passed for the 124-byte instruction span 0x47D9FC..0x47DA78. Candidate and fresh instruction, pseudocode, and reference artifacts match; instruction boundaries are contiguous and the described local branches land on the decoded instructions.

At 0x47D9FC, the word at entry R0+12 is loaded once and compared unsigned against 4501; the call is taken only below the threshold, with arguments `(entry R0, 20, 0, live R3)`. The function epilogue pops into R1/PC. At 0x47DA16, the record pointer is loaded from the literal; word0 and word4 guards precede two distinct word12 loads, with the latter compared unsigned against 4501. It then calls the first entry, which performs another independent word12 load/check, and compares the full call result against a fresh word20 load. The zero-return-equals-zero route therefore produces 1. At 0x47DA58, equality of word0 with the literal bypasses writes; otherwise the `(record,4524,0,live R3)` helper call precedes the word8 zero store. `POP {R0,R4,R5,PC}` returns the entry R3 saved slot in R0.

External helper behavior remains unverified. Candidate status is partial/unaccepted; no source or gate files changed.
