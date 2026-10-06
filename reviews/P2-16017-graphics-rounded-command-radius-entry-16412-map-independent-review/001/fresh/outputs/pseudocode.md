# Radius entry and nonpositive-radius rectangle, 0x522B30..0x522BAC,124 bytes
PUSH R4..R11,LR36; R8=entryR2; SP-=28
R2=u32(R8+(R8>>31)); R6=word[SP+64]; R2=ASR32(R2,1)
if s32(R2)<s32(R6): R6=R2
R10=entryR3; R2=u32(R10+(R10>>31)); R2=ASR32(R2,1)
if s32(R2)<s32(R6): R6=R2
R4=entryR0; R5=entryR1
if s32(R6)>0: branch522BAC
CMP R8,0; if signedGT: CMP R10,0
if resultingflags signedLE: branch522DAE
R0=3; call514AEC()
if R0==0: branch522DAE
R2=Packed16(R4,R5); R1=260; word[R0]=R1; word[R0+4]=R2
R5=u32(R5+R10); R4=u32(R4+R8); R2=Packed16(R4,R5)
R1=264; word[R0+8]=R1; word[R0+12]=R2
R1=word[0x5232CC]; word[R0+16]=R1
R2=word[0x522F18]; R3=word[R2]; R1=word[R3+24]; R1=R1|2; word[R0+20]=R1
SP+=28; restoreR4..R11,PC; SP+=36; return

FifthentrySPword radiusclamped to signedhalves towardzero viaexactwrappedsigncorrection. Nonpositive-radiuspath rejects nonpositivewidth/height; R0retainsentryx onearlydimreject, NULLonallocationfailure, allocatedpointeronsuccess. No impliedbooleanreturn. Literaloutsidecode; outputorderingretained.

Partial; accepted:false. Candidate522B30 active64byteframe (36saved+28locals), wrapped32 operations, comparisons signedunlessspecified. Packed16(x,y)=(x&FFFF)|u32(y<<16). Child514AEC/514D2C return, memory/global effects unresolved. Staticregionnames inference; no physical rendering, completechildcontract, C, admission or gates.
