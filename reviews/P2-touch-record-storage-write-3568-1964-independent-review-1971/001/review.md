# Independent review 1971

**Result:** PASS_SCOPED. The candidate’s exact source and artifact pins match, and the isolated replay agrees with its recorded evidence.

- Recomputed every receipt file hash and source hash; all match.
- Independently decoded [0x3568,0x35A4): 60 bytes / 29 Thumb instructions, with the three literal words outside the body.
- Isolated replay executed 108 original-instruction fixtures; generated replay rows match the candidate exactly.
- The instruction order supports null-data rejection, wrapped unsigned end check, enable-byte gate, 8AAC dispatch, and the two accepted status values returning zero; remaining dispatch statuses normalize to 3.

**Limits:** 8AAC is controlled, so downstream write/physical-storage behavior is not established. No canonical admission is made.
