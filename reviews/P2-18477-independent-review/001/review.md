# Independent review P2-18477

Status: partial, unaccepted. No source or gate changes.

Fresh GNU ARM replay confirms the 48-byte span `0x460344..0x460374`, with instruction and PC-reference manifests matching the candidate. The first function loads the ring-base literal, then makes three ordered zero halfword stores at offsets 256, 258, and 260. Those stores precede a call to `0x43C0E4` with R0=ring base, R1=256, R2=0, and incoming R3 still live. The child’s full R0 is returned through POP R4/PC.

The following leaf zero-extends the low byte of incoming R0, loads the literal global base, and stores that zero-extended value as a full word at base+12; it returns the normalized R0. Other than R1, it leaves the remaining registers unchanged. The distinction between byte normalization and word-width storage is confirmed by UXTB followed by STR.

Child memory semantics, global ownership, and broader coverage remain unresolved. No source, gate, or admission changes.
