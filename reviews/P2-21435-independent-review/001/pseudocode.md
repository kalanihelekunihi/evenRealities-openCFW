# Child parent type-seven search and global callback return tail

Partial/unaccepted;114 instructionbytes4845BC..48462E. Continuing48458E24Bframe:R6result=0. ParentR5+72nonnull,byte[parent+80]!=0,andword[parent+68]==0 enablesparentownersearch;else4845FC. Freshownerword[parent+72]R0,R1=word[owner+68]. TraverseR1nextword0;firstnodewithbyte+4==7,word+80==0,word[word[node+84]+28]==parentR5:store1node+80,R0=1retained,R1=node;48462E;branchreturn48461C,resultR6still0. No matchalso returns0.

4845FCR0=wordliteral4849A8global,R4=word[global+316];whilenode: R1=parentR5,R0=nodeR4,R2=freshword[node+12],BLXR2withoutnullguard; CMNR0,1 EQmeansFFFFFFFFskipsflag,othersR6=1. Freshword[node]nextaftercallback;repeat. ReturnR0=UXTB(R6);POP R1savedentryR3,R4/R5/R6/R7/PC24B. New4846228Bwrapper:R0=wordliteral4849A4;4D46E8;POPR0savedR7/PCoverrideshelperresult. Preservesearchpriorityandexacthelperargs. No C,freeze,wholecoverage or equalityclaim.
