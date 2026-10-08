# Independent review — P2-21361

Status: partial; accepted: false.

Fresh replay passed for the 128-byte range. Regenerated instruction and reference files match the candidate exactly, including byte tiling and PC-relative references.

The precision prefix distinguishes digit parsing from star precision. Star consumes a full argument word, advances the argument cursor by four, and clamps signed values below one to zero while retaining the precision-present flag. The h/l paths perform fresh cursor reads and preserve the separate doubled h/l flag bits; hh completes with the pending cursor store at the boundary.

The continuation and conversion behavior outside this slice remain unresolved. No whole-routine coverage or acceptance claim is made.
