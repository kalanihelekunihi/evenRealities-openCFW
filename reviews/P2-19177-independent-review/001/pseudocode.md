# Object entry arithmetic 0x46A18C..0x46A1DE

Partial/unaccepted;82instructionbytes. PUSH R4/R5/R6/LR16;R6originalR0. R4literal46ACC4,R0=R6 ->43DE82(live1/2/3);storeFULLresult[R4]. R5literal46ACC8;R2freshword[R5],R1=200,R0freshword[R4] ->43F4C0(live3).

R0=R6 ->43FD9E(liveargs);R0=wrapping32(result-200);R1=2;R1=SIGNEDdivideR0by2truncatedtowardzero. R0freshword[R4] ->43F0E0 withcomputedR1/liveR2/3. R0=R6 ->43FDDA(liveargs);R1=SECONDfreshword[R5];R0=wrapping32(result-R1);R1=2;R1=SIGNEDdivideR0by2truncatedtowardzero. R0freshword[R4] ->43F142(computedR1,live2/3). R1=8196,R0freshword[R4] ->43DFA4(liveR2/3).

R4/R5globaladdresses,R6originalR0remainliveat46A1DE. Signeddivision isnotarithmeticshiftfornegativeoddvalues; wrapping32subtractbeforedivision matters. Preservefreshglobalreads andlivechildarguments; no geometry/layoutcontract inferred. No C,freezeorwholefunctionclaim.
