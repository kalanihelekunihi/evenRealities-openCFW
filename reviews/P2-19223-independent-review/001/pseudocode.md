# State two subpaths 0x46A8C0..0x46A940

Partial/unaccepted;128instructionbytes. Inherit24frame, stateword46B00C previouslyFULL2, secondstateword46AE98 previouslyzero onfallthrough. Fresh43D0CE bit1set:literal46B060SP4(overwrites savedR4),510SP0(overwrites savedR3);call43D574(3,literal46B058,literal46B054,literal46B050). Fresh43D0CE bit0set or,ifclear,anotherfresh43D0CE bit2set calls43CE9E(0x0C000000,literal46B064,sameliteral,liveR3). Call45A568(liveargs);FULLresultnot1branches46AAB2outsidecomponent;FULL1 calls464C36(34,0,0,0),thenbranchesAAB2.

Independentincoming91C inheritsR1=addressliteral46AE98 frompreviouscomponent (nonzeroinitialread). SECONDfreshword[R1]R0FULLnot1branchesAAB2. FULL1 fresh43D0CE bit1clearbranches94Aoutsidecomponent. Ifset storeliteral46B068SP4,515SP0;R3literal46B050,R2literal46B054 at93C; diagnosticcontinues940. Retain independentreads and overwritten savedslots. No C/freeze/corpusclaim.
