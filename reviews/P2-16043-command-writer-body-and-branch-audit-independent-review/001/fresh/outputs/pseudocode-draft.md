# Command writer514846 consolidated draft

Partial; accepted:false, child and architecture conditions remain.

# Command entry and immediate publish, 0x514846..0x5148DA,148 bytes
PUSH R4..R11,LR36; R7=word[0x514B78]; R3=word[R7]; SP-=36
R5=entryR0; R0=word[R3+4]; R6=entryR1
if R0==0:
 R0=0; NOP; R1=R6; R0=R5; call523E92(); R0=0; R0=0; NOP
 SP+=36; restoreR4..R11,PC; SP+=36; return
R1=word[R0+24]; R2=u32(R0+16); R1=R1&FFFFFFF7; word[R0+24]=R1
R1=byte[R2+8]; R4=u32(R1<<26)
if R4 signbit:
 R4=word[R2+28]; R1=word[R2+4]; R12=R4
 R4=u32(R4-R1); R1=SDIV_s32(R1,R12); R4=u32(R12*R1+R4)
else:
 R4=word[R2]; R1=word[R2+4]; R4=u32(R4-R1)
R4=u32(R4+(R4>>31)); R1=freshword[R0+24]; R4=ASR32(R4,1); R12=u32(R1<<26)
if R12 signbit==0: branch5148DA
if s32(R4)<=1:
 R0=0; byte[R3+249]=R0; R1=word[R7]; R0=word[R1+4]; call5147B0()
5148BC:
R0=freshword[R7]; R0=word[R0+4]; R1=word[R0+20]; R2=word[R0+8]
word[R2+(R1<<2)]=R5
R2=freshword[R0+8]; R1=u32(R1+1); word[R2+(R1<<2)]=R6
R1=u32(R1+1); word[R0+20]=R1
SP+=36; restoreR4..R11,PC; SP+=36; return

Bit3clearbeforecapacitytest; bit5ringroute. InitialcontextR3used forbyte249write, freshglobalreloadafterflush. Backingpointerrereadafterfirstcommandstore, cursorpublishafterbothstores. NormalR0 activebufferpointer onpublish; NULLbufferdirectchildpathreturns0regardlesschildresult. Dividezero/trapconditional. No genericcommandreturnstatusassumption.

Partial; accepted:false. Candidate514846 frame72 (36saved+36locals). Arithmetic wraps32, signedconditions retained. Opaquechildren may alter memory/registercallercontext; freshloadsretained, child ABI/architecturefaults/concurrentglobal effects unresolved. No completephysical/ownershipcontract, C, admission or gates.


# Linear capacity routes, 0x5148DA..0x514928,78 bytes
R1=u32(R1<<30)
if R1 signbit: goto5148F4
R0=word[R0+20]; R2=word[R2]; R0=u32(R0+2)
if s32(R2)>=s32(R0): branch5148BC
R0=8
5148EA: call4B127C(); SP+=36; restoreR4..R11,PC; SP+=36; return
5148F4:
R1=word[R0+20]; R3=word[R2]; R1=u32(R1+4)
if s32(R1)<s32(R3): branch5148BC
R1=byte[R2+8]; R3=u32(R1<<26)
if R3 signbit:
 R3=word[R2+28]; R1=word[R2+4]; R2=R3
 R3=u32(R3-R1); R1=SDIV_s32(R1,R2); R3=u32(R2*R1+R3)
else:
 R3=word[R2]; R1=word[R2+4]; R3=u32(R3-R1)
R3=u32(R3+(R3>>31)); R3=ASR32(R3,1); R3=u32(R3-2)
if s32(R3)<=0: branch5149AA
continue514928

Bit1distinguishesfixedcapacityversuslinkedexpansion; signedcapacitycomparisonsincludingindex+2/+4wrapping. Bit5recheckedafterinitialrouteevenifnormalinitiallyfalse, no immutableflagsassumption. Errorpathreturnschildresult. R0 stillactivebufferexceptfixedrouteoverwrites. Activeframe72.

Partial; accepted:false. Candidate514846 frame72 (36saved+36locals). Arithmetic wraps32, signedconditions retained. Opaquechildren may alter memory/registercallercontext; freshloadsretained, child ABI/architecturefaults/concurrentglobal effects unresolved. No completephysical/ownershipcontract, C, admission or gates.


# Padding command loops, 0x514928..0x5149AA,130 bytes
word[SP]=R3; LR=R3&3; R1=65536; R4=0
WLS LR,LR,514950 //skipifzerocount; otherwisearchitecturalcountloop
514938:
R3=word[R0+20]; R2=word[R0+8]; word[R2+(R3<<2)]=R1
R2=freshword[R0+8]; R3=u32(R3+1); word[R2+(R3<<2)]=R4
R3=u32(R3+1); word[R0+20]=R3
LE LR,514938
514950:
LR=word[SP]; LR=LR>>2; WLS LR,LR,5149AA
51495C:
R2=word[R0+20]; R3=word[R0+8]; word[R3+(R2<<2)]=R1
R3=freshword[R0+8]; R2=u32(R2+1); word[R3+(R2<<2)]=R4
R3=freshword[R0+8]; R2=u32(R2+1); word[R0+20]=R2
word[R3+(R2<<2)]=R1
R3=freshword[R0+8]; R2=u32(R2+1); word[R3+(R2<<2)]=R4
R3=freshword[R0+8]; R2=u32(R2+1); word[R0+20]=R2
word[R3+(R2<<2)]=R1
R3=freshword[R0+8]; R2=u32(R2+1); word[R3+(R2<<2)]=R4
R3=freshword[R0+8]; R2=u32(R2+1); word[R0+20]=R2
word[R3+(R2<<2)]=R1
R3=freshword[R0+8]; R2=u32(R2+1); word[R3+(R2<<2)]=R4
R2=u32(R2+1); word[R0+20]=R2
LE LR,51495C
continue5149AA

OriginalWLS/LE instructionsretainedasarchitecturaloperations: countn bodyexecutions, firstloop remainder3, secondfourpairsperiterationquotient4; normaln>0 nofault/concurrentmod producesR3initialpaddingpairs. Intermediatecursorpublishedperpairandfreshbackingloads; cannotreplacewithbulkfill. Lowoverheadloopmetadata/cache/interruptandfinalLRstate remainarchitecturalconditionsratherthanordinaryBNEsubstitution. Primaryreference Armv8-M manual B3.28: https://documentation-service.arm.com/static/66b9cafa32f35b31ceb30a11 . No Unicornloopqualification asserted.

Partial; accepted:false. Candidate514846 frame72 (36saved+36locals). Arithmetic wraps32, signedconditions retained. Opaquechildren may alter memory/registercallercontext; freshloadsretained, child ABI/architecturefaults/concurrentglobal effects unresolved. No completephysical/ownershipcontract, C, admission or gates.


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


# Chain linking and final publication, 0x514A4A..0x514AEC,162 bytes
R0=word[R7]; R0=word[R0+4]
if R0==0: R0=8192; call4B127C(); goto514A62
R1=word[R0+24]|4; word[R0+24]=R1
514A62:
R0=freshword[R7]; R3=240; R1=word[R0+4]; R2=word[R1+20]; R12=word[R1+8]
word[R12+(R2<<2)]=R3
R3=word[R4+12]; R12=freshword[R1+8]; R2=u32(R2+1); word[R12+(R2<<2)]=R3
R12=freshword[R1+8]; R2=u32(R2+1); word[R1+20]=R2
R3=244; word[R12+(R2<<2)]=R3
R3=word[R4+16]; R12=freshword[R1+8]; R2=u32(R2+1); word[R12+(R2<<2)]=R3
R2=u32(R2+1); word[R1+20]=R2; word[R1+32]=R4
if R4==0: R0=8192; goto514AA4
R1=byte[R4+12]; TST R1,7
if Z==0: R0=16384; goto514AA4
R0=word[R0+4]
if R0!=0: call5144BA()
514AC0:
R0=byte[R4+24]; R1=u32(R0<<29)
if R1 signbit==0: goto514AE6
514AC6:
R4=word[R4+32]; R0=byte[R4+24]; R1=u32(R0<<29)
if R1 signbit==0: goto514AE6
R4=word[R4+32]; R0=byte[R4+24]; R1=u32(R0<<29)
if R1 signbit==0: goto514AE6
R4=word[R4+32]; R0=byte[R4+24]; R1=u32(R0<<29)
if R1 signbit==0: goto514AE6
R4=word[R4+32]; R0=byte[R4+24]; R1=u32(R0<<29)
if R1 signbit==1: goto514AC6
514AE6:
R0=freshword[R7]; word[R0+4]=R4; branch5148BC
514AA4: call4B127C(); branch5148BC

Command240 carriesnewnodeword12, command244 carriesword16, thenoldnodeword32linked. Alignmenttestnewnodebyte12&7 AFTERlinkcommandsandcursorpublish; errorreturns toordinarycommandpublish (notrollback). R0globalcontextretainedfromA62 if nochildbeforealignmentpass; word[R0+4] loadedfor5144BAcall. Traversalbit2markreads chainword32withoutNULL/cyclevalidation andunroll4nodes. Publishesfirstunmarkednodeascurrent thenrequestedcommandusingfreshglobal/backing/cursor. No globallysafechildassumptions.

Partial; accepted:false. Candidate514846 frame72 (36saved+36locals). Arithmetic wraps32, signedconditions retained. Opaquechildren may alter memory/registercallercontext; freshloadsretained, child ABI/architecturefaults/concurrentglobal effects unresolved. No completephysical/ownershipcontract, C, admission or gates.
