# List counter return and 92-byte allocation copy prefix

Partial/unaccepted;96 instructionbytes4843E0..484440. Continuation48439816Bframe: R2++wrap,storeword[globalR1+320];freshreloadsamewordR1;storeword[nodeR0+8]=R1;POP R1/R2/R3/PCloadsentryR5/R6/R7aliases(replacedondiagpathwhichneverreturnsnormally),release16B;R0node retained.

New4843EEPUSH entryR0/R1/R2/R3/R4/R5/R6/LR32B;R5=entry0,R6=entry1;R0=92;44F730(liveR1/R2/R3);R4=result. Nullordereddiagstackliteral4849AC→SP8(savedentryR2),4849C0→SP4(savedentryR1),4849B4→SP0(savedentryR0);R3=word4849C4,R2=99,R1=word4849BC,R0=3;44D25C;thenR0=0,R1=FFFFFFFF,word[R1]=0repeatloop484422. NonnullR0=R4+8,R1=R6,R2=16;439C04;R0=R4+24,R1=R6,R2=16 staged,nextcallpending484440. Exactdiagnosticline99 andsame sourcepointerforbothcopiesretained. No C,freeze,wholecoverage or equalityclaim.
