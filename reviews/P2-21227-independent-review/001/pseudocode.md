# Decimal float eight-digit backward pair-store loop

Partial/unaccepted;106 instruction bytes481FD6..482040. Continues481836232frame,R4/R5workingpair,R6cursor,R7budget. Call4D4338(R0R4,R1R5,liveR2/R3);R1=fullreturnR0integercopy,R2=R1;R3=cursor+8,R0paircounter4. Fouriterations: R6=unsignedR2/10;LR=5*R6;R2=R2-2*LRmod2^32;R2+=48;storelowbyte[R3-1]withoutwriteback. R2=unsignedR6/10;LR=5*R2;R6=R6-2*LRmod2^32;R6+=48;R0--;predecrementR3by2storelowbyteR6;repeatcounter!=0. ExactlyeightASCIIdecimaldigitsstoredbackwards,reusingquotientR2;R1integercopyretained. LRusedscratch,butroutineLRsavedentryframe.

R7-=8mod2^32;R6=R3+8;ifsignedR7<=0 branch481FD2rechecksbudgetthen482040. Ifpositive:R0=R1integercopy;call4D4346 withliveR1/R2/R3;returnedpair→R2/R3;R0/R1workingR4/R5;call4D4314;R2=0,R3literal48267C;call4D4354 withpriorreturnedR0/R1;returnpair→R4/R5;repeat481FD6. Exacthelperdependencies/registerlivenessretained;nounboundedinteger/double-librarysubstitution,C/freeze/fullcoverage/equality claim.
