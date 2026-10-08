# Selector-two entry 0x469580..0x4695FE

Partial/unaccepted;126instructionbytes. PUSH R0/R1/R2/R3/R4/R5/R6/LR creates32-byteframe; SP0/4/8/12 originalargs,SP16/20/24 saved4/5/6,SP28LR. R5=originalR3. FULLR0!=2 branches4698EE. Equal2 fresh43D0CE bit1 diagnosticloadsunsignedbyte[addressliteral469B88] ->SP8, literal469B8CSP4,214SP0,R3literal469B90,R2literal469B38,R1literal469B3C,R0=3 ->43D574.

Separatefreshbit0 orconditional thirdfreshbit2 enables R1=literal469B94, independentlyfreshunsignedbyte[addressliteral469B88] ->R3,R2=R1,R0=0x0C400000 ->43CE9E. At4695DA setR0=1,R1=literal469B44,storebyte1[R1]. R1=28,R2=0,R4=literal469B98,R6=R4,R0=R6 ->43C0E4 withliveR3; nofillcontractpresumed. Freshunsignedbyte[addressliteral469B88] ->R0; bytezero branches4697BA,nonzero continues4695FE. R4globaladdress,R6sameaddress,R5originalR3remainlive. SP0/4/8 maydiagnosticoverwriteoriginalargs. No C,freezeorchildsemanticclaim.
