# Independent review 6521

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet hashes and 430502..43057C source span match the locked image. GNU decoding confirms a 24-byte saved-register frame, status/index initialization, and an initial branch to 43057C outside this map. The body processes `base + 16*index`: it first calls 42C4C6 with the record word and its +4 address, ignoring the result. It then independently refetches the record's +8 pointer and loads its +8 field into R1, refetches the pointer again for its +0 field in R0, and calls 41D92C; a nonzero return branches to 4305BC. A later pair of fresh pointer loads supplies +12 in R1 and +4 in R0 to another 41D92C call, whose nonzero result branches to 4305C0.

On zero statuses, it calls 42C988 with (fresh record+4, 0, 0), then 42CC34 with (fresh record+4, fresh record+12), then 42C538 with fresh record+4. The last result is retained in R6; 43048E receives the low byte of the current index and its return is ignored. The index increments before the loop joins 43057C. No success of earlier setup/acquire steps is assumed.

This is a local body map only; external child semantics and the later loop/cleanup logic are outside scope.

No canonical files or gates changed.
