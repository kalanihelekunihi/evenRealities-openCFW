# Empty predicate and removal prefix4602B6..460302
Partial;unaccepted.76 instructionbytes,onecompleteleafandopenremovalprefix.
4602B6 R0=wordliteral460E04 ringbase;R0=freshhalf[R0+260];fullzero→R0=1,nonnull→R0=0;4602C8BXLR. No nullguard/frame/child.
4602CA PUSH{R4,R5,R6},frame12. FullzeroincomingR0→R0=FFFFFFFD→460340externalepilogue. OtherwiseR2=low16incomingR1;fullzeroR2→samefailure. NonzeroR3=wordliteral460E04,R2=freshhalf[R3+260];fullzero→R0=0→460340. NonzeroR2=incomingR1;R4=SEPARATEfreshhalf[R3+260];R2=low16R2;unsignedR2<R4→4602FE retainingfullincomingR1. OtherwiseR1=THIRDfreshhalf[R3+260],no retest/recomparison;thisreplaceslength. 4602FER2=0;460300branch460330externaltest;body460302excluded. R0retainsoutputpointeronbodyroute,R3ringbase. Freshcountreadsnotmerged; selectedR1mayobservechangedcount. No synchronization/childreninprefix;remainingloopandreturnunresolved.
No C,gate/source admission,whole coverage or simulator/hardware proof.
