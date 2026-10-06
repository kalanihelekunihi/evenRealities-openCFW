# Mode bit, centers and buffer acquisition, 0x5401B6..0x5401FE

Partial; accepted:false.72bytes continuation, frame224 active. Enteronly priorpointerSP88NZ. Ordered:

R0=byte[R5+53]&1;byte[SP+80]=R0
R0=SP+44;call451598()
R1=word[SP+44];R2=2;R10=u32(SDIV(s32(R0),2)+R1)
R0=SP+44;call4515A4()
R1=word[SP+48];R2=2;R11=u32(SDIV(s32(R0),2)+R1)
R2=word[SP+108];R1=freshword[SP+108];R0=word[SP+76];call4B0B5A()
R0=UXTB(R0)
if R0==1:continue5401FE
R0=word[SP+88];call44F758()
branch5409BE // epilogue outside packet

FreshSP108 reads into twoargs retained for aliases/ordering; SDIVtrunczero, adds wrap. Child4B0B5A lowbyte1 is onlysuccess value; upperbitsdiscarded. Failure calls44F758 with pointer, result ignoredbybranch; cleanup naming inferred, effects unresolved. Geometryhelpers451598/4515A4 existing10420 packet reused. No standaloneABI/return claim, C/admission/gates.
