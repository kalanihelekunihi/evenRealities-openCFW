# Entry low-byte boolean message builder bit-zero-one leaves

Partial/unaccepted;94instructionbytes,threeentries. D870PUSH R2,R3,R4,LR16;R4=fullentryR0. Loadpointerliteral47D9C0;LDRD R2,R3,[pointer];STRD toSP0/SP4overwrites savedR2/R3with8templatebytes. Call45A568withliveargs;LOW8result→SP4. Independentlycall45A568againwithliveargs;fullresult==1→SP5=2;elseSP5=1.
R4=LOW8entryR0;zero→SP6=0;nonzero→SP6=1. ThusentryR0=256 produceszero. SP0..3andSP7retaintemplatebeforecallee. Call464D1C(259,SP,8,0),distinctfromprevious4651E0. POP R0,R1,R4,PC16 returnsR0=templatewordSP0,R1=modifiedwordSP4(bothsubjecttocallee memorywrites),R4=savedentryR4. CallresultR0discarded.
D8B8separateleafentry:loadliteral47D900pointer;freshunsignedbyte;AND1→R0;BXLR. D8C2separateleafentry:samepointer,freshunsignedbyte;extractbit1;UXTB;BXLR. Bothfull0or1,R1/R2/R3untouched,no frame/no fallthroughbetweenentries. No C/freeze/completenessclaim.
