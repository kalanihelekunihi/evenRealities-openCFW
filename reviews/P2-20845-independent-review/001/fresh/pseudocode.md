# Division final quotient remainder and eight-bit stages

Partial/unaccepted;174 instruction bytes. CDE2 inherited20frame: R7zero→CE26. ElseR1 XOR=R0;R6=32-R7;R0=ARM_LSL(R0,R7);R1=ARM_ROR(R1,R6);R1 XOR=R0;R6=UDIV(R1,R3);R1-=R3*R6;UMULL R4low,R5high=R2*R6;SUBS R0,R0,R4;SBCS R1,R1,R5;ifborrow:R6--;ADDS R0,R0,R2;ADCS R1,R1,R3.
CE08:R2=R0 XOR R1;R3=ARM_LSR(R1,LR);R4=32-R7;R2=ARM_ROR(R2,LR);R0=ARM_LSL(IP,R7);R2 XOR=R3;R1=ARM_LSR(IP,R4);R0 OR=R6;POP R4..R7,PC20.
CE26 zeroR7:R2=R0 XOR R1;R3=ARM_LSR(R1,LR);R1=0;R2=ARM_ROR(R2,LR);R0=IP;R2 XOR=R3;POP R4..R7,PC20. ARMregistershiftlow8semantics retained.
CE3A separateentryfromCD68 forunsigneddivisor65536..00FFFFFF,no frame:IP=R1;R1=UDIV(R1,R2);R3=oldR1-R2*R1;R3=(R3<<8)|(R0>>24);IP=UDIV(R3,R2);R3-=R2*IP. AtCE52,CE64,CE76 repeatthree times:R3<<=8;R0=IP|(R0<<8);R3|=R0>>24;IP=UDIV(R3,R2);R3-=R2*IP (lastremainderstore atCE84 usesR2 instead). PreciselyCE84 R2=R3-olddivisor*IP;CE88 R0=IP|(R0<<8);R3=0;BXLR. Four8bitquotientdigits followhighworddivision; retain rollingR0order.
All arithmeticmod32exceptUMULL64,carry/borrowexact. EndsCE90. No C/freeze/wholecompletenessclaim.
