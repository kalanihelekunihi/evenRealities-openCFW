# Independent review — P2-21421

Status: partial; accepted: false.

Fresh replay passed for the 96-byte range. Regenerated instruction and reference files match the candidate exactly, including byte tiling and PC-relative references.

The preceding list tail increments and stores the global counter, reloads it, stores the count into the node, and restores the frame with R1/R2/R3 loaded from saved entry slots. The new wrapper allocates 92 bytes inside a 32-byte saved-register frame and preserves the allocator result. Its null path stages the line-99 diagnostic arguments into stack slots that overwrite saved entry values, issues the diagnostic, then enters the explicit repeated zero-store loop through 0xFFFFFFFF. The nonnull path copies 16 bytes from the same source pointer to allocation offsets +8 and +24; the second call is beyond the mapped boundary.

Later helper behavior and the allocation/copy contracts remain unresolved. Review remains partial/unaccepted.
