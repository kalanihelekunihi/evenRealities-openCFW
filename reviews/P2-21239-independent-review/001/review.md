# P2-21239 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x482286..0x482348 (194 bytes), and both instruction and reference JSON match the candidate. The short and longer digit paths use signed SXTH comparisons and call 0x439BE4 with the recorded pointer/count/precision arguments; count updates are modulo 32 bits. The separator path updates SP36 independently from SP32, while the other path updates SP32 before writing the separator. Fractional-copy helper arguments include the current count and R4+R11; helper results are not assigned semantic meaning. The shared zero-padding test uses fresh SP64 and ordered fresh stack loads, then a signed width comparison and wrapping subtraction. Continuation at 0x4824AC remains unresolved.
