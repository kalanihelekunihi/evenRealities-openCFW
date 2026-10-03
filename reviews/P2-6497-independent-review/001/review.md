# Independent review 6497

Disposition: **PASS_SCOPED**; `accepted:false`.

The packet hashes and FF00..FF84 source span match the locked image. GNU Thumb decoding confirms a 16-byte frame saving R3–R5/LR, low-byte normalization of the mode, and ordered dispatch: modes 1–4 branch to their respective blocks; modes 6, 7, and 9 leave this span for FF84; mode 8 leaves for FFDA; all other low-byte values branch to FFF0.

Each mode 1–4 block truncates the second argument to u8 and normalizes equality-to-1 as R1=1, otherwise R1=0. It calls 4303BC with R0 equal to 129, 125, 128, or 142, respectively, then branches to FFF0 without normalizing the child result in this span. At the direct default branch R0 still contains the low-byte mode.

This review covers only the entry and the four blocks within FF00..FF84; continuation and callee semantics are not claimed.

No canonical files or gates changed.
