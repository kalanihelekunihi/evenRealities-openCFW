# Three-byte weighted blend and stack result

Partial/unaccepted;116 instructionbytes482DD8..482E4C. PUSH{R0,R1,R4,R5}16bytes thenSUBSP4 total20-byteframenoLRsave/no calls. SavedentryR0bytesSP4..7 andentryR1bytesSP8..11. R0=32897(0x8081). Forbyteoffset2first,then1: freshbyteSP(4+i)→R1,R3=UXTB(entryR2),freshbyteSP(8+i)→R4,R5=255-UXTB(entryR2);R4*=R5mod;R1=R3*R1+R4mod;R1*=32897mod;logicalright23;storelowbyteSPi. Thirdoffset0sameformula viaR2 overwritten: R3=UXTB(entryR2),R4=freshSP8byte,R2=255-UXTB(entryR2),R2*=R4;R2=R3*freshSP4byte+R2;R2*=32897mod,logicalright23,storelowbyteSP0.

FreshwordSP0→R0 includes calculatedbytes0..2 and UNWRITTENbyteSP3;upperbyteisnotinitializedbythisroutine. POP{R1,R2,R3,R4,R5}20bytes returnsR1=temporarySP0word,R2=savedentryR0,R3=savedentryR1,R4/R5restored;BXLR retainsR0freshresult. Preserveexactintegerformula/truncations,byteorder andunspecifiedupperresultbyte;noassumedroundedblend/alpharesult. No C,freeze,wholecoverage or equalityclaim.
