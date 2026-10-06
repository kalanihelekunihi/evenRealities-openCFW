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
