# Center band and edge-loop setup, 0x522C28..0x522C80,88 bytes
R7=R0
CMP R8,0; if signedGT: CMP R9,0
if resultingsignedLE: goto522C6C
R0=3; call514AEC()
if R0==0: goto522C6C
R2=Packed16(R4,R7); R1=260; word[R0]=R1; word[R0+4]=R2
R9=u32(R9+R7); R2=Packed16(R11,R9); R1=264
word[R0+8]=R1; word[R0+12]=R2
R1=word[0x5232CC]; word[R0+16]=R1
R2=word[0x522F18]; R3=word[R2]; R1=word[R3+24]; R1=R1|2; word[R0+20]=R1
522C6C:
R7=R10; R9=R5; R4=0; R5=word[SP+12]
R8=word[SP+8]; R10=word[SP+4]; R6=word[SP]
branch522D98

CenterdrawR9change laterdiscardedbyloopsetup; zeroallocator stillcontinuesedgeconstruction. Commands readcurrentglobalflagsafterearlierstores. Literalpointerdataoutsidecode.

Partial; accepted:false. Candidate522B30 active64byteframe (36saved+28locals), wrapped32 operations, comparisons signedunlessspecified. Packed16(x,y)=(x&FFFF)|u32(y<<16). Child514AEC/514D2C return, memory/global effects unresolved. Staticregionnames inference; no physical rendering, completechildcontract, C, admission or gates.
