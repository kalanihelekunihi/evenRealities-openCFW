# Object initializer tail and resource acquire counter prefix

Partial/unaccepted;68 instructionbytes48417C..4841C0. Initializercontinuationword[R4object+20]=R5entry1;POP R4/R5/R6/PC16B. R0 remainszero assignedinprecedingfieldstore sequence;noexplicitreturnassignment.

Newentry484180PUSH R4/R5/R6/LR16B;R6=entry0object,R5=entry1request,R4=0. Requestzero→R0=0,branch4841D6unresolved. NonzeroR1=FFFFFFFF,R0=freshword[object];441C44;result!=1→4841D4unresolved. EqualR1=requestR5,R0=freshword[object+4];4D0722→R4;null→4841C8unresolved. NonnullR0=R4;4D05E4→R0;freshword[object+8]R1;R0+=R1wrap,storeobject+8;freshword[object+12]R0,thenfreshword[object+8]R1;unsignedR0>=R1→4841C4unresolved,elsefallthrough4841C0. Exactreads/counterupdate andhelperargs retained,helpercontractsunknown. No C,freeze,wholecoverage or equalityclaim.
