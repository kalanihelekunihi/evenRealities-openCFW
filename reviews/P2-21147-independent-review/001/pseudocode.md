# Mode four two masked word writes with fixed bits

Partial/unaccepted;92 instruction bytes480B66..480BC2. Dispatch mode4 of4809C4;16-byte frame. R1=pointer literal480EB4;freshword→SP0;reloadR2 ANDliteral480EB8→SP0;reloadR0 retains masked original. Freshbyte from pointer480EBC masked63 ORR0;freshword from pointer480EC0 shifted6mod2^32 AND960 ORR0. OR0x03000000 thenOR0x00118000 intoR0;storeSP0;reloadSP0 and storeword[R1]. Unlike mode3, masked original participates in result. Literal480EC4 not used by this mode.

R1=pointer literal480EC8;freshword→SP0;reloadR2 ANDliteral480ED4→SP0;reload OR2→SP0;reload storeword[R1]. Branch480A18 setsR0=0 thenPOP R1,R4,R5,PC16;R1 receives finalscratchSP0,not entryR3. EntryR1 pointer (savedR4) unused;no input byte predicate or helpercall. Preserve scratch accesses, source-read order and both writes. No C/freeze/fullcoverage/equality claim; remaining modes unresolved.
