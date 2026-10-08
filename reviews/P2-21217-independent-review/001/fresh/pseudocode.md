# Double-word helper, hex prefix and zero magnitude branch

Partial/unaccepted;94 instruction bytes481DE8..481E46. Continues481836232frame. ReloadrawSP8/SP12→R0/R1;R2=SP;call4D4150 withliveR3;storefullreturnedR0/R1SP8/SP12. Helpersemantics/SP0effects unresolved. R0=R11OR32;ifa97:reloadpointerSP20→R0,storebyte48atpointer0;R2=pointer+2→SP20;R1='x'120ifR11exact97else'X'88;storebytepointer1;reloadSP28countadd2mod2^32storeSP28. Otherconversion skipshexprefix.

Separate481E14 special-pathentry:ADR R1=4826F0;branch481DD8 existing3-bytecopy path;notfallthroughnormalization. Preservecontrolflowoverthisisland.

At481E22 reloadreturnedSP8/SP12;R2=lowunchanged(BIC0),R3=high&7FFFFFFF;IT EQ compareslowto0onlyifmaskedhigh0. Bothzero→R6=0,R5=0branch4820C0 unresolvedzeroformatpath. Nonzero→R8=R11OR32;ifR8!='a'→481F6A unresolveddecimalpath;elsefallthrough481E46 unresolvedhexprecision. Exactrawreturnedvalueused;noFPlibrarysubstitution,C/freeze/fullcoverage/equality claim.
