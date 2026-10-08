# Word divisor normalization and fifteen-bit quotient stage

Partial/unaccepted;122instructionbytes. CD68 entryR3zero fromearlierpath,R2>=65536. UnsignedR2<01000000→pendingCE3A beforeframe. OtherwisePUSH R4..R7,LR20;R7=CLZ(R2),R4=CLZ(R1),R6=15-R7,R5=R7-R4;R3=ARM_LSR(R2,R6),LR=R7+17,R2=ARM_ROR(R2,R6),R5+=32,R2 XOR=R3;SUBS R7,R5,15;unsigned<=→CD04 earliermappedcontinuation,20frame maintained.
CD92 alsoenteredfromearlierCCD2 normalizationwith20frame: R1 XOR=R0;R6=32-R4;R0=ARM_LSL(R0,R4);R1=ARM_ROR(R1,R6);R1 XOR=R0. IP=UDIV(R1,R3);R1-=R3*IP;UMULL R4low,R5high=R2*IP;SUBS R0,R0,R4;SBCS R1,R1,R5;ifborrow:IP--;ADDS R0,R0,R2;ADCS R1,R1,R3.
CDB8 unsignedR7<15→pendingCDE2. OtherwiseR7-=15;R1=(R1<<15)|(R0logicalright17);R6=UDIV(R1,R3);R1-=R3*R6;UMULL R4low,R5high=R2*R6;RSBS R0,R4,R0LSL15 computes(oldR0<<15)-R4;SBCS R1,R1,R5;ifborrow:R6--;ADDS R0,R0,R2;ADCS R1,R1,R3. CDDE IP=R6|(IP<<15);fallthroughpendingCDE2.
Arithmeticmod32exceptUMULL64,ARMregistershiftlow8semantics,carry/borrowexact. Shared20frame stilllive. No arithmeticcompleteness/C/freezeclaim.
