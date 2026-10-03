# Independent review 6367

Disposition: **PASS_SCOPED**; `accepted:false`.

The 0x42DE58–0x42DEBA body hash and packet files match the locked source. GNU Thumb decoding confirms a 32-byte saved-register area plus 56 local bytes (88 total). It sets R4 to SP+16 and calls 0x41560C(R4, 40, 0), ignoring the result, then branches to 0x42DE9E. That path freshly loads a global record at offset 12 and calls 0x416920(record, SP16, 0, 0). A nonzero return branches outside this extent to 0x42E0FE; a zero return checks the fresh word at SP16 and branches to 0x42E092 unless it equals 1. The remaining continuation is outside this packet.

At 0x42DE6C, the routine freshly tests the word at R4. If nonzero it rereads it, calls 0x415446, then stores zero. It stages values from R10/R8, a literal and tag 532 for 0x4176CE; ignores that result; calls 0x42DE0E and ignores that result. Caller-register values from paths outside this extent are not inferred. The code then rejoins the request at 0x42DE9E.

No retry completion, return behavior, child purpose, hardware/runtime, C-equivalence, or admission is claimed. No canonical files or gates changed.
