# Rounded loop decision and return, 0x522D98..0x522DB4,28 bytes
522D98:
if R9 signbit==0: branch522C80
R9=u32(R9+(R4<<2)); R9=u32(R9+6)
522DA8:
R4=u32(R4+1)
if s32(R7)>=s32(R4): branch522D14
522DAE:
SP+=28; restoreR4..R11,PC; SP+=36; return

Wrappeddecisionupdates, signedloopbound; no assumptionofterminationunderinvalid/overflowinputs. ReturnR0 retainedlastcomparison/emissioncontext, notfixedstatus. R9normalpositivebranchmaydecrementR7via522C84; negativebranchdoesnot. 64byteframereclaimed.

Partial; accepted:false. Candidate522B30 active64byteframe (36saved+28locals), wrapped32 operations, comparisons signedunlessspecified. Packed16(x,y)=(x&FFFF)|u32(y<<16). Child514AEC/514D2C return, memory/global effects unresolved. Staticregionnames inference; no physical rendering, completechildcontract, C, admission or gates.
