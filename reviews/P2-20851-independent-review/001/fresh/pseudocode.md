# Eight-byte template two fresh reads message259 saved-slot return

Partial/unaccepted;70instructionbytes. PUSH R5,R6,R7,LR16frame. R0=literal47D8FC;LDRD R2,R3,[R0];STRD R2,R3,[SP] overwrites savedR5/R6 with eight templatebytes.
Call45A568 withlivearguments;storeLOW8 returnedR0 atSP4. Call45A568 again withcurrentlivearguments;comparefullreturnedR0exact1:if1 SP5=2 elseSP5=1. Do notcachecalls orcomparelowbyteonly.
R0=literal47D900;freshunsignedbyte[R0],extractbit2 (0or1),storeSP6. SP0..3 andSP7 retainedfromtemplate. Call4651E0(259,SP,8,0).
POP R0,R1,R2,PC16. ReturnR0=wordSP0 (templatefirstword,subjecttoanycallee memorywrites);R1=wordSP4 (modifiedtemplatebytes,subjecttoanycallee memorywrites);R2=savedentryR7SP8. R5/R6/R7 currentregisters are not restoredbythisPOP. Callee resultR0 discarded. No protocolfieldcontract inferred; pointedtemplateownership remains. No C/freeze/completenessclaim.
