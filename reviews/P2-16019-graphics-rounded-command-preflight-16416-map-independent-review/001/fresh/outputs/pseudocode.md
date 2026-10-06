# Rounded command count and setup, 0x522BAC..0x522C28,124 bytes
R9=u32(R6<<1); R0=0; R2=R6; R3=u32(3-R9); R9=u32(R10-R9)
word[SP+20]=R2; word[SP+16]=R3
if s32(R9)<=0: R7=0; R1=0
else: R7=1; R1=3
branch522BD4
522BD0: if R0!=0: R1=u32(R1+6)
522BD4:
if R3 signbit==1:
 R3=u32(R3+(R0<<2)); R3=u32(R3+6)
else:
 if R0!=R2: R1=u32(R1+6)
 R12=u32(R0-R2); R3=u32(R3+(R12<<2)); R3=u32(R3+10); R2=u32(R2-1)
R0=u32(R0+1)
if s32(R2)>=s32(R0): goto522BD0
R0=R1; call514D2C()
if R0 signbit==1: branch522DAE
R1=u32(R6+R4); word[SP+12]=R1
R11=u32(R8+R4); R1=u32(R11-R6)
R0=u32(R6+R5); R5=u32(R5+R10); R5=u32(R5-R6); R5=u32(R5-1)
R1=u32(R1-1); word[SP]=R5; word[SP+8]=R0; word[SP+4]=R1
R10=word[SP+20]; R5=word[SP+16]
if R7==0: branch522C6C
continue522C28

Preflightloopupdateswrappedsigneddecision/count, no abstractradiusiterationsoroverflowtermination guarantee. Negativechildresultskipsevenifpartiallysideeffecting; nonnegativechildresultcontinues. Localsreloadafterchildmayreflecteffects; activeframe64.

Partial; accepted:false. Candidate522B30 active64byteframe (36saved+28locals), wrapped32 operations, comparisons signedunlessspecified. Packed16(x,y)=(x&FFFF)|u32(y<<16). Child514AEC/514D2C return, memory/global effects unresolved. Staticregionnames inference; no physical rendering, completechildcontract, C, admission or gates.
