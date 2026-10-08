# Byte quarter clamp and descriptor clear wrappers

Partial/unaccepted;50 instructionbytes48277E..4827B0. Frameless48277E: UXTB R0,logicalshiftR0right2,UXTB R0again;unsignedR0>=31 setsR0=31,else retained;BXLR. Thus returnmin(UXTB(entryR0)>>2,31), no table/memoryaccess.

48278C PUSH{R7,LR}8bytes;R1=12,call4826FC withentryR0/liveR2/R3;POP{R0,PC} returns savedentryR7, overridinghelperresult. Separate482796 PUSH{R4,LR}8bytes,R4=entryR0;freshbyte[R4+8] compare255. Ifnot255 freshword[R4]→R0,callunresolved44F758 withliveR1/R2/R3. BothpathsR1=12,R0=currentR4,call4826FC;POP{R4,PC} retainsreturnedR0 from4826FC (thathelperreturns itsentryR7). No nullguard or inferredallocation/free contract;recordcallsequenceandfreshreads. No C,freeze,wholecoverage or equalityclaim.
