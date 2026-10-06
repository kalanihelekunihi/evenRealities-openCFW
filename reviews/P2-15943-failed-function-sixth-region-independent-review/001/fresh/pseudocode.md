# Sixth region, 0x5405F2..0x5406A4, 178 bytes

word[SP+12]=u32(R9+word[SP+44])
word[SP+20]=u32(word[SP+52]-R9)
word[SP+16]=u32(word[SP+56]-R9+1)
word[SP+24]=freshword[SP+56]
R1=SP+12; R0=SP+60; call540024()
R0=u32(R11+1); R1=word[SP+16]
if s32(R0)<s32(R1): R0=freshword[SP+16]
else: R0=u32(R11+1)
word[SP+64]=R0
R2=u32(R4+56); R1=SP+60; R0=SP+28; call450BCC()
if R0==0: branch5406A4
R2=R8; R1=SP+92; R0=SP+28; call450F28()
if R0!=0: branch5406A4
R0=SP+112; call561810()
R0=SP+112; R1=word[0x5409D8]; word[R0+16]=R1
R1=u32(word[SP+20]-R6); S0=F(R1); word[R0+8]=S0.bits
R1=word[SP+16]; R1=u32(R1+R9); R1=u32(R1-1); R1=u32(R1-R7)
S0=F(R1); word[R0+20]=S0.bits
R0=SP+112; call561B38()
R0=SP+112; call5226E8()

R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0()
continue5406A4
Literal5409D8 remains data outside code span.

Partial; accepted:false. Frame224 of candidate540036 active. u32 wraps each operation; comparisons use signed32. F(x) means transfer wrapped32 bits to S0 and VCVT.F32.S32 into the indicated S register, under architectural rounding/status/enable controls. Opaque children may modify memory; subsequent loads are fresh. Child prototypes, physical rendering, whole-function behavior, faults and concurrent mutation unresolved. Names are inference. No admission, C, freeze or gate changes.
