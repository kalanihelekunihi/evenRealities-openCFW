# Independent review — P2-21445

Status: partial; accepted: false.

Fresh replay passed for the 102-byte range. Regenerated instruction and reference files match the candidate exactly, including tiling and PC-relative references.

The routine saves eight registers in a 32-byte frame and requests an 88-byte allocation. Its null path writes the diagnostic arguments into stack slots that alias saved entry registers, invokes diagnostic line 399, and enters the explicit repeated zero-store loop through 0xFFFFFFFF. The nonnull path includes a redundant second null guard. It then calls 0x4847C4 with R0=new record, R1=parent, R2=UXTB(entry R6), and R3=entry R7. If parent is nonnull, it copies byte +56 first, then performs the unaligned word copy at +57. The normal path returns the allocation and restores entry arguments through POP.

The initializer implementation at 0x4847C4 and allocation contract are outside this map. Review remains partial/unaccepted.
