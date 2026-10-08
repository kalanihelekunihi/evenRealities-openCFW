# Zero-argument wrapper and sparse or packed byte-key lookup

Partial/unaccepted;130 instructionbytes4826FC..48277E. Separate4826FC wrapper PUSH{R7,LR}8bytes,R2=entryR1,R1=0,call454746 withentryR0/liveR3;POP{R0,PC} returns savedentryR7 ratherthan helperresult. Frameless482708 freshly readsbyte[entryR0+8],returns1ifequals255else0,BXLR.

482716 lookup PUSH{R4,R5,R6,LR}16bytes;R6=entryR0 descriptor,R5=entryR1 key,R4=entryR2 output. Call482708(R0=R6,liveR1/R2/R3). Nonzero result: freshword[R6]→R1 table,R2=0. Loop freshbyte[R1+8*R2 modulo] firsttestsNUL;zero→return0. Otherwise independently reread samebyte and compareUXTB(R5);mismatchR2++modrepeat. Match freshword[R1+8*R2+4]→R0,store[R4],return1.

Zero predicate: freshword[R6]→R0, freshbyte[R6+8]→R1, compute retainedkeybaseR0+=4*R1 modulo;R1=0. Eachiteration independently rereadsbyte[R6+8]countR2;unsignedR1>=R2→return0. Freshbyte[keybase+R1] compareUXTB(R5);mismatchincrementR1andretest. Match independentlyreloadword[R6]→R0, freshword[R0+4*R1]→R0,store[R4],return1. BothreturnsPOP{R4,R5,R6,PC}. No outputwriteonmiss/no nullguards;preserve repeated fresh reads and packedkeybase computedfrominitialcount versus reloadedloopcount. Next48277E belongsanotherhelper. No C,freeze,wholecoverage or equalityclaim.
