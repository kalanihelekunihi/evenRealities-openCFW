# Guarded selector68 record 0x469E66..0x469EB0

Partial/unaccepted;74instructionbytes. PUSH R7/LR8 thenSUBSP48 creates56frame,SP48savedR7,SP52LR. R2=literal46AABC;freshunsignedbyte[R2];nonzeroR0=0 ->469F9E outsidechunk. Zero FULLR0selector!=68 branches469EB0;equal68 R0=originalR1,loadword[R0+16] ->R0pointer,thenNOP retained. No pointerguards.

R1=0,storebyte0SP40;R1=SP40;R2=68,storebyte[R1+1]. Freshword[R0] ->R2,storelow8[R1+2]. SECONDfreshword[R0] ->R2,ASR8,storelow8[R1+3]. Freshword[R0+4] ->R2,storelow8[R1+4]. SECONDfreshword[R0+4] ->R0 clobberpointer,ASR8,storelow8[R1+5]. Thisconstructs6bytes fromseparatewordreads; do notsnapshotorassumevaluesstable. SPwritesinterleavedwithreads preservealiasbehavior.

Call464BB2(34,SP40,6,0);branch469F9E withFULLchildR0live. OtherargsandR7restorationdeferredtosharedreturn. No C,freezeorchildcontractclaim.
