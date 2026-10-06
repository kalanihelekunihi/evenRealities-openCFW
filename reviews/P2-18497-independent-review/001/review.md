# Independent review P2-18497

Status: partial, unaccepted. No source or gate changes.

Fresh GNU replay confirms the 92-byte prefix `0x460638..0x460694`; instruction/reference manifests match. The function pushes R4-R9/LR (28 bytes), reserves 36 local bytes, and therefore has a total 64-byte frame with saved R4-R9/LR starting at SP+36. Incoming R0/R1/R2 are retained in R4/R6/R5.

The first diagnostic uses live incoming arguments and tests bit 1. Its set path writes retained R5 at SP8, a literal to SP4, and 386 to SP0, then calls `0x43D574`; these are locals, not saved-register slots. Bit-1-clear continues with separate fresh `0x43D0CE` calls for bit 0 and conditionally bit 2. The bit-2 route calls `0x43CE9E` with the shown arguments. The other route calls `0x460178` without rebuilding arguments, then tests the full child result against exactly 4; non-equal branches to external `0x460746`, while exact 4 continues outside this map.

The call at 0x460178 is the previously mapped lazy initializer, but its result/side effects are not reinterpreted here. Remaining mode branches and epilogue are outside the span; partial/unaccepted only.
