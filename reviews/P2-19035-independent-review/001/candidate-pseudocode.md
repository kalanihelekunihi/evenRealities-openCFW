# Payloadcases15/16 468920..4689DE

Partial,unaccepted;190instructionbytes.Inherited40frame,R4FULLthirdarg,R5payload,R6FULLpredicate,R7byte15or16. No additionalpayloadlengthcheckinthisinterval;entrynonnullR4previouslyrequired.

Case15fresh43D0CEbit1setSP4literal4690B4,SP0=361,R3literal468F08,R2literal468A38,R1literal468A3C,R0=3 to43D574. Separatefreshbit0 orconditional thirdbit2 R1literal4690B8,R2R1,R0=0x0C000000,liveR3 to43CE9E. TruncateR6inplace low8;!=1->46897C. Equal1:R0literal4690BC,THENfreshhalfword[R0]toR0;storehalfwordSP4 overwritinglow16previousSP4diagnosticcontext;R3=0,R2=2,R1SP4,R0=16 to464BB2. Branch46897C->468A28.

Case16freshbit1setSP4literal4690C0,SP0=374,samecommonargsR0=3 to43D574. Separatefreshbit0 orconditional thirdbit2 R1literal4690C4,R2R1,R0=0x0C000000,liveR3 to43CE9E. TruncateR6inplace low8;!=1->4689DC. Equal1:R0literal4690C8,THENfreshhalfword[R0]toR0;storehalfwordSP2 overwritingupper16previousSP0diagnosticline;R3=0,R2=2,R1SP2,R0=16 to464BB2. Branch4689DC->468A28. Childcontracts/halfwordmeaningunproven;exactreplay only,no gates/runtime/acceptance.
