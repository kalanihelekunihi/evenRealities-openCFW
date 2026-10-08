# Second acquisition tail and size adjustment prefix

Partial/unaccepted;100 instructionbytes484208..48426C. Continuation4841D824Bframe: R0=R4resource,4D05E4;freshcurrentword[objectR6+8]R1,R0+=R1wrap,storecurrent;freshhighwater+12R0,current+8R1,unsignedhigh>=current→freshhighwaterR0elsefreshcurrentR0;storehighwater. At484224R3/R2/R1=0,R0=freshobjectword0;4417EE;484230R0=R4;POP R1(savedentryR3),R4/R5/R6/R7/PC24B. Earlierguardfailure skipsrelease;zero request directPOPresult0.

New484234PUSH R4/R5/R6/R7/R8/LR24B;R5=entry0object,R6=entry1,R7=entry2,R4=0. R1=FFFFFFFF,R0=word[object];441C44;result!=1→484298unresolved. EqualR0=R6,4D05E4→R8oldsize;R2=R7,R1=R6,R0=word[object+4];4D0868→R4;zero→48428Cunresolved. Nonzerofreshcurrentword[object+8]R0,R8=R0-R8oldsizewrap;fallthrough48426Cunresolved. Preserveseparatefreshloads,originalentryR3returnalias andoldsizebeforeoperation. No C,freeze,wholecoverage or equalityclaim.
