# Two-word nonzero high divisor normalization and correction

Partial/unaccepted;150 instruction bytes. CCD2 CMP R0,R2 thenSBCS IP,R1,R3;carryzero→CCC8 zeroquotient/originalremainder. ElseunsignedR3>=65536→CD40.
Lowhighwordpath:PUSH R4..R7,LR20;R7=CLZ(R3),R4=CLZ(R1),LR=R7-15,R5=R7-R4;R3 XOR=R2;R6=32-LR;R2=ARM_LSL(R2,LR);R3=ARM_ROR(R3,R6);R3 XOR=R2. SUBS R7,R5,15;unsignedHI→pendingCD92 (20frame remains).
OtherwiseR4-=15;R4+=R5;R1 XOR=R0;R6=32-R4;R0=ARM_LSL(R0,R4);R1=ARM_ROR(R1,R6);R1 XOR=R0. R6=UDIV(R1,R3);R1-=R3*R6;UMULL R4low,R5high=R2*R6. SUBS R0,R0,R4;SBCS R1,R1,R5;carryone→CD2C;elseR6--;ADDS R0,R0,R2;ADCS R1,R1,R3.
CD2C:R2=R0 XOR R1;R3=ARM_LSR(R1,LR);R2=ARM_ROR(R2,LR);R1=0;R2 XOR=R3;R0=R6;POP R4..R7,PC20. Use ARM register-shift semantics including low8 count; no host maskedshift substitution.
CD40:PUSH R4,R5 8;IP=UDIV(R1,R3);R1-=R3*IP;UMULL R4low,R5high=R2*IP;SUBS R0,R0,R4;SBCS R1,R1,R5;carryone→CD5C;elseIP--;ADDS R0,R0,R2;ADCS R1,R1,R3. CD5C POP R4,R5;R2=R0,R3=R1,R0=IP,R1=0;BXLR.
All arithmeticmod32 exceptUMULL64;borrow/carry retainedexactly. PendingCD92 continuation andCD68 entry remain. No C/freeze/completenessclaim.
