# Selector-four guard and counter 0x46997C..0x4699E0

Partial/unaccepted;100instructionbytes. Inherited32frame,FULLoriginalselectorR0. FULLR0!=4 branches469A76. Equal4 loadsR0=literal469B9C thenfreshword[R0]; FULLnonzero branches4699C6. Zero fresh43D0CEbit1diagnostic:SP4literal469BC8,SP0=353,R3literal469B90,R2literal469B38,R1literal469B3C,R0=2 ->43D574. Separatefreshbit0 orconditional thirdfreshbit2: R1literal469BCC,R2R1,R0=0x08000000,live3 ->43CE9E. R0=0 ->469ADE.

Nonnull4699C6 R0=literal469B98;R1=freshword[R0+24];R1=wrapping32(R1+1);storeword[R0+24];SECONDfreshword[R0+24] ->R1; compareSIGNED32 R1 against180. Signedless branches469A72, includingnegativewrappedvalues. OtherwiseR1=0;storeword0[R0+24];call45A568 withR0globaladdress,R1zero,liveR2/3. FULLresult!=1 branches469A72;FULL1 falls4699E0 outsidechunk. Preservewrite-then-freshread andsignedthreshold; no unsignedcounterreplacement. No C,freezeorchildcontractclaim.
