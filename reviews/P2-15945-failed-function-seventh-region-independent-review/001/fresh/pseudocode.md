# Seventh region, 0x5406A4..0x540764, 192 bytes

word[SP+12]=u32(word[SP+52]-R9+1)
word[SP+20]=freshword[SP+52]
word[SP+16]=u32(R9+word[SP+48])
word[SP+24]=u32(word[SP+56]-R9)
R1=SP+12; R0=SP+60; call540024()
R0=word[SP+16]; R1=u32(R11+1)
if s32(R0)<s32(R1): R0=freshword[SP+16]
else: R0=u32(R11+1)
word[SP+64]=R0
R0=word[SP+24]
if s32(R11)<s32(R0): R0=freshword[SP+24]
else: R0=R11
word[SP+72]=R0
R0=word[SP+12]
if s32(R10)<s32(R0): R0=freshword[SP+12]
else: R0=R10
word[SP+60]=R0
R2=u32(R4+56); R1=SP+60; R0=SP+28; call450BCC()
if R0==0: branch540764
R2=R8; R1=SP+92; R0=SP+28; call450F28()
if R0!=0: branch540764
R0=SP+112; call561810()
R0=word[SP+16]; R0=u32(R7-R0); R0=u32(R9+R0); R0=u32(R0-1)
S0.bits=R0; S1=F(R0)
R0=u32(R6-word[SP+12]); S0.bits=R0; S0=F(R0)
R0=SP+112; call561856()
R0=SP+112; call5226E8()

R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0()
continue540764
The SP+72 selection here is a maximum, unlike earlier minima.

Partial; accepted:false. Frame224 of candidate540036 active. u32 wraps each operation; comparisons use signed32. F(x) means transfer wrapped32 bits to S0 and VCVT.F32.S32 into the indicated S register, under architectural rounding/status/enable controls. Opaque children may modify memory; subsequent loads are fresh. Child prototypes, physical rendering, whole-function behavior, faults and concurrent mutation unresolved. Names are inference. No admission, C, freeze or gate changes.
