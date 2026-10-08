# Size adjustment tail and resource release counter prefix

Partial/unaccepted;100 instructionbytes48426C..4842D0. Continuation48423424Bframe: storeR8(current-oldsize)word[objectR5+8];R0=R4newresource,4D05E4;freshcurrentR1,R0+=R1wrap,storecurrent. FreshhighwaterR0/currentR1,unsignedhigh>=current→freshhighwaterelsefreshcurrent;storehighwater. R3/R2/R1=0,R0=freshobjectword0;4417EE;R0=R4result;POP R4/R5/R6/R7/R8/PC24B. Earlierguardfailure jumpsresultreturnwithoutrelease,operationnull skipscounterupdatesbutreleases.

New48429EPUSH R4/R5/R6/LR16B;R5=entry0object,R4=entry1resource;resourcezero→4842E4unresolved. NonzeroR1=FFFFFFFF,R0=word[object];441C44;result!=1→4842E4. EqualR0=R4,4D05E4→R6size;R1=R4,R0=word[object+4];4D0808ignoredresult;freshcurrentR0, unsignedR6>=R0→4842D4unresolved;elsefreshcurrentR0again,R6=R0-R6wrap. Fallthrough4842D0unresolved. Retaincurrentmutationafterhelperandfreshreads,nohelpercontractassumption. No C,freeze,wholecoverage or equalityclaim.
