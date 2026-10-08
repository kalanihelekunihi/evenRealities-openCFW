# Third template two fresh calls message259

Partial/unaccepted;56instructionbytes. PUSH R5,R6,R7,LR16frame. R0=literal47D908;LDRD R2,R3,[R0];STRD toSP0/SP4 overwritessavedR5/R6with8templatebytes.
Call45A568withliveargs;LOW8returnedR0→SP4. Independentlycall45A568againwithliveargs;fullreturnedR0==1→SP5=2;elseSP5=1. Thisroutinehasnoflagbyte read orSP6write;SP0..3/SP6..7retaintemplatebytesbeforecallee.
Call4651E0(259,SP,8,0). POP R0,R1,R2,PC16;R0=wordSP0,R1=modifiedwordSP4 (bothsubjecttocallee memorywrites),R2=savedentryR7. HelperresultR0discarded;R5/R6/R7notrestoredbyPOP. No protocolcontract/C/freeze/completenessclaim.
