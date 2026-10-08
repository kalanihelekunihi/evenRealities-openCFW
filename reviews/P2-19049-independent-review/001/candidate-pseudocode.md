# Payloadbyteone468BB6..468C24

Partial,unaccepted;110instructionbytes.Inherited32frame,R4savedpayloadbyte nonzero. TruncateR4inplace low8;!=1->468C20. Equal1:R4literal469100,replacingbyte;freshbyte[R4+2]zero->468C20. Nonzero:fresh43D0CEbit1setfreshbyte[R4+1]toSP12 THENfreshbyte[R4]toSP8;SP4literal469104,SP0=440,R3literal4690D8,R2literal4690DC,R1literal4690E0,R0=3 to43D574. Separatefreshbit0 orconditional thirdbit2 FIRSTR1literal469108 THENfreshbyte[R4+1]toSP0 THENfreshbyte[R4]toR3;R2R1,R0=0x0C800000 to43CE9E.

468C18:R0=0,storebyte0[R4+2];47E58E(R0=0,liveR1/R2/R3). No explicitpairrestore/childcontractassumed;onlyflagclear andcallproved. Shared468C20 ADDSP24 discards20locals ANDsavedR3slotSP20;POP R4/PC8 restores32frame. R0remainslivefromlastpath/call;notexplicitsuccessconstant. SavedR4restored,originalR3notpoppedintoaregister. Exactreplay only,no gates/runtime/acceptance.Followingpool excluded.
