# Ordered matrix inverse candidate, 0x561B38..0x561C64

300 original bytes; partial/accepted:false. R0 ninewordmatrix; no stack/calls. M(a,b)=VMUL.F32, A(a,b,c)=VMLA.F32 accumulator a plus b*c, D(a,b,c)=VMLS.F32 accumulator a minus b*c; keep exact architectural rounding/intermediate/status semantics, not fused or real arithmetic replacements. Fword moves binary32 bits. Ordered operations:
S5=Fword[R0+20]; S0=Fword[R0+12]; S2=Fword[R0+28]; S6=Fword[R0+32]
S11=Fword[R0]; S1=Fword[R0+24]
S7=M(S5,S1); S3=Fword[R0+16]
S8=M(S6,S3); S8=D(S8,S5,S2)
S4=M(S2,S0); S7=D(S7,S6,S0)
S10=Fword[R0+4]; S12=M(S8,S11)
S4=D(S4,S3,S1); S9=Fword[R0+8]
S12=A(S12,S7,S10); S12=A(S12,S4,S9)
S13=VABS.F32(S12); S14=Fword[0x561C64] // raw bits3727C5AD
VCMP.F32(S13,S14); APSR.NZCV=FPSCR.NZCV
if APSR.N==1: R0=FFFFFFFF; return via LR
// BPL proceeds also for unordered comparison (NaN); not a universal finite/singular check.
S13=M(S2,S9); S13=D(S13,S10,S6)
S14=M(S10,S5); S6=M(S11,S6)
S14=D(S14,S3,S9); S6=D(S6,S1,S9)
S1=M(S1,S10); S1=D(S1,S11,S2)
S9=M(S0,S9); S2=M(S11,S3)
S9=D(S9,S11,S5); S2=D(S2,S0,S10)
Fword[R0]=S8; Fword[R0+4]=S13; Fword[R0+8]=S14
Fword[R0+12]=S7; Fword[R0+16]=S6; Fword[R0+20]=S9
Fword[R0+24]=S4; Fword[R0+28]=S1; Fword[R0+32]=S2
S0.bits=3F800000; S0=VDIV.F32(S0,S12)
S1=Fword[R0]; S1=M(S1,S0); Fword[R0]=S1
S2=Fword[R0+4]; S1=Fword[R0+8]
S2=M(S2,S0); S1=M(S1,S0); Fword[R0+4]=S2; Fword[R0+8]=S1
S2=Fword[R0+12]; S1=Fword[R0+16]
S2=M(S2,S0); S1=M(S1,S0); Fword[R0+12]=S2; Fword[R0+16]=S1
S2=Fword[R0+20]; S1=Fword[R0+24]
S2=M(S2,S0); S1=M(S1,S0); Fword[R0+20]=S2; Fword[R0+24]=S1
S2=Fword[R0+28]; S1=Fword[R0+32]
S2=M(S2,S0); S0=M(S1,S0); Fword[R0+28]=S2; Fword[R0+32]=S0
R0=0; return via LR

Literal threshold bits3727C5AD ~1.0000000656873453e-5 is data outside instruction span. Low-magnitude comparison failure returns before any matrix store, but clobbers S registers/FPstatus/APSR and R0. Successful path stores all cofactors BEFORE division/scaling; FP fault during later steps may leave partial transformed matrix. Normal completion returns0, preserving other integer registers/SP; success MOVS0 updates APSR.N0/Z1 retaining comparison C/V. Signaling/quietNaNs, subnormals, infinite/zero determinant, rounding/trap/access and memoryfault/concurrency remain architectural conditions. Matrix inverse name inferred; exact instruction algorithm retained. No C/admission/gates.
