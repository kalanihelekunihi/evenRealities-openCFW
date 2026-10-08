# Aligned size and two-pointer initialization, node prepend

Partial/unaccepted;86 instructionbytes482B00..482B56. Frameless482B00: R2=0 store[R0+4],R2=0 store[R0+8];R1+=3mod2^32,logicalright2thenleft2,store[R0];BXLR. Thus alignedsize=(entryR1+3mod)&FFFFFFFC; no overflowguard; ordered fieldwrites before size.

Separate482B12 PUSH{R3,R4,R5,LR}16bytes;R5=entryR0descriptor;freshword[R5]→R0,add8mod;call44F718 liveR1/R2/R3;returnedR0→R4. ZeroR4 skipsalllinkwrites returns0. Nonzero: R2=0,R1=R4,R0=R5,call482DAE liveR3. Freshword[R5+4]→R2,R1=currentR4,R0=currentR5,call482DC2 liveR3. Freshword[R5+4]→R0,ifnonzero independentlyreload[R5+4]→R1,R2=R4,R0=R5,call482DAE liveR3. StoreR4[R5+4] thenfreshword[R5+8]zero→storeR4[R5+8];nonzero retains. R0=R4,POP{R1,R4,R5,PC}16bytes;R1=savedentryR3. Linkhelper semantics unresolved; no allocationownershipassumption or C. No freeze,wholecoverage or equalityclaim.
