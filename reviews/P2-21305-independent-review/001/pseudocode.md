# Conditional provider and common transform wrappers

Partial/unaccepted;54 instructionbytes482F74..482FAA. Separate482F74 PUSH{R7,LR}8bytes;fullentryR0nonzero calls44DC0A withentryR0/liveR1/R2/R3;zero calls44FA1A withR0=0/liveothers. Bothjoin482F84 call44FE7E withcurrenthelperreturnedR0/liveR1/R2/R3. POP{R1,PC}8bytesretainslasthelperR0,returns savedentryR7inR1. No provider/transformcontractassumed.

482F8A PUSH{R3,R4,R5,LR}16bytes;R5=entryR0;call482F74(R0=R5,liveothers),R4=returnedR0. Zero skipsremainingcalls. Nonzero call44BC3A(R0=R5,liveR1/R2/R3),thenR1=currentR5,R0=currentR4,call482FF2 liveR2/R3. BothpathsPOP{R0,R4,R5,PC}16bytes returns savedentryR3wordoverridinghelperresult;restoresR4/R5. Preserveconditionalcallorderandreturnslotaliases;next482FAAisdistinctroutine. No C,freeze,wholecoverage or equalityclaim.
