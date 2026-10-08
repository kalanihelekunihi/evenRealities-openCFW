# Payloadcase9 46869A..468722

Partial,unaccepted;136instructionbytes.Inherited40frame,R4FULLinputthirdarg,R5payload,R6FULLpredicate,R7byte9. UnsignedR4<3->468720. Elsefreshbyte[payload+1]overwritesR4,THENfreshbyte[payload+2]overwritesR5(payloadpointerlost). Fresh43D0CEbit1setR0low8R5toSP12,R0low8R4toSP8,SP4literal469098,SP0=297,R3literal468F08,R2literal468A38,R1literal468A3C,R0=3 to43D574. Separatefreshbit0 orconditional thirdbit2 FIRSTR1literal46909C THENR0low8R5toSP0,R3low8R4,R2R1,R0=0x0C800000 to43CE9E;R4/R5byte snapshots preserved.

R0literal468C24;storebyteR4at0 thenbyteR5at1. TruncateR6inplace low8;!=1->468720. Equal1:R0literal4690A0,THENfreshbyte[R0]toR0,storebyteSP0;R3=0,R2=1,R1SP,R0=16 to464BB2. Shared468720->468A28 (distinctfromgeneral468A2A). No length/object/childcontracts inferred beyondobservedunsignedcomparison;epilogueexcluded. Exactreplay only,no gates/runtime/acceptance.
