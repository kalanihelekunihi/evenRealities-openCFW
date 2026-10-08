# P2-20851 independent review

Status: **partial / unaccepted**.

Fresh replay passed for 70 bytes at 0x47CE90..0x47CED6; image/source hashes and instruction tiling match, and local branches resolve. The 16-byte PUSH frame is overlaid by STRD of the 8-byte template at SP0. Two separate 0x45A568 calls are compared using the full second result; the byte at SP5 is selected as 2 or 1. A fresh global byte read contributes bit 2 to SP6 before the 0x4651E0 call. POP R0/R1/R2/PC returns stack words from SP0/SP4 and saved entry R7 from SP8; the call result in R0 is discarded. Template return words remain subject to possible callee memory writes; no template field contract is inferred.
