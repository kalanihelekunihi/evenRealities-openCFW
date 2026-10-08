# Guarded event list return and global secondary callback traversal

Partial/unaccepted;70 instructionbytes484502..484548. Guardalreadysetentry484502storebyte100recordR5+89,byte0record+88;R4=word[globalR4];loopnode nonnull,freshword[node+16]R0nonnull→R1=recordR5,R0=nodeR4,R2=freshword[node+16],BLXR2;ignoredresult;freshword[node]R4aftercallback;repeat. Unlikeunguardedpath,no claimbytecheck/helperaftertraversal;fallscommon484526. POPR0/R1,R4/R5/R6/PC24B;R0/R1savedentryR2/R3 exceptdiagnosticpathSP0overwrittenwithliteral4849CC,thereR0diagnosticpointer. Noexplicitstatusreturn.

484528newPUSH R4/LR8B;R0=wordliteral4849A8global,R4=word[global+316]. Whilenodenonnull: freshword[node+20]R0nonnull→R0=node,R1=freshword[node+20],BLXR1(liveR2/R3);nextfreshword[node]R4aftercallback. Nullcallbackskipinvoke;returnPOPR4/PC8B leavespathdependentR0(lastnullcallbackcheckorcallbackresult). No C,freeze,wholecoverage or equalityclaim.
