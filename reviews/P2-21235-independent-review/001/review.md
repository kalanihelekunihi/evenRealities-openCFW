# P2-21235 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482174..0x482200 (140 bytes); the candidate instruction and reference outputs exactly match the independent replay. The marker paths preserve distinct full-width comparisons and the general-format path uses SXTH(R6), signed comparisons, a fresh SP64 flag-byte read, and a wrapping decrement with a negative clamp. At 0x4821B4 the count is incremented before the postincrement input-byte read and output store; the later separator has a separate count increment and output reload. CMP flags remain live across intervening loads/store. The positive-precision path narrows R6 with SXTH, forwards old count in R3 to 0x439BE4, then reloads SP32 and stores a wrapping sum. Helper semantics and continuation at 0x482200 are unresolved.
