# Buffer configuration continuation, 0x5401FE..0x540264

Partial; accepted:false.102bytes continuation of540036 candidate; frame224 active. After prioracquiresuccess:

word[SP+8]=0;word[SP+4]=FFFFFFFF;word[SP+0]=8
R0=word[SP+76];R0=word[R0+64];R3=word[R0+4]>>16
R0=freshword[SP+76];R0=word[R0+64];R2=UXTH(word[R0+4])
R0=freshword[SP+76];R0=word[R0+64];R1=word[R0+16]
R0=1;call4B1298()
word[SP+8]=0;word[SP+4]=FFFFFFFF;word[SP+0]=8
R3=R9;R2=R9;R1=word[SP+88];R0=2;call4B1298()
word[SP+4]=0;word[SP+0]=FFFFFFFF
R3=2;R2=1;R1=1;R0=word[SP+76];call4B06C0()
R3=word[SP+164];R2=word[SP+108];R1=0;R0=0;call4B1516()
continue540264

Stackwords are actual call-context memory; child prototypes/additionalargument consumption remain unresolved. Registers and stackargs explicitly refreshed at shownsites, including three separatepointerchains for firstcall dimensions/backingptr. Child R0results discarded by following overwrite; child memoryeffects not assumedabsent. No completefunction behavior/ABI, C/admission/gates.
