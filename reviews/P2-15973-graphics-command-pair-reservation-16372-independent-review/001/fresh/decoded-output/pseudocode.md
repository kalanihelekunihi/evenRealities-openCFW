# Command pair reservation, 0x514AEC..0x514B76

138 original bytes; partial/accepted:false. PUSH R4,R5,R6,LR16; R4=entryR0 request. Ordered original registers/memory:
R5=word[0x514D94]; R2=word[R5]; R0=word[R2+4]
if R0==0:
 R0=128; call4B127C(); R0=0; restoreR4,R5,R6,PC; SP+=16; return
R1=word[R0+24]&FFFFFFF7; word[R0+24]=R1
R1=u32(R0+16); R3=byte[R1+8]; R6=u32(R3<<26)
if R6 signbit==1:
 R3=word[R1+28]; R6=word[R1+4]; R1=R3
 R3=u32(R3-R6); R6=SDIV_s32(R6,R1); R3=u32(R1*R6+R3)
else:
 R3=word[R1]; R1=word[R1+4]; R3=u32(R3-R1)
R3=u32(R3+(R3>>31)); R0=byte[R0+24]; R3=ASR32(R3,1)
R1=u32(R0<<26)
if R1 signbit==1:
 R0=u32(R4+1)
 if s32(R3)<s32(R0):
  R1=0; byte[R2+249]=0
  R0=word[R5]; R0=word[R0+4]; call5147B0()
 goto514B4E
else:
 R3=u32(R3-2)
 if s32(R3)>=s32(R4): goto514B4E
 R0=R4; call514504()
 if R0 signbit==1:
  R0=0; restoreR4,R5,R6,PC; SP+=16; return
514B4E:
R0=freshword[R5]; R1=word[R0+4]; R2=word[R1+20]; R0=word[R1+8]
R0=u32(R0+(R2<<2)); R2=u32(R2+(R4<<1)); word[R1+20]=R2
restoreR4,R5,R6,PC; SP+=16; return

Bit5 controls ring-style vs linear path, bit3 cleared before capacity computation. Wrapped signed SDIV/MLA on ring values retained, including dividezero trapping conditional on architecture; no valid-ring or positive-request assumption. (R3+(R3>>31)) arithmeticshift1 implements signedhalf towardzero only within exactwrapped intermediate semantics. Final pointer is backingbase+oldwordindex*4 and index advances request*2: units commandpairs, but actual capacity/allocationownership and synchronization depend on unresolvedchildren5147B0/514504 and global lifetime. InitialR2 object used for byte249 write beforefresh globalread. Ringflush callresult ignored thenfreshobject/buffer reloaded. Negativecapacityhelper result returnsNULL; any nonnegative proceeds. Literal514D94 is data outsidecode. No C/admission/gates or universal allocator success qualification.
