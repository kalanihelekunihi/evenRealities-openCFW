# Matrix command encoding, 0x5226E8..0x522848

352 original bytes; partial/accepted:false. PUSH R4/LR8; R4=entryR0 matrix. Fword bits load/store; CMPF performs VCMP.F32 and copies FPSCR.NZCV intoAPSR; subsequent branches test those flags, including unorderedNaN cases.
S1=Fword[0x522918] //33D6BF95 ~positive1e-7
S0=Fword[R4+24]; CMPF(S0,S1)
if N==0: goto5227C2
S2=Fword[0x52291C] //B3D6BF94 ~negative1e-7
CMPF(S0,S2); if N!=V: goto5227C2
S3=Fword[R4+28]; CMPF(S3,S1); if N==0: goto5227C2
CMPF(S3,S2); if N!=V: goto5227C2
S3.bits=BF800000; S0=VADD.F32(S0,S3)
CMPF(S0,S1); if N==0: goto522740
CMPF(S0,S2); if N==V: goto5227A0
522740:
for offset in [0,4,8,12,16,20] in that order:
 S0=Fword[R4+offset]; S1=freshFword[R4+32]
 S1=VDIV.F32(S0,S1); Fword[R4+offset]=S1
5227A0:
R0=6; call514AEC()
if R0==0: goto522846
R1=372; word[R0]=R1
R2=word[R4+20]; R1=360; word[R0+8]=R1; word[R0+4]=R2
R1=word[R4+8]; word[R0+12]=R1
R1=4; goto522800
5227C2:
R0=9; call514AEC()
if R0==0: goto522846
R1=372; word[R0]=R1
R2=word[R4+20]; R1=360; word[R0+8]=R1; word[R0+4]=R2
R1=word[R4+8]; R2=376; word[R0+16]=R2; word[R0+12]=R1
R1=word[R4+24]; R2=380; word[R0+24]=R2; word[R0+20]=R1
R1=word[R4+28]; R2=384; word[R0+32]=R2; word[R0+28]=R1
R1=word[R4+32]; word[R0+36]=R1
R1=10
522800:
R2=352; word[R0+(R1<<2)]=R2
R2=word[R4]; R1=u32(R1+1); R3=356; word[R0+(R1<<2)]=R2
R1=u32(R1+1); word[R0+(R1<<2)]=R3
R2=word[R4+4]; R1=u32(R1+1); R3=364; word[R0+(R1<<2)]=R2
R1=u32(R1+1); word[R0+(R1<<2)]=R3
R2=word[R4+12]; R1=u32(R1+1); R3=368; word[R0+(R1<<2)]=R2
R1=u32(R1+1); word[R0+(R1<<2)]=R3
R2=word[R4+16]; R0=u32(R0+4); word[R0+(R1<<2)]=R2
522846: restoreR4/PC; SP+=8; return

Final R0 successfulallocatedbase+4 (not base); NULL childreturn0. Shortform writes48bytes (6 commandpairs), longform72bytes (9pairs), allocationunits assumedpairs only as inference until514AEC contract recovered. Inputmatrix is mutated before allocation on normalizationpath, so allocationfailure does not undo changes. Fresh divisorloads and encoding loads retain concurrent/alias ordering; no readonlyinput assumption. Comparing bottomleft-minus1 here is actualinstruction, not silently corrected to bottomright-minus1. Constants are data references outsidecode. FPoperation exactrounding/status/trap/NaN/subnormal and global allocator semantics unresolved; no C/admission/gates/physicalqualification.
