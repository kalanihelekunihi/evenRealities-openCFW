# Boot startup memory ambient return correction

Locked stock SHA-256: `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

Native 0x41bbd0 has a five-byte memory descriptor in R0 and an ambient R1. Its entry pushes `{r1,r2,r3,r4,r5,r6,r7,r8,r9,lr}`; every exit uses `ldmia.w sp!,{r1,r2,r3,r4,r5,r6,r7,r8,r9,pc}` at 0x41bd76. Therefore R1 at return is always the incoming R1. The decompiler's local high-word changes are overwritten by this epilogue. The source C body previously returned only a uint32_t status, which left R1 unspecified.

A named Thumb entry now forwards raw R0/R1 to a typed C core. The core preserves the existing authored descriptor/MMIO/status algorithm and returns `((uint64_t)ambient_r1 << 32) | status` on every exit. The source header and integrated startup child declaration use the 64-bit return. Native literal-pool pointers at 0x41c49c..0x41c4b0 and 0x41c860 map to the selected 0x200271a7 and 0x40021018/0x40020284/0x40021014/0x40021008/0x40021004/0x4002101c addresses.

The earlier `boot-coplacement-memory-return-round` initially followed the decompiler's high=1 branch and is superseded. Corrected `boot-coplacement-memory-ambient-round/receipt.json` is terminal `PASS_BOUNDED_LINK`: 372 selected C/ASM units, 1,009 providers, three genuine ROM imports, 34 callback relocations, 158,612 candidate file bytes versus 148,599 stock. This qualifies source ABI/build only; complete original/source runtime equality and final layout remain open. The conservative direct-root header-only proof backlog is 181 of 654; whole 903-entry catalogue has 279. Runtime-installed/indirect roots and three ROM contracts remain separate gates.
