# Cached graphics state update, 0x4B06C0..0x4B0730,112 bytes
PUSH R4,R5,R6,R7,R8,LR24.
R4=entryR0; R6=entryR1; R7=entryR2; R8=entryR3
if R4==0: call4C791A(); R4=R0
R0=UXTB(word[SP+28]); R5=SXTB(byte[SP+24])
if R0!=0: goto4B070C
R0=word[R4+80]; if R6!=R0: goto4B070C
R0=SXTB(R7); R1=SXTB(byte[R4+84]); if R0!=R1: goto4B070C
R0=SXTB(R8); R1=SXTB(byte[R4+85]); if R0!=R1: goto4B070C
R0=SXTB(R5); R1=SXTB(byte[R4+86]); if R0==R1: goto4B072C
4B070C:
R3=SXTB(R5); R2=SXTB(R8); R1=SXTB(R7); R0=R6; call513924()
word[R4+80]=R6; byte[R4+84]=UXTB(R7); byte[R4+85]=UXTB(R8); byte[R4+86]=UXTB(R5)
4B072C: restore R4..R8,PC; SP+=24; return

Fifth argument entrySP lowbyte signed, sixthargument entrySP+4 lowbyte force. Zero force plus equal cache bypasseschild, retaining finalcomparisonR0 signedfifthbyte, notfixedsuccess. UpdatedpathreturnschildR0 and publishes cache regardlesschildresult. Defaultobject getter result notNULLchecked. All cache loads orderedshortcircuit; forcewordloaded beforefifthbyte. No formalchildcontract.

Partial; accepted:false. Original instruction bytes; opaque children supply return/register/memory effects. Aliasing, fault and concurrentglobal effects remain conditional; names inferred. No C, admission, freeze or gates.
