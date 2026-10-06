# Final region and cleanup, 0x540842..0x5409C4, 386 bytes

word[SP+4]=0; word[SP+0]=FFFFFFFF
R3=FFFFFFFF; R2=1; R1=1; R0=word[SP+76]; call4B06C0()
R0=FF000000; call522A16()
word[SP+12]=u32(R9+word[SP+44])
word[SP+20]=u32(word[SP+52]-R9)
word[SP+16]=u32(R9+word[SP+48])
R0=word[SP+56]; R9=u32(R0-R9); word[SP+24]=R9
R1=SP+12; R0=SP+60; call540024()
R0=word[SP+16]; R1=u32(R11+1)
if s32(R0)<s32(R1): R0=freshword[SP+16]
else: R0=u32(R11+1)
word[SP+64]=R0
R0=word[SP+24]
if s32(R11)<s32(R0): R11=freshword[SP+24]
word[SP+72]=R11
R2=u32(R4+56); R1=SP+60; R0=SP+28; call450BCC()
if R0==0: goto5408EA
R2=R8; R1=SP+92; R0=SP+28; call450F28()
if R0!=0: goto5408EA

R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0()

5408EA:
R0=byte[SP+80]
if R0==0:
 R0=0; call522A16()
 R0=SP+92; call4515A4(); R4=R0
 R0=SP+92; call451598()
 word[SP+0]=R8; R3=R4; R2=R0
 R1=u32(word[SP+96]-R7); R0=u32(word[SP+92]-R6); call522B30()
54091A:
R0=word[SP+84]; R0=byte[R0+20]
if R0==16: R4=0x501
else: R4=0x504
R0=SP+112; call561810()
R0=SP+112; call5226E8()
R0=SP; R1=u32(R5+32); R2=3; call439BE4()
R1=byte[R5+52]; R0=word[SP+0]; call4B06A8(); R8=R0
R0=freshbyte[R5+52]
if R0==255:
 R1=R4; R0=word[SP+76]; call4B0748()
else:
 R4=R4|08000000; R1=R4; R0=word[SP+76]; call4B0748()
 R0=R8; call513E2E()
540974:
R0=R8; call4B146C()
call4B1548() // inherits previous child's R0 and other caller registers; no reset
R0=SP+44; call4515A4(); R4=R0
R0=SP+44; call451598()
R3=R4; R2=R0
R0=word[SP+48]; R7=u32(R0-R7); R1=R7
R0=word[SP+44]; R6=u32(R0-R6); R0=R6
call522AE0()
call5144FA() // inherits prior return context
R4=R0
R0=R4; call514CF2()
R0=R4; call514D00()
R0=R4; call514384()
R0=word[SP+88]; call44F758()
5409BE:
SP=u32(SP+188)
restore R4,R5,R6,R7,R8,R9,R10,R11,PC from nine consecutive words at SP; SP+=36

Final R0 is the 44F758 child result on normal completed path. Early paths from5400F8 (initial clip failure) and5401FC (acquire rejection afterfree) branch directly to5409BE retaining their child return context. Epilogue skips saved entryR3 by adding188 after184-byte locals, restores other saved registers, and consumes savedLR intoPC. Total frame224 restored. Final clipping mutates R9/R11; previous packet mutates R10, all later restored from entry saves. Stack0 is reused for arguments and then three-byte copy; remaining fourth byte is not assumed zero before subsequent wordload. Repeated alpha loads may differ afterchild effects; no invented saturation here.

Partial; accepted:false. Frame224 of candidate540036 active. u32 wraps each operation; comparisons use signed32. F(x) means transfer wrapped32 bits to S0 and VCVT.F32.S32 into the indicated S register, under architectural rounding/status/enable controls. Opaque children may modify memory; subsequent loads are fresh. Child prototypes, physical rendering, whole-function behavior, faults and concurrent mutation unresolved. Names are inference. No admission, C, freeze or gate changes.
