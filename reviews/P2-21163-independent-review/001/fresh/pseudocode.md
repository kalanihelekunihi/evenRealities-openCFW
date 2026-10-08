# Three-bank bit query and six-mode direct mask write prefix

Partial/unaccepted;152 instruction bytes480F8A..481022. Framelessquery480F8A:selectorUXTBentryR1;0→tablepointerliteral48174C,1→481750,2→481754,other→return6withoutoutputwrite. Eachvalidmode:wordindex=(fullentryR0>>5)&7;freshword[table+4*wordindex];bitindex=entryR0&31;wordrightshiftbitindex AND1→word[entryR2];return0BXLR. No index224boundorpointerguard;upperindexbitsignored. Preserve tablewordreadbeforeoutputstore.

Routine480FD6 PUSH R2,R3,R4,LR16;R4fullentryR0;selectorUXTBentryR1 dispatch0→480FF2,1→48100A,2→481022,3→481050,4→481068,5→481080,other→4810AC. Modes0/1 usepointerliteral481758/48175C respectively;R1=(R4>>5)&7,R2=1,R4=1<<(R4&31);storefullmaskword[table+4*R1] directly withoutsource read orRMW. Branch4810AC unresolvedcommonreturn. No indexbound,nullcheck,orhelpercallin modes0/1. Othermodes/epilogue require recovery;no C/freeze/fullcoverage/equality claim.
