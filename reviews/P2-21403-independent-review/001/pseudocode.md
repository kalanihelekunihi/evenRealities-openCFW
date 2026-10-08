# Resource high-water, release and next acquisition prefix

Partial/unaccepted;72 instructionbytes4841C0..484208. Continuation484180frame16B: previousunsignedcomparisoncurrent>highwater→4841C0freshword[object+8]R0;else4841C4freshword[object+12]R0;bothstoreword[object+12]. Entry4841C8 setsR3/R2/R1=0,R0=freshword[object],call4417EE. 4841D4R0=R4resource;4841D6POP16B. Requestzero jumpsdirectPOPwithR0=0;acquirehelperfailurejumpsD4withR4=0 andskiprelease.

New4841D8PUSH R3/R4/R5/R6/R7/LR24B;R6=entry0object,R5=entry1request,R7=entry2,R4=0. RequestzeroR0=0→484232unresolved. NonzeroR1=FFFFFFFF,R0=word[object],441C44;result!=1→484230unresolved. EqualR2=requestR5,R1=R7,R0=word[object+4];4D0744→R4;null→484224unresolved;nonnullfallthrough484208. Helpercontractsnotassumed;exactreleaseguard andfreshhighwaterreads retained. No C,freeze,wholecoverage or equalityclaim.
