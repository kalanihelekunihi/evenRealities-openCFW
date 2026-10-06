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
