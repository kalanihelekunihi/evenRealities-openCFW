# Independent review — P2-21419

Status: partial; accepted: false.

Fresh replay passed for the 96-byte range. Regenerated instruction and reference files match the candidate exactly, including byte tiling and PC-relative references.

Both short wrappers restore their saved entry R7 into R0, overriding helper return values. The allocation-failure diagnostic path writes its three literal arguments into stack slots that alias saved registers before issuing the observed diagnostic call with its literal and scalar arguments. The failure loop performs an actual repeated store of zero through address 0xFFFFFFFF; this is recorded as recovered instruction behavior, without inferring exception handling. On the nonnull path, the head link at offset 316 is freshly loaded and exchanged with the new object, followed by a separate fresh read at offset 320.

The final continuation, external helper contracts, and pointer target contents remain unresolved. Review remains partial/unaccepted.
