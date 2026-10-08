# Payloadcase14 entry46882A..4688B8

Partial,unaccepted;142instructionbytes.Inherited40frame,R4FULLthirdarg,R5payload,R6predicate,R7byte14. UnsignedR4<2->46891E. Elsefreshbyte[payload+1]overwritesR5(payloadpointerlost);R0=0,liveR1/R2/R3 to4A7838;R4FULLreturnedpointer. Nonnullfreshbyte[R4]overwritesR6(predicate lost),elseR6=0. R0low8R5==1 ANDR0low8R6==1 =>R7=1,elseR7=0. Unlikecase13 R5payloadbyte/R6pointedbyte snapshot.

Fresh43D0CEbit1setR0low8R7toSP16,R0low8R6toSP12,R0low8R5toSP8;SP4literal4690A4,SP0=347,R3literal468F08,R2literal468A38,R1literal468A3C,R0=3 to43D574. Separatefreshbit0 orconditional thirdbit2 FIRSTR1literal4690A8 THENR0low8R7toSP4,truncateR6inplace low8toSP0,truncateR5inplace low8toR3;R2R1,R0=0x0CC00000 to43CE9E. R4pointer preserved;no ownership/object/childcontracts inferred. Furtherfreshcomparison/actions excluded;exactreplay only,no gates/runtime/acceptance.
