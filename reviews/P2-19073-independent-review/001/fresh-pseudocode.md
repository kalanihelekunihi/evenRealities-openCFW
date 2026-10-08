# Result branches and selector tail 0x468F9E..0x469036

Partial/unaccepted; 152 instruction bytes. Inherit 24-byte frame. R0 is full child 0x4ABCC6 result, R4 overwritten with global address on selector-two path. FULL R0 zero branches 0x468FDE; nonzero follows 0x468FA2.

Nonzero: fresh 0x43D0CE result bit1 enables diagnostic: SP4=literal 0x469154, SP0=581, R3=literal 0x469144, R2=literal 0x4690DC, R1=literal 0x4690E0, R0=4 -> 0x43D574. Independent fresh 0x43D0CE bit0, or conditional third fresh bit2, enables R1=literal 0x469158, R2=R1, R0=0x10000000, live R3 -> 0x43CE9E. Branch 0x469018.

Zero: fresh mask bit1 diagnostic uses SP4=literal 0x46915C, SP0=583, same diagnostic R3/R2/R1 literals, R0=1 -> 0x43D574. Separate fresh bit0 or conditional fresh bit2 enables R1=literal 0x469160, R2=R1, R0=0x04000000, live R3 -> 0x43CE9E. At 0x469018 set R0=0, branch shared return 0x469024.

Entry 0x46901C comes from original FULL selector R4 !=2, so R4 still original R0 and live R0/R1 are original R1/R2. FULL R4==3 calls 0x4A99D0 with live arguments and falls through shared return, retaining child R0 result. At 0x469024 POP R1/R2/R3/R4/R5/PC consumes all 24 bytes; restored R1/R2 may instead contain diagnostic line/context in SP0/SP4. No blanket zero return claim.

FULL selector !=3 reaches 0x469026. FULL selector 4 calls 0x4A9C0C with live arguments, then explicitly R0=0 and shared return. Other selectors compare FULL R4==5: unequal goes directly shared return with live R0 (original R1); equal falls through 0x469036 outside this chunk. Child contracts unresolved; no C or gate claim.
