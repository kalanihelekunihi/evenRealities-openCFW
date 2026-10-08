# Independent review — P2-21437

Status: partial; accepted: false.

Fresh replay passed for the 96-byte range. Regenerated instruction and reference files match the candidate exactly, including tiling and PC-relative references.

The first wrapper calls the global helper and POPs saved entry R7 into R0, overriding its result. The count-dispatch wrapper compares the global word with one and branches with R3=1 or UXTB(entry R2), preserving the incoming R0/R1/R2 otherwise. The node scan uses a 24-byte frame, checks the fresh head pointer, performs two separate 453604 calls, then rereads the node pointer. Status, signed bound, and signed cursor-difference tests use the recorded signed conditions and wrapping R7 decrement before loading node+12.

Helper contracts and broader list semantics remain unresolved. Review remains partial/unaccepted.
