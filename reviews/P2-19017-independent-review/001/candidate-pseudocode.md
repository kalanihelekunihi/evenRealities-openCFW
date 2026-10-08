# Eventzero4684F6..468558

Partial,unaccepted;98instructionbytes.Inherited40frame,R7event0,R5payload,R4FULLinputthirdarg,R6FULL45A568snapshot. R1=low16R4,R0R5,liveR2/R3 to4A78D0;FULLnonzero->4685E8. Zero:R4literal468C24 replacinginputthirdarg;freshbyte[R4+2]!=2->46862C. Equal2:freshbyte[R4]==4else468546.

Statebyte4:R0=0,liveargs to47E470;THENtruncateR6inplace low8. R6!=1->46862C. Else443484(alllive)FULLresultmust1else46862C;R0=16,liveargs to4434D0 FULLresultmust1else46862C. R3/R2/R1=0,R0=16 to464C36;branch468544->46862C.

468546 non4arm:443484 withR0freshstatebyte,liveR1/R2/R3. FULLzero->468558. NonzeroR0=16,liveargs to4434D0;FULLresult==1->4685B6,othersfallthrough468558. Independentpredicatecalls retained,notmergedwithstate4path. No globalstate/event/childcontracts assumed. Laterdiagnostics/actions excluded;exactreplay only,no gates/runtime/acceptance.
