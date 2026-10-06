# Pair-count capacity preflight, 0x514D2C..0x514D92,102 bytes
R1=word[0x514D94]; PUSH R4,R6,LR12; R2=word[R1]; SP-=4; R1=word[R2+4]
if R1==0:
 R0=128; call4B127C(); R0=FFFFFFFE; SP+=4; restoreR4,R6,PC; SP+=12; return
R2=word[R1+24]; R3=u32(R2<<26) //LSLSsetsN
if N==1: goto514D7E
R3=word[R1+20] //doesnotchangeN
if N==0: goto514D60
//retainrawunreachablearmunderunchangedarchitecturalflags
R1=word[R1+44]; R4=u32(R1-R3); R6=SDIV_s32(R3,R1); R3=R4; R3=u32(R1*R6+R3); goto514D64
514D60: R1=word[R1+16]; R3=u32(R1-R3)
514D64: R3=u32(R3+(R3>>31))
CMP signed R0,ASR32(R3,1)
if signedLT: goto514D7E
R1=u32(R2<<30) //LSLSbit1intoN
if N==0: goto514D84
call514504(); CMP R0,0
if N==1: R0=16 //conditionalMOVdoesnotchangeNinIT
if N==1: goto514D86
514D7E: R0=0; SP+=4; restoreR4,R6,PC; SP+=12; return
514D84: R0=8
514D86: call4B127C(); R0=FFFFFFFF; SP+=4; restoreR4,R6,PC; SP+=12; return

Ringbit5immediate0return, noreservationmutation. Linearrequestedcountstrictlylessremainingpaircount=>0 (equalitytriggersgrowth/error). Grownegative=>record16returnFFFFFFFF; fixedexhaustion=>record8returnFFFFFFFF; NULLbufferrecord128returnFFFFFFFE. RawringmatharmafterLDRexistsbutprecedingbit5branchmakesitunreachablewhenflagsrestoredunchanged; don'tsilentlydeleteit. No genericallocatorresultsemantics; preflightchildmaymutatecapacity.

Partial; accepted:false. Ordered instructions, wrap32 and signedconditions retained; childcontracts, architecturalfault/alias/concurrentstate/lifetime conditional. No C, admission, freeze, gate or physicalqualification.
