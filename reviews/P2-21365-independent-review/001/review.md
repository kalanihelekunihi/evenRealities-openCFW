# Independent review — P2-21365

Status: partial; accepted: false.

Fresh replay passed for the 126-byte range. Regenerated instructions and references match the candidate exactly, including tiling and PC-relative targets.

The pending u dispatch reaches the shown x/X test before the integer parsing arm. The integer radix selection preserves the separate x/p/o/b/default tests and the observed flag updates. Pointer p/P selection sets the pointer-related flags, then consumes a following uppercase V only when that fresh byte comparison matches; subsequent X/P suffix checks reread the cursor byte rather than reusing an earlier observation.

Several branches continue outside this mapped slice. No downstream conversion behavior or whole-routine coverage is inferred.
