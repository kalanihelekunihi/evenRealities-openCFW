# Second region transform continuation, 0x540372..0x5403C8

Partial; accepted:false. 86 original bytes; active224-byte frame.

R0=SP+112; R1=word[0x5409D8]; word[R0+16]=R1
R1=word[SP+12]; R1=u32(R1-R6); S0.bits=R1; S0=VCVT.F32.S32(S0); word[R0+8]=S0.bits
R1=word[SP+16]; R1=u32(R1+R9); R1=u32(R1-1); R1=u32(R1-R7)
S0.bits=R1; S0=VCVT.F32.S32(S0); word[R0+20]=S0.bits
R0=SP+112; call561B38()
R0=SP+112; call5226E8()
R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0(); continue5403C8

5409D8 is literal data outside this code span, explicitly recorded by PC-relative reference. Conversion uses signed interpretation of wrapped32 and architectural binary32 conversion with floating-point rounding controls, with floating status/trap/enable conditions unresolved. Child return values overwritten; child contracts and effects unresolved. Join5403C8 also reached from preceding skip branches. No C, admission, gate or physical rendering qualification.
