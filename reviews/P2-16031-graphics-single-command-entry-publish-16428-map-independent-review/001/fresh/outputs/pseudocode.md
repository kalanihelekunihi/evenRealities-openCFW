# Command entry and immediate publish, 0x514846..0x5148DA,148 bytes
PUSH R4..R11,LR36; R7=word[0x514B78]; R3=word[R7]; SP-=36
R5=entryR0; R0=word[R3+4]; R6=entryR1
if R0==0:
 R0=0; NOP; R1=R6; R0=R5; call523E92(); R0=0; R0=0; NOP
 SP+=36; restoreR4..R11,PC; SP+=36; return
R1=word[R0+24]; R2=u32(R0+16); R1=R1&FFFFFFF7; word[R0+24]=R1
R1=byte[R2+8]; R4=u32(R1<<26)
if R4 signbit:
 R4=word[R2+28]; R1=word[R2+4]; R12=R4
 R4=u32(R4-R1); R1=SDIV_s32(R1,R12); R4=u32(R12*R1+R4)
else:
 R4=word[R2]; R1=word[R2+4]; R4=u32(R4-R1)
R4=u32(R4+(R4>>31)); R1=freshword[R0+24]; R4=ASR32(R4,1); R12=u32(R1<<26)
if R12 signbit==0: branch5148DA
if s32(R4)<=1:
 R0=0; byte[R3+249]=R0; R1=word[R7]; R0=word[R1+4]; call5147B0()
5148BC:
R0=freshword[R7]; R0=word[R0+4]; R1=word[R0+20]; R2=word[R0+8]
word[R2+(R1<<2)]=R5
R2=freshword[R0+8]; R1=u32(R1+1); word[R2+(R1<<2)]=R6
R1=u32(R1+1); word[R0+20]=R1
SP+=36; restoreR4..R11,PC; SP+=36; return

Bit3clearbeforecapacitytest; bit5ringroute. InitialcontextR3used forbyte249write, freshglobalreloadafterflush. Backingpointerrereadafterfirstcommandstore, cursorpublishafterbothstores. NormalR0 activebufferpointer onpublish; NULLbufferdirectchildpathreturns0regardlesschildresult. Dividezero/trapconditional. No genericcommandreturnstatusassumption.

Partial; accepted:false. Candidate514846 frame72 (36saved+36locals). Arithmetic wraps32, signedconditions retained. Opaquechildren may alter memory/registercallercontext; freshloadsretained, child ABI/architecturefaults/concurrentglobal effects unresolved. No completephysical/ownershipcontract, C, admission or gates.
