# First region transform continuation, 0x5402C8..0x540308

Partial; accepted:false. 64 original bytes, active 224-byte frame of candidate540036. Ordered register operations:

R0=u32(R7-word[SP+16]); S0.bits=R0; S1=VCVT.F32.S32(S0)
R0=u32(R6-word[SP+12]); S0.bits=R0; S0=VCVT.F32.S32(S0)
R0=SP+112; call561856()
R0=SP+112; call5226E8()
R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0(); continue540308

Conversions reinterpret wrapped subtraction as signed32 before conversion to binary32; they do not convert an unbounded signed difference. VCVT.F32.S32 follows architectural floating-point rounding controls; floating exception/status and enable/trap state remain architectural conditions. S0/S1 are explicit call context, without inventing a child prototype or assuming child preservation. Child memory effects unresolved. Registers loaded after both transform calls reflect potentially changed local rectangle words. Join540308 also receives skipped-region branches from prior packet. No whole-function, physical rendering, admission, C or gates.
