# Packed-key update reverse search and resize prefix

Partial/unaccepted;152 instructionbytes482868..482900. PUSH{R1,R2,R3,R4,R5,R6,R7,LR}32bytes;R4=descriptor,R5=entrykey,R6=entryvalue. Call482708(R0=R4,liveothers). Nonzero loads482AC4→SP0(overwritessavedR1),482AC8→R3,R2=332,482AB4→R1,R0=3;call44D25C;branchunresolved482944 withreturnedR0. Zero predicate:UXTB(R5)==0 diagnostic loads482ACC→SP4(savedR2),482AD0→SP0,482AC8→R3,R2=336,482AB4→R1,R0=3;call44D25C then infinite4828AC loop R0=0,R1=FFFFFFFF,storeword0atFFFFFFFF,branchback;mayfault, no assumedtrapreplacement.

Nonzerokey: freshword[R4]testnull;null→4828E2. Nonnullindependentlyreloadbase, freshcount[R4+8] compute keybase=base+4*countmod;independentlyreloadcount,index=count-1mod. Loop signedindex<0→4828E2;elsefreshbyte[keybase+index] compareUXTB(R5);mismatchindex--repeat. Match freshword[R4]reloadbase,storefullR6 atbase+4*index,branch482944.

4828E2 freshcountbyte+1mod→R0,R1=5*R0mod;freshbase[R4]→R0;call44F76A withliveR2/R3. ReturnedR0zero→482944;nonzero storebase[R4] beforefreshcountbyte→R1,keybaseR1=R0+4*countmod;freshcountbyte→R2 at4828FE. Fallthrough482900unresolved. Preserve independent freshcounts, reverse unsigned-byte key comparison, ordereddescriptorstore and rawcallreturns. No C,freeze,wholecoverage or equalityclaim.
