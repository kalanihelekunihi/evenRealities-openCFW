# Guarded arithmetic 0x46A2F0..0x46A344

Partial/unaccepted;84instructionbytes. Inherit40frame,R6literal46AE70,R7literal46ACD4,R8literal46ACD8addresses,allthreepointedwordsinitiallynonnull. R9literal46ACCC;R0freshword[R9] ->43F66C(liveargs). R0freshword[R6] ->43FD9E(liveargs),FULLresultR10. SECONDfreshword[R6] ->43FDDA(liveargs),FULLresultR5. Freshword[R7] ->43FDDA(liveargs),FULLresultR4.

R0literal46ACDC;freshword[R0];R10=wrapping32(R10+wrapping32(R0<<1));R1R10,R0freshword[R9] ->43F506(live2/3). R0literal46ACD0;freshword[R0];R10=wrapping32(R0+R10);storeFULLR10SP0 overwriting savedoriginalR3. R10=literal46ACC4 replacesarithmeticvaluewithglobaladdress. R1freshwordSP0,R0freshword[R10] ->43F506(live2/3). R4/R5FULLchildresults,R6/R7/R8/R9/R10addressesremainliveat46A344. No cachedpointerreuse,overflowassumptions orchildcontractinferred; no C,freezeorwholefunctionclaim.
