# Independent review 6401

Disposition: **PASS_SCOPED**; `accepted:false`.

The locked bytes, declared body digest, and packet file hashes match. GNU Thumb decoding confirms the E53C entry's 16-byte frame saving R2/R3/R4/LR. The first global slot is freshly read before and after the create call 416816(15, 8, literal). A still-zero result stages diagnostic tag 88 at SP0 and a literal at SP4, overwriting the saved R2/R3 slots; diagnostic return does not prevent the second create sequence. At E57A, a distinct global slot is freshly checked and, if zero, 4163B2 receives the computed ADR target, zero, zero, and the fourth literal argument. The ADR at E58C uses aligned PC 0x42E590 plus 0x165, producing Thumb target 0x42E6F5. Its still-zero path stages tag 97 and a different literal, then joins E5BA regardless of the diagnostic result.

The frame's overwritten saved argument slots are material to its continuation and are not presumed restored as original values. This review validates source-level sequencing and argument placement only; it does not infer callee/API meaning or make C/admission claims. No canonical files or gates changed.
