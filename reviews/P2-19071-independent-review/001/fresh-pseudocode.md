# Selector-two entry 0x468F24..0x468F9E

Partial and unaccepted; 122 instruction bytes. PUSH R1/R2/R3/R4/R5/LR creates a 24-byte frame, with SP0 original R1, SP4 original R2, SP8 original R3. R4=original R0, R0=original R1, R1=original R2, R5=original R3. Compare FULL R4 against 2; unequal branches to 0x46901C outside this chunk.

Equal-two path calls 0x43D0CE with live R0/R1/R2/R3. If result bit1 is set: SP4=word literal 0x469140; SP0=571; R3=literal 0x469144; R2=literal 0x4690DC; R1=literal 0x4690E0; R0=4; call 0x43D574. Then call 0x43D0CE afresh. If this result bit0 is set, or otherwise a third fresh call has bit2 set: R1=literal 0x469148; R2=R1; R0=0x10000000; call 0x43CE9E with live R3. These calls and fresh reads are distinct.

At 0x468F6C: R0=0; R1=literal 0x469124; store word zero at [R1]. Call 0x46801E with live arguments and discard its return by setting R0=R5; call 0x4ABA58 with original R3 and live other arguments. Load R0=word at address stored in literal 0x469118. R1=literal 0x46914C; store that freshly read word at [R1+4]. Call 0x45A568 with live arguments. FULL result unequal to 1 branches to 0x469018 outside this chunk.

FULL result 1: R1=3; R2=0; R4=literal 0x469100; R0=R4; call 0x43C0E4 with live R3. Then R0=literal 0x469150; call 0x4ABCC6 with live R1/R2/R3. Its full result and inherited R4/global address are live at 0x468F9E for the next chunk. No memory-fill or lookup contract is inferred for these children. No C, runtime, completeness, or gate claim.
