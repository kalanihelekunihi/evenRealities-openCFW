# Byte-key lookup wrapper and five-word descriptor initialization

Partial/unaccepted;54 instructionbytes482946..48297C. Separate482946 PUSH{R7,LR}8bytes,UXTB R1,call482716 lookup withentryR0/entryR2/liveR3;POP{R1,PC} retainshelperR0return,returns savedentryR7 inR1.

482950 PUSH{R3,R4,R5,R6,R7,LR}24bytes;R4=entryR0descriptor,R5=entryR1,R6=entryR2,R7=entryR3. R1=20,R0=R4,call4826FC withliveR2/R3. StorefullR5 at[R4]. If currentR6==0 freshliteral482AD4→R6;else retainR6. FreshwordSP28→R1(sixthentryargument),thenSP24→R0(fifthentryargument). Orderedstores[R4+8]=R6,[R4+12]=R7,[R4+16]=R0,[R4+4]=R1. POP{R0,R4,R5,R6,R7,PC}24bytes returns savedentryR3 viaR0, not fifthargument/helperresult. Preserve no nullguards, initializerhelperclobberboundary, freshstackargumentorder and storeorder. No C,freeze,wholecoverage or equalityclaim.
