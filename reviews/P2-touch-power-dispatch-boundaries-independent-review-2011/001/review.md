# Independent review 2011

**Result:** PASS_SCOPED.

- Source and artifact receipt pins match.
- Isolated replay reproduced all 32 boundary rows exactly. Invalid index reaches the original BKPT at A450; valid indices with mode 0/3 reach the BKPT at A462; the harness stops before assertion continuation.
- Null heads in modes 1/2/4 return zero. Mode 8 and aliases 0x101/0x102 reach the word read at A47C using null-head + 20; the harness stops at that read rather than assigning fault or safe-return semantics.

**Limits:** This is only the listed boundary set. BKPT continuation, memory-fault behavior, cycles, and arbitrary callback effects are unresolved. No canonical admission is made.
