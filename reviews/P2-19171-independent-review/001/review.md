# Independent review: P2-19171

Status: partial / unaccepted. No source or gate changes.

Fresh replay of `0x46A0CC..0x46A12C` (96 bytes) matches candidate instruction and reference records. The selector test is full-width 69. Diagnostic paths use separate fresh mask reads and preserve the listed stack-slot writes. The later mode test is also full-width; result 2 sets R0=1 directly, while other results forward the full selector in R0 and the saved original R3 from R5 in R1 to `0x469E66`, retaining live R2/R3. Both routes reach the explicit R0=1 result.
