# Direct ring command writer, 0x523E92..0x523F0E,124 bytes
PUSH R4,R5,R6,R7,LR20; R4=word[0x52404C]; R3=word[R4]; SP-=4
R2=entryR0; R0=word[R3+16]; R6=word[R4+12]; R5=word[R4+4]; R7=u32(R0+2)
if s32(R6)>=s32(R7): goto523EC2
R7=65536
523EAC:
word[R3+16]=R0; word[R5+(R0<<2)]=R7
R0=freshword[R3+16]; R0=u32(R0+1)
if s32(R0)>=s32(R6): goto523EBE
if R0!=0: goto523EAC
523EBE: R0=0; word[R3+16]=R0
523EC2:
R0=freshword[R3+16]; word[R5+(R0<<2)]=R2
R0=freshword[R3+16]; R0=u32(R0+1)
if s32(R0)>=s32(R6): R0=0
word[R3+16]=R0; word[R5+(R0<<2)]=R1
R0=freshword[R3+16]; R0=u32(R0+1)
if s32(R0)>=s32(R6): R0=0
word[R3+16]=R0
if (R2&FF000000)==0:
 SP+=4; restoreR4,R5,R6,R7,PC; SP+=20; return
R0=R3; call5140EA()
R0=freshword[R4]; R1=word[R4+8]; R2=word[R0+16]
SP+=4; R0=236; R1=u32(R1+(R2<<2))|4
restoreR4,R5,R6,R7,LR; SP+=20; tailbranch514046

Cursorfreshloadsbetweenstores, signedwrappedcapacityandindex checks. Padding65536singlewordsuntilendthenwrap; paircursorpublishbetweencommandandpayload. Highcommandbyte0returnsfinalcursorR0; nonzeroissueschildcontextsubmission then236tailcommandwithpointerlowbit2. Childeffects/lifetime/config and invalidsize/cycle/faultconditions unresolved. Literal52404C outsidecode; argumentsignoredbyinput-pointerhelperonlyifchilddoesit, no silenttailstatus.

Partial; accepted:false. Ordered instructions, wrap32 and signedconditions retained; childcontracts, architecturalfault/alias/concurrentstate/lifetime conditional. No C, admission, freeze, gate or physicalqualification.
