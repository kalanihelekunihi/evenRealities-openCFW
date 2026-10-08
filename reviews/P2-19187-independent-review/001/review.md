# Independent review: P2-19187

Status: partial / unaccepted. No source or gate changes.

Fresh replay of `0x46A344..0x46A3D8` (148 bytes) matches candidate instruction and reference records. The two differences use wrapping 32-bit subtraction followed by signed division by 2, and child calls then receive fresh global loads. Subsequent calls use fresh pointers and wrapping sums in the recorded order. The shared epilogue is `LDMIA SP!, {R0,R4-R10,PC}` and returns the word currently at SP0 (the earlier input R3 slot unless overwritten); it does not return the last child result. The adjacent `BX LR` leaf remains separate.
