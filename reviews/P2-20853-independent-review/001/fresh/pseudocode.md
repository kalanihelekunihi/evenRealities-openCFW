# Alternate template bit-four two-three message259

Partial/unaccepted;82instructionbytes. PUSH R5,R6,R7,LR16frame. Loadpointerliteral47D904,readtwo templatewords viaLDRD R2,R3,STRD toSP0/SP4 overwritessavedR5/R6.
Call45A568 withliveargs;LOW8result→SP4. Independentlycall45A568againwithliveargs;fullR0==1→SP5=2;elseSP5=1.
Loadpointerliteral47D900;freshunsignedbyteatpointer;extractbit4,UXTB,comparezero;ifnonzeroSP6=3;elseSP6=2. No secondflagbyte read. SP0..3/SP7remain templatebytes beforecallee.
Call4651E0(259,SP,8,0). POP R0,R1,R2,PC16 returnswordSP0 (templatefirstwordsubjecttocallee memorywrites),R1=modifiedwordSP4subjecttocallee memorywrites,R2=savedentryR7;sendresultdiscarded. R5/R6/R7notrestoredbyPOP. Preservetwohelpercalls,fullwidthcomparison anddifferenttemplate/flagbit. No protocolcontract/C/freeze/completenessclaim.
