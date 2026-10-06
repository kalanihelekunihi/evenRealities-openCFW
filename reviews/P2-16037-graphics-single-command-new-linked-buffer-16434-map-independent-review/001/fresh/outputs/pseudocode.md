# Linked buffer construction, 0x5149AA..0x514A4A,160 bytes
R4=word[R0+32]
if R4!=0: branch514A4A
R0=60; call51416C(); R4=R0
if R4==0: R0=16; branch5148EA
R2=1024; R1=0; R0=SP+16; call514070()
R1=SP+16; loadR2,R3,R12,LR fromword[R1+0,+4,+8,+12]
R0=SP; R8=SP+16; storeR2,R3,R12,LR toword[R0+0,+4,+8,+12]
R0=word[R0+8]; NOP
R1=SP; loadR2,R3,R12,LR fromword[R1+0,+4,+8,+12]
R0=SP+16; storeR2,R3,R12,LR toword[R0+0,+4,+8,+12]
loadR1,R9,R10,R11 fromword[R8+0,+4,+8,+12]
R0=word[SP]; R2=ASR32(R0,2); R0=u32(R0+(R2>>29))
storeR1,R9,R10,R11 toword[R4+0,+4,+8,+12]
R1=2; R0=ASR32(R0,3); R0=u32(R0<<1); word[R4+16]=R0
R0=0; word[R4+20]=R0
R0=FFFFFFFF; word[R4+28]=R0; word[R4+52]=R0; word[R4+56]=R0; word[R4+24]=R1
R0=word[R4+8]; R1=0
word[R4+32]=R1; word[R4+36]=R1; word[R4+40]=R1; word[R4+44]=R1; word[R4+48]=R1
if R0==0:
 R0=16; call4B127C(); R0=R4; call514178()
 SP+=36; restoreR4..R11,PC; SP+=36; return
R1=word[R7]; R2=word[R1+4]; R0=word[R2+36]
if R0!=0: R2=R0
word[R4+36]=R2
R0=freshword[R1+4]; R1=word[R0+24]&FFFFFFF3; word[R4+24]=R1
continue514A4A

Helper60byteobject and1024configurationcontracts unresolved; no genericmalloc assumptions. Exactduplicated16bytecopies and deadR0load/NOP retained. CapacityfromwrappedwordSPsigncorrectdivision8 then*2. Initialflags2 overwrittenbycurrentbufferflagsmaskedbits2/3, globalcurrentreloadandparentword36conditional. Constructionmaypublishpartialobject beforelaterfailure; backingNULLpatherrorthenfreechildreturnretained.

Partial; accepted:false. Candidate514846 frame72 (36saved+36locals). Arithmetic wraps32, signedconditions retained. Opaquechildren may alter memory/registercallercontext; freshloadsretained, child ABI/architecturefaults/concurrentglobal effects unresolved. No completephysical/ownershipcontract, C, admission or gates.
