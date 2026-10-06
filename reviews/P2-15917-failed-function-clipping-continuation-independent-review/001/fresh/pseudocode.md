# Clipping setup continuation, 0x5400B8..0x540144

Partial; accepted:false.140bytes continuation within candidate540036..5409C4, frame224 remainsactive. R0 initially retained entryR0, R5=entryR1,R8=entryR2. Ordered:

R1=byte[R5+52];if signed(R1)>=254:R1=255
R4=R0
word[SP+84]=word[R4+72]
R6=word[word[SP+84]+4]
R7=word[freshword[SP+84]+8]
R0=word[SP+84]+4;call451598();word[SP+108]=R0
R0=freshword[SP+84]+4;call4515A4();word[SP+164]=R0
word[SP+76]=word[R4+76]
R2=u32(R4+56);R1=SP+44;R0=SP+168;call450BCC()
if R0==0:branch5409BE // shared epilogue outside this packet
R1=R8;R0=SP+92;call540024()
R2=FFFFFFFF;R1=FFFFFFFF;R0=SP+92;call450B98()
R8=word[R5+28]
R0=SP+92;call451598();R9=R0
R0=SP+92;call4515A4()
if s32(R9)<s32(R0):R0=SP+92;call451598()
else:R0=SP+92;call4515A4()
R1=ASR(R0,1)
if s32(R1)<s32(R8):R8=ASR(R0,1)
continue540144

Children451598/4515A4 have existing geometry dimension map10420; preserve repeated calls (fresh reads) and child R1 effects. R1byte saturation atentry is overwritten by first dimensionchild, not asserted as a retained parameter. Otherchildren450BCC/540024/450B98 contracts remain explicit external packet dependencies; no effects silently assumed. ASR roundsnegativeodd towardnegativeinfinity. No fullfunction return/ABI/semantic closure, physical drawing/alias/fault/concurrency qualification or C/gates.
