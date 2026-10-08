# Independent review — P2-21451

Status: partial; accepted: false.

Fresh replay passed for the 64-byte range. Regenerated instruction and reference files match the candidate exactly, including tiling and PC-relative references.

The zero-resource path writes the diagnostic pointer at SP0, overwriting the saved entry R3 slot, calls line 471, and returns zero. The nonzero path adds the previously computed product to a freshly loaded global+324 word with 32-bit wrap and stores it. A fresh byte read at record+20 gates the clear helper, whose arguments are a fresh record word and zero. The final resource+16 value is freshly loaded for R0 before POP restores saved entry R3 into R1. The existing-resource path joins the POP after loading resource+16, skipping the count update and conditional clear.

External helper semantics remain unresolved; review remains partial/unaccepted.
