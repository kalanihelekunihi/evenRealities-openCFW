# Fixed helper wrappers and exact parser end-pointer acceptance

Partial/unaccepted;124instructionbytes47DDFE..47DE7A,threeentries.
DDFE PUSH R7,LR8;4D34C4(entryR0,12,0,liveR3);POP R1,PC returns fullhelperR0 andR1=savedentryR7.
DE0A PUSH R7,LR8;R3=entryR2,R2=literal47E294;44B728(entryR0,entryR1,literal,entryR2). POP R0,PC returns savedentryR7,discardingformatterresult.
DE18 PUSH R2,R3,R4,R5,R6,LR24;R4=entryR0,R5=entryR1.44A43C(R4,liveargs)→R6 fullresult. UnsignedR6<8→failure0. Otherwise44B610(R4,address47E084,3,liveR3);fullnonzero→failure0. Otherwise46CACC((R4+R6-4)modulo2^32,literal47E298,liveR2,R3);fullnonzero→failure0.
ThenSP0=0;48D874(R4+3 modulo2^32,SP,10,liveR3);fullreturnedvalue→R1. FirstfreshSP0 mustnonzero; otherwisefailure0. SecondindependentSP0 mustequal(R4+R6-4)modulo2^32;otherwisefailure0. EqualitystoresfullR1 toword[entryR1] thenR0=1. No recovered nulloutputcheck, numericrangecheck or localparseroverflowguard. HelpersmaymodifySP0, and firstnonzerotest mustnot collapse withsecondload. POP R1,R2,R4,R5,R6,PC24: R1=SP0 (savedentryR2 onearlyfailure orparserlocal),R2=savedentryR3 subjecttocallee memoryeffects;R4..6restored. No string/API semantics inferred from unrecoveredhelpers; no C/freeze/completenessclaim.
