# Ring reset and byte setter460344..460374
Partial;unaccepted.48 instructionbytes,two completefunctions.
460344 PUSH{R4,LR},frame8;R4=wordliteral460E04 ringbase. OrderedR0=0,half[R4+256]=0;R0=0,half[R4+258]=0;R0=0,half[R4+260]=0. ThenR1=256,R2=0,R0=retainedR4;43C0E4 with liveincomingR3. ChildresultfullR0retained;460368POP{R4,PC}restoreoriginalR4/LR,returnchildR0. No nullguard/globalpointerdereference;ringbaseis literalvalue. No childmemorycontract inferred. Metadata storesprecedechild.
46036A leaf:R0=low8incomingR0;R1=wordliteral460E08 globalbase;word[R1+12]=zeroextendedlow8R0;460372BXLR returnsnormalizedR0. Fullwordstore,notbytewrite;otherregistersunchangedexceptR1. Next460374excluded.
No C,gate/source admission,whole coverage or simulator/hardware proof.
