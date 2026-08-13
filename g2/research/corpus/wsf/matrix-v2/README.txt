Scope: stock functions [0x0052a51a,0x0052a542) and [0x0052a542,0x0052a574).
Mapping proven by operand behavior: stock_1 writes a bool_t through argument 0 and returns queue-head ticks at offset 4, so it is the r19.02-style WsfTimerNextExpiration(bool_t *). stock_2 tests queue-head ticks at offset 4, removes an expired timer, clears isStarted at offset 13, and returns it, so it is WsfTimerServiceExpired.
Source candidates use the recovered G2 layout pNext@0,ticks@4,msg@8,handlerId@12,isStarted@13,sizeof=16. Static assertions enforce it.
Configs: Cortex-M55 Thumb, GCC -O2/-Os, inlining disabled, freestanding, no LTO/builtins/unwind, function/data sections, no unaligned access.
Normalization removes absolute addresses, relocation values, call destinations, and branch destinations while retaining opcode, register, immediate, and load/store-offset dataflow shape. Exact normalized equality is intentionally strict.
Qualification: raw object bodies retain unresolved relocations and are not final-link byte candidates. Matches require both exact raw or strict normalized equality; size equality alone is not a match.
