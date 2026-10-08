# Threshold action 0x4699E0..0x469A76

Partial/unaccepted;150instructionbytes. Inherit32frame,threshold>=180signed andFULLmode1. Fresh43D0CEbit1diagnostic SP4literal469BD0,SP0=364,R3literal469B90,R2literal469B38,R1literal469B3C,R0=4 ->43D574. Separatefreshbit0 orconditional thirdfreshbit2 R1literal469BD4,R2R1,R0=0x10000000,live3 ->43CE9E.

R0=255;storebyteSP12 preservingupper24bits ofsavedoriginalR3word. R3=0,R2=1,R1=SP12,R0=266 ->464BB2. SaveFULLresultR4; FULLzero branches469A72. Nonzero fresh43D0CEbit1diagnostic storesR4SP8,literal469BD8SP4,369SP0,R3literal469B90,R2literal469B38,R1literal469B3C,R0=1 ->43D574. Separatefreshbit0 orconditional thirdfreshbit2 enables R1literal469BDC,R3FULLR4,R2R1,R0=0x04400000 ->43CE9E.

Shared469A72explicitR0=0 ->469ADE outsidechunk; alsoenteredbycounterless/modefailure branches. Childgets pointertoSP12 so furtherwritespossible; do not assumeimmutablebyte. DiagnosticsoverwritesSP0/4/8 are savedargument slots, notnewlocals. No C,freezeorchildcontractclaim.
