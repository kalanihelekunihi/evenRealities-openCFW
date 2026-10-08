# Handler entry 0x46949A..0x46951A

Partial/unaccepted;128 instruction bytes. PUSH R4/R5/LR thenSUBSP20 creates32-byteframe. FULL R0!=4 orFULL R1==0 orFULL R2==0 eachbranches469550 outsidechunk. Otherwise unsignedbyte[R1] ->R4; call46919E withliveoriginalargs, R5=FULLboolresult.

Fresh43D0CE bit1 enablesdiagnostic: loadunsignedbyte[address literal469B54] fresh andstoreSP16; temporaryR0low8R4 ->SP12; temporaryR0low8R5 ->SP8, preservingR4/R5. SP4=literal469B7C,SP0=189,R3=literal469B80,R2=literal469B38,R1=literal469B3C,R0=4 ->43D574.

Separatefresh43D0CE bit0 orconditional thirdfreshbit2 enables secondarydiagnostic. R1=literal469B84; independentlyloadunsignedbyte[address literal469B54] again ->SP4; temporarylow8R4 ->SP0; R3=low8R5 viaR3temporary;R2=R1;R0=0x10C00000 ->43CE9E. Do not mergetwo globalreads ortruncateR4/R5inplace. SP0/4/8/12/16 arelocaldiagnostics; savedregisters atSP20/24/28 remainintact. R4payloadbyte/R5boolliveat46951A. Childcontracts unresolved; no C,freezeorwholefunctionclaim.
