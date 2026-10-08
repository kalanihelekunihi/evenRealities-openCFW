# Provider stack-field result and recursive callback wrapper

Partial/unaccepted;72 instructionbytes482FAA..482FF2. 482FAA PUSH{R7,LR}8bytes,call482F74 entryR0/liveR1/R2/R3;R1=returnedR0,testzero. NonzeroR0=SP,R1+=16mod,R2=3,call439BE4 liveR3;branch482FCA. Helpersemanticsunresolved; ifthree-bytecopycontractlaterproved, SP3 remains savedentryR7upperbyte. ZeroR1:R0=17,call488290 liveR1/R2/R3,storefullreturnedR0 SP0. CommonfreshwordSP0→R0,POP{R1,PC},R1=thatstackwordalso,PCsavedLR.

Separate482FCE PUSH{R3,R4,R5,LR}16bytes,R4=entryR0,R5=entryR1. Freshword[R4+4]→R0;nonnull: independentlyreload[R4+4]→R0,R1=R5,recursivelycall482FCE liveR2/R3. Thenfreshword[R4]→R0;nonnull:R1=R5,R0=R4,independentlyreload[R4]→R2,BLXR2 liveR3. No secondnullcheckonfreshcallbackreload/no cycleguard. POP{R0,R4,R5,PC}returns savedentryR3overridingcallback/recursiveR0. Preservefreshfieldreads,recursivebeforecallbackorder,stackwordreadwidth andreturnaliases. No C,freeze,wholecoverage or equalityclaim.
