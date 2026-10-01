# Private P2 recovery 1525: AF8 zero-mode wrapper

Candidate runtime span `[0x10000AF8,0x10000B02)`, conditional child offsets `[0xB10,0xB1A)`. The wrapper saves R15, sets R2 to zero, calls 9CC, and restores R15. Its child semantics remain unresolved.

Run `python3 verify.py` in this directory. Four direct callers and their argument/return dataflow are pinned; wrapper fixtures keep 9CC post-state controlled. Adjacent AF4 literal and B02 BKPT are separately recorded.
