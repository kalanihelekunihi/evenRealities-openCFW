# Guarded diagnostic entry 0x469388..0x469400

Partial/unaccepted;120 instruction bytes. PUSH R0/R1/R2/R3/R4/LR creates24-byte frame; SP0/4/8/12 original R0/1/2/3, SP16 savedR4,SP20 LR. Load R0=literal469B44 then unsignedbyte[R0]; nonzero branches46946C outsidechunk. Zero calls46919E withliveargs; R4=fullreturnedbool.

Fresh43D0CE bit1 enables diagnostic. SetR0=R4 then low8R0, leavingR4 intact; byte nonzero R0=ADDRESS469578 viaADR, zero R0=ADDRESS46957C. Store selectedaddressSP8, literal469B68 atSP4,141 atSP0. R3=literal469B6C,R2=literal469B38,R1=literal469B3C,R0=4 ->43D574.

Separatefresh43D0CE bit0 or conditional thirdfreshbit2 enables secondarydiagnostic. Testlow8R4 viaR0 temporaryagain. Nonzero R3=ADDRESS469578, zeroR3=ADDRESS46957C; these are immediatePC-relative addresses, not worddereferences. R1=literal469B70,R2=R1,R0=0x10400000 ->43CE9E. At4693FA truncateR4 inplacelow8; zero fallsoutsidechunk469400, nonzero branches469408. SavedargumentsSP0/4/8 may have been overwritten by diagnosticline/context/address; SP12 preserved inthischunk. Childcontracts anddata semantics unresolved, no C/freeze/runtimeclaim.
