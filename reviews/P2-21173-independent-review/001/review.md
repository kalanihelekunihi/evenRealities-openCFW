# P2-21173 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4812F6..0x481364 (110 bytes); instruction and literal-reference outputs match. PUSH 24 plus SUB SP,32 establishes a 56-byte frame. The loop writes seven 0xFFFFFFFF words at SP+4 through SP+28 before the 473940 helper call (R0=7, R1=0xFFFFFFFF, R2=SP+4, R3 live); the full helper result is stored at SP0. Only after the helper does UXTB bank selection choose the path. For bank byte zero, a zero mask-enable skips the snapshot; nonzero performs seven ordered, independent literal-pointer word reads and stack stores. There are no output writes or atomic-snapshot guarantees in this prefix, and continuation/unwind remain unresolved.
