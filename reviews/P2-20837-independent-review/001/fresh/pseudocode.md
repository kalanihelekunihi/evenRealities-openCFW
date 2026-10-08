# Two-word sign normalization and flag-dependent helper

Partial/unaccepted;66 instruction bytes. InputpairsR1:R0 andR3:R2. IP=R3&80000000 usingANDS; ifNset negateR3thennegateR2 thenR3=SBC(R3,0) using carryfromlowwordNEG:pairnegationmod64.
CC2A IP XOR=arithmeticshift(R1,32), flagsupdated;shiftcarry=originalR1bit31. IfZset tailbranch47CC60 withoutframe. This means IPzero; pendinghelperreturnsdirectlytocaller. OtherwisePUSH R4,LR8;R4=IP;BCC CC40 usingcarryfromASR32. Ifcarryone negatepairR1:R0 byNEGhi,NEGlo,SBC hi0.
CC40 call47CC60 with currentR0..R3,IP. CC44 LSLS R4,1;carry=oldR4bit31,N=newbit31. Ifcarryone negate returnedpairR1:R0;thenTST R4,R4 reestablishN. IfNset atCC52 negate returnedpairR3:R2. POP R4,PC8.
No helper arithmetic operation inferred until47CC60 recovered. Preserve flags across branches, lowwordNEGcarryintoSBC,tailbranchvsframedcall. R4encodesentrysigncombination; do not eraseIPsideeffects. No C/freeze/completenessclaim. BytesCC5E..60outsideinstructionmap.
