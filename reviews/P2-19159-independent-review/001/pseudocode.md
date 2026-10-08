# Selector69 and74 records 0x469EB0..0x469F16

Partial/unaccepted;102instructionbytes. Inherit56frame,FULLoriginalselectorR0,R1originalarg1. FULLR0!=69 branches469EE8. Equal69 R0=R1,loadword[R0+16]pointerthenNOP. No nullguard. Storebyte0SP32,R1=SP32,storebyte69[R1+1]. Freshword[pointer] ->R2low8store[R1+2];SECONDfreshword[pointer] ->R2ASR8low8store[R1+3]. Freshword[pointer+4] ->R2low8store[R1+4];SECONDfreshword[pointer+4] ->R0ASR8low8store[R1+5],clobberpointer. Call464BB2(34,SP32,6,0);branch469F9E retainingchildR0.

469EE8FULLR0!=74 branches469F16. Equal74 storebytes0,74,0,0,0,0 atSP24..29 throughorderedindividualbytewrites (explicitR1zeroassignmentsretained). Call464BB2(34,SP24,6,0);branch469F9E retainingchildR0. Theseareseparatecasebuffersfromselector68SP40; no overlappingwritesamongthese6byteregions. Preservefreshreads/interleavingforpointeralias, no cachedsnapshot. No C,freezeorchildcontractclaim.
