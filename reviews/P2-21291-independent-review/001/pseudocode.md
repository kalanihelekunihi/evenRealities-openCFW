# Node-chain wrapping count helper

Partial/unaccepted;32 instructionbytes482D02..482D22. PUSH{R3,R4,R5,LR}16bytes;R4=entryR0descriptor,R5=0. R0=R4,call482CD8 withliveR1/R2/R3 (nullguardedheadaccessor). Initiallybranch482D1A. WhilefullreturnedR0nonzero:incrementR5mod2^32,R1=currentnodeR0,R0=R4,call482CF0 withliveR2/R3(computednextaccessor),retestreturnedR0. ZeroendsR0=R5;POP{R1,R4,R5,PC}16bytes,R1=savedentryR3. No cycle,overflow,membershipguard;null descriptorcounts0throughheadhelper. Preserve freshlinkreads throughhelper and32-bit wrapping count; no C,freeze,wholecoverage or equalityclaim.
