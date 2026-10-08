# Empty predicate and dequeue entry 0x469C98..0x469CE4

Partial/unaccepted;76instructionbytes. Completeleaf469C98..469CAC:R0literal46A824;freshunsignedhalf[R0+132] ->R0; FULLzero returns1,nonzero0;BXLR,noframeorchildcall.

469CAC PUSH R4/R5/R6 creates12frame,LRunchanged. FULLR0destinationzero orlow16R1requestedlengthzero setsR0=NOT2=0xFFFFFFFD ->469D20 outsidechunk. OtherwiseR3=literal46A824;freshunsignedhalf[R3+132] ->R2;zero setsR0=0 ->469D20. NonzeroR2=low16R1;SECONDfreshunsignedhalf[R3+132] ->R4;unsignedR2<R4 skipsclamp469CE0,retainingFULLoriginalR1. OtherwiseTHIRDfreshunsignedhalf[R3+132] ->R1, replacingrequestedlengthwithcurrentcount. R2index=0;branch469D10 outsidechunklooptest. Distinctcountreads maydiffer; no cachedminreplacement. Loopuseslow16lengthaslatercodewillestablish. Preserveglobalinvariantsasunknown anddestinationaliaspossibility; no C/freeze/wholefunctionclaim.
