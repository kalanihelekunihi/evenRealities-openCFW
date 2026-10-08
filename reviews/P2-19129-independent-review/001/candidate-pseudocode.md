# Selector-five and epilogue 0x469A76..0x469AE2

Partial/unaccepted;108instructionbytes. Inherit32frame originalselectorR0. FULLR0!=5 branches469ADC explicitR0=0. Equal5 fresh43D0CEbit1diagnostic SP4literal469BE0,SP0=378,R3literal469B90,R2literal469B38,R1literal469B3C,R0=4 ->43D574. Separatefreshbit0 orconditional thirdfreshbit2 R1literal469BE4,R2R1,R0=0x10000000,live3 ->43CE9E.

Freshunsignedbyte[addressliteral469B88] ->R0; zero skips469AC8. NonzeroR0=1 ->4691BC(liveotherargs); thenR0=1 ->49BF24(liveotherargs). Shared469AC8 R0=0,R1literal469B44,storebyte0[R1];R0=0,R1literal469B54,storebyte0[R1];call46946E(liveargs), knownBXLRleafretainingR0. ExplicitR0=0 ->469ADE.

469ADE ADDSP16 discardsoriginalsavedR0/R1/R2/R3words,includingdiagnosticoverwrites andSP12byte/pointerwrites;POP R4/R5/R6/PC16 restores32frame. Allfunctionrecordedselector2/3/4/5/default exits explicitlysetR0=0 beforeepilogue. Following469AE2newPUSH isexcluded. Preservetwo distinctflagstoresandchildorder; no C,freezeorwholecorpusclaim.
