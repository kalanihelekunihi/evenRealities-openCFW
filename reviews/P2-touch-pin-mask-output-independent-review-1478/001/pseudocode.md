# Pin mask output helper at 5188

The 52-byte body [5188,51BC) loads three original output words and first stores each with mask bits cleared. For mode bits 2, 1 and 0 respectively, overwrite the corresponding word with its original value OR mask. Higher mode bits do not affect the branch decisions. Preserve input mask in R0 and restore the four-word frame. No calls occur.

The 240 original-instruction fixtures check final words and every ordered store, including zero/full/high-bit masks, independent original words and high mode bits. Physical interpretation and pointer validity remain unresolved. No canonical admission or C implementation.
