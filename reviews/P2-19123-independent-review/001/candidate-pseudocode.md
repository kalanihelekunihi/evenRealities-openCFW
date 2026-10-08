# Selector-three path 0x4698EE..0x46997C

Partial/unaccepted;142instructionbytes. Inherit32frame, entryfromFULLoriginalR0!=2; liveR0originalselector,R1originalarg1,R2originalarg2,R5originalR3. FULLR0!=3 branches46997C. FULLR1zero orFULLR2zero eachbranches469978. Otherwise unsignedbyte[R1] ->R0; explicitUXTB thenFULLcompare255; unequalbranches469978.

Fresh43D0CE bit1 diagnostic SP4literal469BC0,SP0=335,R3literal469B90,R2literal469B38,R1literal469B3C,R0=4 ->43D574. Separatefreshbit0 orconditionalthirdfreshbit2 R1literal469BC4,R2R1,R0=0x10000000,liveR3 ->43CE9E.

R2=literal469B9C,R0=freshword[R2];FULLzero branches469978. Nonzero R1=266,R0=SECONDfreshword[R2] ->4641B6 withliveR2/R3. R0=0,R1literal469B44,storebyte0[R1];call45A568(liveargs). FULLresult!=1 branches469978. FULL1 freshunsignedbyte[addressliteral469B88] ->R0; nonzero branches469978. Zero setsR0=0 ->49BF24(liveargs); then45A8EE(1,0,0,500).469978explicitR0=0 ->469ADE outsidechunk. Preservetwofreshglobalwordreads andorderedchildsideeffects. No C,freezeorchildcontractclaim.
