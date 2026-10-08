# Inverted byte, return and leaves 0x469400..0x46949A

Partial/unaccepted;154 instruction bytes. Inherit24-byte frame. R4 low8contextbool zero sets byteSP12=1, nonzero sets byteSP12=0, preserving upper24 bits of savedoriginalR3word. Shared46940E setsSP0=4,R3=0,R2=1,R1=SP12,R0=266 ->464F76. FULLresultR4=R0 zero branches46946C. Nonzero fresh43D0CE bit1diagnostic storesR4SP8,literal469B74SP4,150SP0,R3literal469B6C,R2literal469B38,R1literal469B3C,R0=1 ->43D574. Separatefreshbit0 orconditionalthirdfreshbit2 enables R2=literal469B78,R3=FULLR4,R1=R2,R0=0x04400000 ->43CE9E.

Shared46946C POP R0/R1/R2/R3/R4/PC consumes24bytes. Initialglobalguardnonzero returns originalR0/R1/R2/R3. Actionpaths return R0=4 fromSP0, unless resultdiagnosticbit1 overwroteSP0 with150. R1/R2 similarly reflect overwrittencontext/result ifdiagnostic; restoredR3 includesSP12modifiedbyte and possiblechildwrites throughpointer. LivechildR0 is not returned. R4 restored.

46946E standalone BXLR changes no registers. 469470..46949A leaf comparesFULLR2 inorderedtree10,66,67,68,69,72; eachcase anddefault separatelysetR0=1 andBXLR469498. Preserveorderedcomparisons despitecommonresult; nochildcalls. No C,freezeorwholecorpusclaim.
