# Rounded edge emission loop, 0x522C80..0x522D98,280 bytes
522C80:
if R4!=R7: goto522C92
522C84:
R0=u32(R4-R7); R9=u32(R9+(R0<<2)); R9=u32(R9+10); R7=u32(R7-1); branch522DA8
522C92:
R0=3; call514AEC()
if R0==0: goto522CD2
R1=260; word[R0]=R1
R2=UXTH(u32(R5-R4)); R1=u32(R8-R7); R2=R2|u32(R1<<16)
R3=264; word[R0+8]=R3; word[R0+4]=R2
R2=UXTH(u32(R4+R10)); R1=R2|u32(R1<<16); R2=word[0x522F18]
word[R0+12]=R1; R1=word[0x5232CC]; word[R0+16]=R1
R3=word[R2]; R1=word[R3+24]|1; word[R0+20]=R1
522CD2:
R0=3; call514AEC()
if R0==0: goto522C84
R1=260; word[R0]=R1
R2=UXTH(u32(R5-R4)); R1=u32(R7+R6); R2=R2|u32(R1<<16)
R3=264; word[R0+8]=R3; word[R0+4]=R2
R2=UXTH(u32(R4+R10)); R1=R2|u32(R1<<16); R2=word[0x522F18]
word[R0+12]=R1; R1=word[0x5232CC]; word[R0+16]=R1
R3=word[R2]; R1=word[R3+24]|1; word[R0+20]=R1
branch522C84
522D14:
if R4==0: branch522D98
R0=3; call514AEC()
if R0==0: goto522D58
R1=260; word[R0]=R1
R2=UXTH(u32(R5-R7)); R1=u32(R8-R4); R2=R2|u32(R1<<16)
R3=264; word[R0+8]=R3; word[R0+4]=R2
R2=UXTH(u32(R7+R10)); R1=R2|u32(R1<<16); R2=word[0x522F18]
word[R0+12]=R1; R1=word[0x5232CC]; word[R0+16]=R1
R3=word[R2]; R1=word[R3+24]|1; word[R0+20]=R1
522D58:
R0=3; call514AEC()
if R0==0: branch522D98
R1=260; word[R0]=R1
R2=UXTH(u32(R5-R7)); R1=u32(R4+R6); R2=R2|u32(R1<<16)
R3=264; word[R0+8]=R3; word[R0+4]=R2
R2=UXTH(u32(R7+R10)); R1=R2|u32(R1<<16); R2=word[0x522F18]
word[R0+12]=R1; R1=word[0x5232CC]; word[R0+16]=R1
R3=word[R2]; R1=word[R3+24]|1; word[R0+20]=R1
continue522D98

Fouremissionpathsusefreshallocator/globalreads. NULLmaydropindividualedgewithoutundoingpriorcommands; secondedgeNULL stilladvancesdecision522C84. RegistersR4..R10usedafteropaquechildren, childABI isqualificationboundary. Literalreadsoutsidecode.

Partial; accepted:false. Candidate522B30 active64byteframe (36saved+28locals), wrapped32 operations, comparisons signedunlessspecified. Packed16(x,y)=(x&FFFF)|u32(y<<16). Child514AEC/514D2C return, memory/global effects unresolved. Staticregionnames inference; no physical rendering, completechildcontract, C, admission or gates.
