# Independent review — P2-21357

Status: partial; accepted: false.

Fresh replay passed for the 126-byte range. Regenerated instruction and reference files match the candidate exactly, including instruction tiling and PC-relative references.

The 88-byte frame accounting (52-byte register save plus 36-byte local allocation), callback selection using the fresh saved argument read, literal-output loop, and repeated cursor reads are reflected in the instruction sequence. The percent path advances/stores the cursor before dispatch, clears the flags register, and applies the observed zero/minus flag-bit updates before the shared unresolved continuation. The callback result is ignored, and the saved stack slots remain live across calls.

This is only the prefix map; several dispatch destinations and the epilogue are unresolved. No whole-routine coverage or acceptance claim is made.
