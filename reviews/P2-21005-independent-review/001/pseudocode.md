# Guarded object reads and negative-code stack message forwarding

Partial/unaccepted;118instructionbytes47EAF6..47EB6C,threeentries.
EAF6 PUSH R4,LR8;R4=entryR0. FullentryR0zero→5FA0A4(liveargs),ifreturnsstoreword0toFFFFFFFFthenEB0Aselfloopifstorecompletes. Nonzero→4420D0(liveargs),freshunsignedbyteobject40bit0→R4boolean0/1;4420E8(liveargs);R0=R4returns,discardunlockhelperresult. POP R4,PC restoresentryR4.
EB26 same8frame/nullfatalcall/write/selfloopEB3A. Nonzero→4420D0(liveargs),freshwordobject28→R4;4420E8(liveargs);R0=R4fullwordreturns. No otherobjectfieldwrites.
EB4A PUSH R0,R1,R2,R3,R4,LR24;R4=entryR3;SP0=FFFFFFFE(-2)overwritessavedentryR0;SP4=entryR0,SP8=entryR1,SP12=entryR2.441952(freshword[pointerliteralEB6C],SP,entryR3,0). SP+=16discardsfourmessagewords;POP R4,PC8 restoresentryR4. Returnfull441952R0,nostackmessagewordaliasreturn. No queueownership/helpersemanticsinferred;orderedwritesretained. No C/freeze/completenessclaim.
