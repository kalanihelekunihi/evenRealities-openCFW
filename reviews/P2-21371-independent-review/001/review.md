# Independent review — P2-21371

Status: partial; accepted: false.

Fresh replay passed for the 128-byte range. Regenerated instruction and reference files match the candidate exactly, including byte tiling and PC-relative references.

The ordinary signed-word path and shared output staging preserve sign detection, wrapping magnitude handling, ordered stack writes, and the helper arguments. The recursive V path follows the pointer chain shown, loads the recursive first stack argument, derives the two cursor-relative values from fresh stack reads, invokes the same callback context recursively, and adds the recursive result to R6 with wrapping arithmetic. The unsigned-wide prefix aligns the argument pointer to eight bytes and loads the pair before staging flags.

This is a prefix only; later argument handling and return behavior are unresolved. No broader ABI or full-routine claim is made.
