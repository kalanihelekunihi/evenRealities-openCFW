# P2-20861 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 86 bytes at 0x47CF60..0x47CFB6; image/source hashes and instruction tiling match. PUSH24 plus 16 local bytes yields a 40-byte frame. Full entry R1/R2 are kept in R5/R7; entry R0 is not captured in this prefix. Diagnostic arguments are written to local SP0..12, with distinct status calls and the mask path using 0x10800000. No pointer validation, length limit, copy, or loop behavior is inferred beyond this slice; execution continues at 0x47CFB6.
