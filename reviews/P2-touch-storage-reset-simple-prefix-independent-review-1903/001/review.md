# Independent review 1903 — storage reset simple-mode prefix

**Result: PASS_SCOPED.** Candidate `touch-storage-reset-simple-prefix-1896/002`; receipt SHA-256 `a5afec8059fac78d638df54ecd0fd2412bff4df7d166c71f8013929dc2caca8a`.

Candidate receipt binds source hash and exact prefix [0x8AE0,0x8B3E), 94 bytes/44 instructions, body hash a2a0e7f5e1520bb7158550ba028219eb5c5a0da41b711eb59d9f9b368b322549. Isolated replay passes all 24 fixtures and byte-matches candidate output.

The decoded prefix multiplies the count and copy byte, clears the requested scratch span with original A9D4, then tests mode. The tested nonzero-mode path computes wrapped product×span minus one, divides by fresh context capacity, adds one, and iterates from context+16 using a fresh capacity load rounded down to a multiple of four for stepping. Controlled 890C return values are examined after every call; the first nonzero is retained while the loop continues. The body branches to 8BE6 for the shared epilogue, outside the owned prefix.

Mode zero, zero dimensions/capacity, callback mutation, and physical storage are outside the fixture scope; 890C is controlled. Shared epilogue execution does not expand the prefix ownership span. No canonical admission.
