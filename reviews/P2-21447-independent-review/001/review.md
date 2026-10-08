# Independent review — P2-21447

Status: partial; accepted: false.

Fresh replay passed for the 100-byte range. Regenerated instruction and reference files match the candidate exactly, including tiling and PC-relative references.

The 24-byte frame receives the record, parent, value, and source pointer. It calls the reset helper first, then stores the parent pointer and issues three ordered 16-byte copies from the same source into record offsets +24, +4, and +40, followed by the low-byte store at +20. The owner path freshly reads owner+688 and, when nonnull, calls using owner, record, and a fresh owner+688 callback pointer. Only after that does it test/reload owner+684 and traverse node+76 links using fresh reads before and during advancement.

The continuation, callback contracts, and owner/list semantics remain unresolved. Review remains partial/unaccepted.
