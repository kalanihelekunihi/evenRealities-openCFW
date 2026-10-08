# Independent review — P2-21363

Status: partial; accepted: false.

Fresh replay passed for the 128-byte range. Regenerated instruction and reference files match the candidate exactly, including byte tiling and PC-relative references.

The t, j, and z paths set their observed flag bits and advance/store the cursor once. The conversion dispatch uses the distinct equality targets shown, with the final u comparison pending beyond the mapped boundary. The map does not establish the behavior of those downstream conversion handlers.

The continuation and conversion behavior outside this slice remain unresolved. No whole-routine coverage or acceptance claim is made.
