# Dimension clamp, allocation and diagnostic loop, 0x540144..0x5401B6

Partial; accepted:false.114bytes continuation of2446byte rawcandidate540036, frame224active. Ordered:

R9=word[R5+28]
R0=SP+148;call451598();R10=R0
R0=SP+148;call4515A4()
if s32(R10)<s32(R0):R0=SP+148;call451598()
else:R0=SP+148;call4515A4()
R1=ASR(R0,1)
if s32(R1)<s32(R9):R9=ASR(R0,1)
R0=freshword[R5+36];R9=u32(R9+R0)
R0=u32(R9*R9);call44F718();word[SP+88]=R0
R0=freshword[SP+88]
if R0!=0:continue5401B6
word[SP+8]=word[5409C4]
word[SP+4]=word[5409C8]
word[SP+0]=word[5409CC]
R3=word[5409D0];R2=111;R1=word[5409D4];R0=3
call44D25C()
loop5401AC:
 R0=0;R1=FFFFFFFF;word[FFFFFFFF]=0
 branch5401AC

44F718 result used as pointer later; allocation/diagnostic names inferred from zero gate and error path, child semantics separately required. Square/add arithmeticwrap32 with no overflow/sign checks. Failure loop includes unchecked unaligned invalidaddressstore: actual fault/bus outcome depends on memory architecture, not asserted as normal completion. This operation is plausible source of raw Ghidra memory-range error, not established toolrootcause. Literal pool outside rawfunction envelope recorded by references, not code. No FP in this packet, nofullreturn/ABI/hardwarequalification or C/admission/gates.
