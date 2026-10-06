# Fifth region, 0x54055A..0x5405F2, 152 bytes

word[SP+12]=u32(R9+word[SP+44])
word[SP+20]=u32(word[SP+52]-R9)
word[SP+16]=word[SP+48]
word[SP+24]=u32(R9+freshword[SP+48]-1)
R1=SP+12; R0=SP+60; call540024()
R0=word[SP+24]
if s32(R0)<s32(R11): R0=freshword[SP+24]
else: R0=R11
word[SP+72]=R0
R2=u32(R4+56); R1=SP+60; R0=SP+28; call450BCC()
if R0==0: branch5405F2
R2=R8; R1=SP+92; R0=SP+28; call450F28()
if R0!=0: branch5405F2
R0=SP+112; call561810()
R0=u32(R7-word[SP+16]); S0.bits=R0; S1=F(R0)
R0=u32(R6-word[SP+20]); S0.bits=R0; S0=F(R0)
R0=SP+112; call561856()
R0=SP+112; call5226E8()

R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0()
continue5405F2

Partial; accepted:false. Frame224 of candidate540036 active. u32 wraps each operation; comparisons use signed32. F(x) means transfer wrapped32 bits to S0 and VCVT.F32.S32 into the indicated S register, under architectural rounding/status/enable controls. Opaque children may modify memory; subsequent loads are fresh. Child prototypes, physical rendering, whole-function behavior, faults and concurrent mutation unresolved. Names are inference. No admission, C, freeze or gate changes.
