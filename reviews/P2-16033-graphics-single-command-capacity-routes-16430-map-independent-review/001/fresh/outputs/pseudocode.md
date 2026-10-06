# Linear capacity routes, 0x5148DA..0x514928,78 bytes
R1=u32(R1<<30)
if R1 signbit: goto5148F4
R0=word[R0+20]; R2=word[R2]; R0=u32(R0+2)
if s32(R2)>=s32(R0): branch5148BC
R0=8
5148EA: call4B127C(); SP+=36; restoreR4..R11,PC; SP+=36; return
5148F4:
R1=word[R0+20]; R3=word[R2]; R1=u32(R1+4)
if s32(R1)<s32(R3): branch5148BC
R1=byte[R2+8]; R3=u32(R1<<26)
if R3 signbit:
 R3=word[R2+28]; R1=word[R2+4]; R2=R3
 R3=u32(R3-R1); R1=SDIV_s32(R1,R2); R3=u32(R2*R1+R3)
else:
 R3=word[R2]; R1=word[R2+4]; R3=u32(R3-R1)
R3=u32(R3+(R3>>31)); R3=ASR32(R3,1); R3=u32(R3-2)
if s32(R3)<=0: branch5149AA
continue514928

Bit1distinguishesfixedcapacityversuslinkedexpansion; signedcapacitycomparisonsincludingindex+2/+4wrapping. Bit5recheckedafterinitialrouteevenifnormalinitiallyfalse, no immutableflagsassumption. Errorpathreturnschildresult. R0 stillactivebufferexceptfixedrouteoverwrites. Activeframe72.

Partial; accepted:false. Candidate514846 frame72 (36saved+36locals). Arithmetic wraps32, signedconditions retained. Opaquechildren may alter memory/registercallercontext; freshloadsretained, child ABI/architecturefaults/concurrentglobal effects unresolved. No completephysical/ownershipcontract, C, admission or gates.
