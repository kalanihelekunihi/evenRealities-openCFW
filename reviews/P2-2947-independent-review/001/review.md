# Independent review 2947/001

**PASS_SCOPED**; `accepted` remains false.

I reran all 4,608 original caller-prefix/decoder fixtures into a fresh directory. The source hash and both body digests match the locked flash image. The original caller setup supplies the record at entry SP+4 and output words at SP and SP+24; the decoder’s ordered writes/status pass, as do R1/R2/R4/R5, SP, PRIMASK, and the stop at 0x42BCF0 before caller postprocessing. All candidate and isolated replay output hashes match their receipts.

This is not evidence for the caller’s later postprocessing or its complete gate/publication behavior.

Candidate receipt SHA-256: `e6c5a69c89494a8068fabb451689b87365b2c4b5c40146e3feb00e8e12a47864`.
