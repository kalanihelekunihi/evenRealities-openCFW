# Independent review 6395

Disposition: **PASS_SCOPED**; `accepted:false`.

The receipt's packet hashes and E3E0..E458 source bytes match. GNU Thumb decoding confirms three distinct entries. E3E0 saves R0-R4/LR (24 bytes), waits by calling 4162C4(0x00800000, 1, 0xFFFFFFFF) and repeating until the returned word's bit 23 is set, then stages the input's low byte, a literal, and tag 299 for diagnostic 4176CE. POP restores the staged saved-register slots as return values: R0=299, R1=literal, R2=low byte, R3=incoming R3, with R4 restored.

E412 uses the same frame, stages tag 313 and the low input byte, then computes `1 << low8(input)` using the Thumb register-shift semantics (shift amounts at least 32 yield zero). It freshly loads the handle from the literal-backed global at +0x1C, calls 41652E(handle, mask), and returns the staged R0-R3 values through POP while restoring R4. E444 saves R7/LR, computes the same low-byte shift mask, freshly loads the same handle slot, calls 41652E, and POP {R0,PC} returns incoming R7 in R0.

The review covers only local instruction flow, stack aliases, and raw child arguments. It does not claim child meaning or hardware/runtime behavior; no canonical files or gates changed.
