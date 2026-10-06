# Backing descriptor construction, 0x514070..0x5140C6,86 bytes
PUSH entryR0,R1,R2,R3,R4,R5,R6,LR32
R5=entryR0 destination; R4=entryR1 selector; R6=entryR2 requestedbytes
R0=0; R0=R4; call514050()
R1=byte[R0+24]
if R1!=0:
 R6=u32(R6+31)&FFFFFFE0; R2=32; R1=R6; call4841D8()
else:
 if R4 in {0,1,2}: R2=8; R1=R6; call4841D8()
 else: R1=R6; call484180()
word[SP+8]=R0; word[SP+12]=R0; word[SP]=R6; word[SP+4]=R4
R0=R5; R1=SP; R2=16; call439C04()
POP R0,R1,R2,R3,R4,R5,R6,PC; SP+=32; return

AllocatorR0still514050returnedcontextuntilchild, noselectorcontextreplacement. Localdescriptor[size,selector,allocatedptr,allocatedptr] copied16bytes toentrydestination. FinalPOPnormallyR0actualsize/R1selector/R2ptr/R3ptr, notcopyresult; alias/childwritescanaltertheseactualstackslots. 32bytealignmentwrapcanproduce0, noallocationNULLvalidation beforedescriptorcopy. Alignment8forselectors0/1/2whencontextbyte24zero. Ownership/lifetime unresolved.

Partial; accepted:false. Ordered instructions, wrap32 and signedconditions retained; childcontracts, architecturalfault/alias/concurrentstate/lifetime conditional. No C, admission, freeze, gate or physicalqualification.
