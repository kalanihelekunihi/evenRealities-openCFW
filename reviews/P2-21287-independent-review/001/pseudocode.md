# Node unlink endpoint and interior helper sequence

Partial/unaccepted;140 instructionbytes482C0E..482C9A. PUSH{R4,R5,R6,LR}16bytes;R4=descriptorentryR0,R5=nodeentryR1. NullR4 immediatelyPOPretainsR0=0. Otherwisecall482CD8(R0=R4,liveR1/R2/R3). ReturnedR0==R5:call482CF0(R4,R5,liveR2/R3);store returnedR0[R4+4],freshreloadthatfield. Zero→store0[R4+8],returnR0=0. Nonzero→freshreload[R4+4]R1,R2=0,R0=R4,call482DAE liveR3,returnhelperR0.

Unequalfirstendpoint:call482CE4(R0=R4,liveothers). EqualR5:call482CFA(R4,R5,liveR2/R3);store returnedR0[R4+8],freshreload;zero→store0[R4+4],return0;nonzero→freshreload[R4+8]R1,R2=0,R0=R4,call482DC2 liveR3,returnhelperR0.

Unequalboth:call482CFA(R4,R5,liveR2/R3),returnedR0→R6;call482CF0(R4,R5,liveR2/R3),returnedR0→R5(overwritesentrynode). Call482DC2(R4,R6,R5,liveR3),then482DAE(R4,R5,R6,liveR3);returnlasthelperR0. AllpathsPOP{R4,R5,R6,PC}16bytes. No node-null/membershipguard or releasecall inthisrange;helperfieldsemantics unresolved. Preserveexactcalls,freshendpointreads,storeorder and pathdependentreturn. No C,freeze,wholecoverage or equalityclaim.
