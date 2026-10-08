# P2-21129 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x4807A0..0x4807F0 (80 bytes); instruction and literal-reference outputs match candidate. VCVT.F32.U32 and fixed-point VCVT.U32.F32,#5 were retained as architectural floating conversions; no algebraic simplification was applied. The fresh predicate chooses threshold 15 or 24, and the unsigned compare conditionally calls absolute address 0x40 with the recorded live arguments. That target is outside the locked image, so its behavior remains unresolved. The final POP returns saved entry R7 through R0.
