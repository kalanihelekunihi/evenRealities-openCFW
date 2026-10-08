# Nonnull node insertion with ordered link-helper sequence

Partial/unaccepted;116 instructionbytes482B56..482BCA. PUSH{R3,R4,R5,R6,R7,LR}24bytes;R6=entryR0descriptor,R5=entryR1node. IfeitherfullpointerzeroR0=0→return482BC8. Otherwisecall482CD8(R0=R6,liveR1/R2/R3);returnedR0==R5:call482B12(R0=R6,liveothers);R4=returnedR0;ifzeroR0=0return,else482BC6R0=R4return.

Unequal path freshword[R6]→R0,+8mod,call44F718 liveR1/R2/R3;returnedR0→R4;zero→return0. Nonzero call482CFA(R0=R6,R1=R5,liveR2/R3);returnedR0→R7. Orderedcalls, liveR3 each:482DC2(R6,R7,R4);482DAE(R6,R4,R7);482DAE(R6,R5,R4);482DC2(R6,R4,R5). No membership/nullguard onreturnedR7 inthisrange. FinallyR0=R4;POP{R1,R4,R5,R6,R7,PC}24bytes,R1=savedentryR3. Preserveexacthelperregisterflow withoutunprovedlinkfieldsemantics,comparisonhelperclobberboundary and allocationfailurepath. No C,freeze,wholecoverage or equalityclaim.
