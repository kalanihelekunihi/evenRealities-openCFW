# P2-19097 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x469400–0x46949A (154 bytes; 62 instructions); candidate instruction/reference records match exactly. Locked image SHA-256: `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Verified the inverted low-byte write at SP+12 preserves the upper 24 bits, then the shared SP+0 write of 4 and child call. The child result is tested as a full word and is not the return value. Diagnostics can replace SP0 (and therefore returned R0) with 150; POP restores the stack slots, including potentially child-modified data behind the SP+12 pointer. The leaf at 0x469470 compares full R2 in the recorded ordered tree and all exits set R0=1. The intervening BX LR at 0x46946E is a separate leaf.
