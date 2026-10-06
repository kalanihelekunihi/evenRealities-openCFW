# Current buffer detach, 0x5144BA..0x5144FA,64 bytes
PUSH R4,R5 (noLRsave)8
R0=word[0x514B78]; R1=word[R0]; R0=word[R1+4]
if R0==0: goto5144F2
R2=word[R0+20]; R3=word[R0+16]; R4=u32(R2+2)
if s32(R3)>=s32(R4):
 R3=word[R0+8]; R4=327680; R5=0
 word[R3+(R2<<2)]=R4; R3=u32(R3+4); word[R3+(R2<<2)]=R5
 R2=freshword[R0+24]&FFFFFFF7; word[R0+24]=R2
R2=freshword[R0+24]&FFFFFFDF; word[R0+24]=R2
5144F2: R0=0; word[R1+4]=R0; restoreR4,R5; SP+=8; returnviaLR

Markerpair50000,0 maybewrittenwithoutcursoradvance. Capacitysignedwrappedindex+2. Bit3onlyclearwhenmarkerwritten; bit5alwaysclearifbufferexists; contextcurrentpointeralwayscleared. ArgumententryR0ignored, globalcurrentused. GlobalwordR1retainedthroughwrites; aliaswithcontext/backingmayaffecteffectoflaststore. No calls/traps; normalreturn0, LRunchanged.

Partial; accepted:false. Ordered instructions, wrap32 and signedconditions retained; childcontracts, architecturalfault/alias/concurrentstate/lifetime conditional. No C, admission, freeze, gate or physicalqualification.
