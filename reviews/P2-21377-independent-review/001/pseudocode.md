# Character output with postincrement padding callbacks

Partial/unaccepted;86 instructionbytes483E98..483EEE continuing88-byteframe483960. R4=1paddingcounter. Flagsbit1setskipprepadding→483EB6;clearcondition483EAE oldR0=R4,R4=old+1wrap, unsignedold<widthR7→spacecallback(R0=32,R1=freshSP40,R2=R6,R3=freshSP44)viaR5;ignorecallbackresult,R6++wrap;repeat. FailedconditionalsoincrementsR4.

483EB6loadfullwordvarargR0[R9],R9+=4wrap;freshR3SP44,R2R6,R1SP40,R0=UXTBvalue;BLXR5ignored,R6++. Flagsbit1clear→483EE6;settrailingcondition483EDE withsameR4 (initial1becauseprepadding skipped):oldR0=R4,R4++wrap;unsignedold<R7→spacecallbackandR6++,repeat. FailedconditionincrementsR4. FinalfreshSP48cursor++store,branch48398E. Width0/1normalcasesemitnopadding, but wrappedcounterbehaviorretained. No C,freeze,wholecoverage or equalityclaim.
