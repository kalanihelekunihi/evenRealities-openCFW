# Third region continuation, 0x5403C8..0x54049A

210 original bytes. Ordered register/memory operations:

word[SP+12]=word[SP+44]
R0=freshword[SP+44]; word[SP+20]=u32(R9+R0-1)
R0=word[SP+56]; word[SP+16]=u32(R0-R9+1)
word[SP+24]=freshword[SP+56]
R1=SP+12; R0=SP+60; call540024()
R0=u32(R11+1); R1=word[SP+16]
if s32(R0)<s32(R1): R0=freshword[SP+16]
else: R0=u32(R11+1)
word[SP+64]=R0
R0=word[SP+20]; R1=u32(R10-1)
if s32(R0)<s32(R1): R0=freshword[SP+20]
else: R0=u32(R10-1)
word[SP+68]=R0
R2=u32(R4+56); R1=SP+60; R0=SP+28; call450BCC()
if R0==0: branch54049A
R2=R8; R1=SP+92; R0=SP+28; call450F28()
if R0!=0: branch54049A
R0=SP+112; call561810()
S0.bits=BF800000; word[SP+112]=S0.bits
R0=SP+112; word[R0+16]=S0.bits
R1=word[SP+12]; R1=u32(R1+R9); R1=u32(R1-1); R1=u32(R1-R6)
S0=F(R1); word[R0+8]=S0.bits
R1=word[SP+16]; R1=u32(R1+R9); R1=u32(R1-1); R1=u32(R1-R7)
S0=F(R1); word[R0+20]=S0.bits
R0=SP+112; call561B38()
R0=SP+112; call5226E8()
R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0(); continue54049A

Signed selection uses wrapped R10-1 and R11+1, not unbounded min/max. BF800000 is immediate binary32 negative one. Geometry and region names are inference only.

For each shown conversion F(x), transfer u32(x) bits into S0 then execute VCVT.F32.S32 S0,S0; signed32 interpretation and architectural floating-point rounding/status controls apply. u32 wraps each arithmetic operation. Children are opaque, may modify memory; loads following a child are fresh. Frame224 remains active. This packet is partial/accepted:false, no whole-function or physical-rendering qualification, no admission, C or gates.
