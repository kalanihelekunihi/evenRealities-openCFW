# Independent review 2423

**Result:** PASS_SCOPED.

Candidate 002 receipt hash 9e1d52d3914d8893db6ac86824d5af1042940e954154cce890c021814735f077; source SHA-256 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches the pinned value. Original body [0x752E,0x757E) hashes to the receipt value; disassembly and candidate artifacts match their file hashes.

Isolated replay of 002 passes 108 fixtures; the replay output exactly matches pinned replays.json. The corrected prose accurately states 108 cases. Earlier attempt 001 is preserved and its 216-case prose count was inaccurate.

Instruction trace supports the mutable-bound behavior: R4 is initialized from original halfword 128 and is incremented after each child; after every child the code reloads halfwords 128 and 130, adds them, and compares the sum against R4. It therefore continues from the original slot after mutation, while R8 retains the kind-derived selector captured before the loop. The controlled child mutates both bounds and the row kind on the first call; exact subsequent args, call count/status and R4-R11/SP pass.

**Limits:** Only the supplied two initial kinds, three start values, three replacement starts, four replacement counts and two replacement kinds are covered; child behavior is controlled. Row pointer replacement, actual measurement behavior, aliasing and broader caller interaction remain unresolved. Private evidence only; accepted:false.
