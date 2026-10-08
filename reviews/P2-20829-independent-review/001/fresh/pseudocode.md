# Byte table high-byte XOR rolling word update

Partial/unaccepted;36 instruction bytes. PUSH R4,R5,R6 creates12-byte frame. EntryR0 buffer,fullR1 unsignedlength,R2 statepointer;load initialword[R2] intoR5,R4index=0;branchCBCDE (47CBDE).
While unsignedfullR4<fullR1:read unsignedbyte[R0+R4] intoR3;R3=byte XOR (R5logicalright24);R6=literal47CC14;readword[R6+(R3<<2)] intoR3;R5=R3 XOR (R5<<8)mod32;incrementR4mod32;repeatunsignedcomparison. Stateword read once before loop and written once atCBE2; zero length still reads/writes sameword. No assumed polynomial or table content; pointed table remains unrecovered here.
POP R4,R5,R6 thenBXLR. R0 unchangedbufferpointer,R1/R2unchanged,R3lastintermediateifloopran. No calls,finalxor or byteorderconversion. No C/freeze/completenessclaim.
