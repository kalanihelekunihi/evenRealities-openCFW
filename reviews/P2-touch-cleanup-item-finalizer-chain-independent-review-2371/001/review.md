# Independent review 2371

**Result:** PASS_SCOPED.

Receipt 01f90816e8c0704c6a7b137e1d01176b5cb37e5d6ea52d066ec4063ee2b2a727 pins the source and four contiguous bodies [0x4DB8,0x4DC4), [0x4DC4,0x4DEC), [0x4DEC,0x4E1C), [0x4E1C,0x4E36); combined code hash and evidence pins match. Isolated replay passes 324 cases.

All four bodies execute original instructions with no function interception. The top-level dispatch descends 2,1,0. Type7 skips its row; other rows capture count and dispatch items descending, while 4DC4 executes exactly one 4DB8 leaf for each item. The leaf store order is byte+8 zero, halfword0 copied to halfword+2, byte+7 zero. The oracle agrees with the complete ordered write ledger and full supplied memory.

The fixtures cover rotated types/counts, four halfword values and three byte fills; exact row/item arguments, R4-R11/SP and dispatch order pass. No mismatches were found.

**Limits:** Counts and pointers are stable in the fixtures; changing-count/pointer behavior and aliasing are unresolved. All allocations are distinct synthetic memory; no physical meaning is inferred. R0 is incidental, not a general return contract. Private evidence only; accepted:false.
