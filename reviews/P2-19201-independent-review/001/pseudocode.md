# Difference coordinates and diagnostics 0x46A5C0..0x46A64A

Partial/unaccepted;138instructionbytes. Inherit48frame, selected-object pathR7/R8/R4childsnapshots,R6/R5globaladdresses. Freshword[R6] ->43FD9E(liveargs),FULLresultR9;SECONDfreshword[R6] ->43FDDA(liveargs). R7=wrapping32(R7-R9-8);R4=wrapping32(R4-childR0);R0=2;R9=wrapping32(signeddivideR4by2towardzero+R8). Zero-selected-object route skips this arithmetic to5E0 with R7=0,R9=0, no use of uninitializedR8.

At5E0 fresh43D0CE(liveargs) bit1 set: storeR9SP16,R7SP12,freshword[R5]SP8,literal46B014SP4,451SP0;call43D574(4,literal46A834,literal46A830,literal46B018). At60C fresh43D0CE bit0 set or, if clear, anotherfresh43D0CE bit2 set: storeR9SP4,R7SP0;call43CE9E(0x10C00000,literal46B01C,sameliteral,freshword[R5]). Extra stackwords preserved per route; no statusread collapsing.

Call43F09A(freshword[R6],R7,R9,liveR3). R4=addressliteral46ACD4;freshword[R4]zero branches46A668outsidecomponent;otherwisefreshword[R5]FULLcomparedzero at46A648, flagscontinue46A64A. Childcontracts unresolved;no C/freeze/wholecorpusclaim.
