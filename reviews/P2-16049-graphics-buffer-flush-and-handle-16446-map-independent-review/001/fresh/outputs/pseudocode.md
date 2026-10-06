# Buffer flush and handle update, 0x5147B0..0x514846,150 bytes
PUSH R4,LR8; R4=entryR0
if R4==0:
 R0=8192; restoreR4,LR; SP+=8; tailbranch4B127C
R1=byte[R4+24]; R0=word[R4+20]; R2=u32(R1<<26)
if R2 signbit:
 R1=word[R4+44]; R3=SDIV_s32(R0,R1); R0=u32(R0-R1*R3)
 if R0==0: restoreR4,PC; SP+=8; return
else:
 if R0==0: branch514844
R0=R4; call514B7C()
R0=freshbyte[R4+24]; R1=u32(R0<<26)
if R1 signbit==0: goto514826
R0=word[0x514B78]; R2=word[R0]; R1=byte[R2+249]; CMP R1,1
if Z==0:
 R1=word[R4+40]; R2=R1>>2; R0=word[R4+48]; CMP R0,R2
if Z==1: goto51481A
CMP R0,(R1>>1)
if Z==0: R2=u32(R2+(R2<<1)); CMP R0,R2
if Z==1: goto51481A
CMP R0,0
if Z==0:
 R0=word[R4+52]; R1=00FFFFFF; CMP R0,R1
if Z==1: goto51481A
branch51482C
51481A:
R0=word[R4+52]; call523F10()
R0=freshword[R4+52]; word[R4+28]=R0; goto51482C
514826: R0=word[R4+28]; call523F10()
51482C:
R1=word[R4+28]; R0=00FFFFFF; CMP R1,R0
if Z==0: goto514844
call514026() //R0 remains00FFFFFF, notbufferpointer
CMP R0,0
if N==0: R0=FFFFFFFF; word[R4+28]=R0
514844: restoreR4,PC; SP+=8; return

Ringbit5path signedremainder usingSDIV/MLS, notunsignedmodulo; dividezero architectural. Ringhandleupdateconditions quarter/half/threequarter positions or zero or sentinel/currentflag1, allnormalorderedfreshloads. ShortcircuitITflagsretained; nonSshiftsinsideITdon'talterflags. Changedflagafter514B7C respected; global249readbeforecountword40/48. Sentinel00FFFFFF distinguishedfromFFFFFFFF. Child514026 receives sentinel notR1handle; handlewordsetFFFFFFFFonly nonnegativechildresult. NormalR0 varieslatestchild/comparecontext, nofixedsuccess. Literaldataoutsidecode; childfunctionnames notqualifiedhardwareoperation.

Partial; accepted:false. Opaquechildren, architecturefaults, concurrentglobal/lifetime effects conditional; arithmeticwrap32 and orderedfreshloads retained. No C, admission, freeze, gates or physicalqualification.
