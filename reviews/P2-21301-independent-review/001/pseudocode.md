# Packed three-byte weighted scalar helper

Partial/unaccepted;34 instructionbytes482ED4..482EF6. PUSH{R0}4bytes,savedentrywordbyte0atSP0,byte1SP1,byte2SP2,byte3SP3. FreshbyteSP2→R1,R2=3,freshbyteSP1→R0;R0=3*R1+R0mod2^32. FreshbyteSP0→R1;R0+=R1<<2mod;R0=UXTH(R0),logicalright3,R0=UXTB(R0). ThusreturnUXTB(UXTH(3*byte2+byte1+4*byte0)>>3);entryhighbyteunused. ADDSP4,BXLR,no calls/memorywritesbeyondstackpush,clobbersR1/R2. Preserveactualweights/truncationswithoutassumedcolorchannelmeaning. No C,freeze,wholecoverage or equalityclaim.
