# P2-19101 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x46949A–0x46951A (128 bytes; 50 instructions); candidate instruction/reference records match exactly against locked image SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Confirmed the full-width guards for R0==4 and nonzero R1/R2, the 32-byte frame, and distinct fresh global-byte reads in each diagnostic route. R4/R5 are narrowed only into temporary registers for stack arguments; neither is truncated in place. Diagnostic SP0–SP16 slots remain separate from the saved-register area, and the snapshot registers stay live into the next chunk.
