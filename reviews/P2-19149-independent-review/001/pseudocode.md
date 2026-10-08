# Accepted payload path 0x469D9E..0x469DDE

Partial/unaccepted;64instructionbytes. Inherit32frame,FULLoriginalR2==5,R1originalpayloadpointer; no nullpointerorlengthguardinthispath. Freshunsignedbyte[R1] ->R0,R2literal46A83C,storebyteR0[R2]. THENfreshbyte[R1+1] ->R0,byte[R1+2] ->R2,OR R0|R2<<8; freshbyte[R1+3] ->R2,OR<<16; freshbyte[R1+4] ->R1,OR<<24. ThislastreadclobberspayloadpointerR1. R1literal46A840;storeassembledlittleendianwordR0[R1]. Preservefirstglobalwritebeforelaterpayloadreadsforaliasbehavior.

Call45A568(liveargs) FULLresult!=1 branches469E12. FULL1 call443484(liveargs) FULLresult!=1 branches469E12. FULL1 R1=SP16,R0=SP12 ->443504 withliveR2/R3. LocalSP12/16 notinitializedhere; childispassedbothaddresses,butcontractunresolved. FreshwordSP16 ->R0; FULLnonzero branches469E18 outsidechunk,zero falls469DDE. No C,freezeorwholehandlerclaim; retainbranchbeyondprevioussurveyreturn ratherthanassumingfunctionends469E18.
