# Arithmetic tail and epilogue 0x46A344..0x46A3D8

Partial/unaccepted;148instructionbytes. Inherit40frame,R10literal46ACC4address,SP0computedwordoverwrittensavedR3. Freshword[R10] ->44DCA2(liveargs),FULLresultR11. R0R11 ->43FD9E;R1freshSP0;R0wrapping32(result-R1);R1signeddivideR0by2towardzero;R0freshword[R10] ->43F0E0(live2/3). R0R11 ->43FDDA;R1freshword[addressliteral46ACC8];R0wrapping32(result-R1);R1signeddivideR0by2;R0freshword[R10] ->43F142(live2/3).

R10literal46ACE0 replacesoldaddress;R3freshword[R10],R2=0,R1=2,R0freshword[R6] ->43F6B8. SECONDfreshword[R10] ->R0;R5wrapping32(R5+R0);R0freshword[addressliteral46ACE4];R5wrapping32(R0+R5). Call43F6B8(freshword[R7],2,0,FULLR5). R4wrapping32(R4+R5);R0freshword[addressliteral46AE74];R4wrapping32(R0+R4);call43F6B8(freshword[R8],2,0,FULLR4). Freshword[R9] ->43F66C(liveargs),then46A53A(liveargs).

Shared46A3D2 LDMIA SP! R0/R4/R5/R6/R7/R8/R9/R10/R11/PC restores40bytes. R0fromSP0 originalR3 onshortcircuitfailure,computedwordonsuccess, notlastchildresult. Independentleaf46A3D6 BXLR changesnothing. No C,freezeorwholecorpusclaim.
