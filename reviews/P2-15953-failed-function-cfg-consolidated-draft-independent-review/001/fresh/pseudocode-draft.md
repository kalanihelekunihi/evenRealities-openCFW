# Candidate540036 consolidated pseudocode draft

Partial; accepted:false. Locked main image; raw discovered envelope2446bytes. This concatenation preserves ordered packet pseudocode and unresolved child/architectural boundaries. Independent review bindings are not promoted by concatenation.

# Failed raw function coordinate preparation prefix, 0x540036..0x540078

Partial; accepted:false.66 exact original instruction bytes. This is only the entry prefix of raw discovered candidate540036..5409C4 (2446bytes), not a complete function. PUSH R3-R11/LR consumes40bytes, then SUBSP184: total224. R5=entryR1, R8=entryR2; R0 untouched in this prefix. All word reads below occur in stated order, arithmetic wraps32bits:

R2=word[R8];R1=word[R5+44];R2=u32(R1+R2);R1=freshword[R5+40];R2=u32(R2-R1);word[SP+148]=R2
R2=word[R8+8];R1=freshword[R5+44];R2=u32(R1+R2);R1=freshword[R5+40];R2=u32(R1+R2);word[SP+156]=R2
R2=word[R8+4];R1=word[R5+48];R2=u32(R1+R2);R1=freshword[R5+40];R2=u32(R2-R1);word[SP+152]=R2
R2=word[R8+12];R1=freshword[R5+48];R2=u32(R1+R2);R1=freshword[R5+40];R2=u32(R1+R2);word[SP+160]=R2
continue at540078 with224byte frame active

No validation before these reads, no childcalls or FP in prefix; stack stores and repeated loads preserve aliases/fault/order effects. Inputpointees unnamed; coordinate terminology is inferred from symmetric additions/subtractions and not a physical UI contract. The extent outside this prefix must be recovered independently:2446-66=2380bytes in raw candidate, whose discovery boundaries/semantics remain unreviewed. Raw Ghidra export failed with memory-range error; prefix itself decodes normally. No complete ABI/return/exception behavior claimed. No C/admission/freeze/gates.


# Expanded bounds continuation, 0x540078..0x5400B8

Partial; accepted:false.64 bytes of candidate540036..5409C4, not standalone. Entry frame224 active; R5/R8 from previous prefix. Repeated ordered computations:

R2=word[SP+148];R1=SDIV(s32(word[R5+36]),2);R3=2;R2=u32(R2-R1-1);word[SP+44]=R2
R2=word[SP+156];R1=SDIV(s32(freshword[R5+36]),2);R3=2;R2=u32(R1+R2+1);word[SP+52]=R2
R2=word[SP+152];R1=SDIV(s32(freshword[R5+36]),2);R3=2;R2=u32(R2-R1-1);word[SP+48]=R2
R2=word[SP+160];R1=SDIV(s32(freshword[R5+36]),2);R3=2;R2=u32(R1+R2+1);word[SP+56]=R2
continue5400B8

Signed division truncates towardzero, unlike arithmetic shift for negative oddvalues; denominator2 nonzero. All subsequent additions/subtractions wrap32. R0 unchanged; R1/R2/R3 finalscratch as above, no child/extraSPchange. Repeatedpointee loads not collapsed. Fullfunction bounds/ABI/fault/alias/concurrency unresolved; no C/admission/gates.


# Clipping setup continuation, 0x5400B8..0x540144

Partial; accepted:false.140bytes continuation within candidate540036..5409C4, frame224 remainsactive. R0 initially retained entryR0, R5=entryR1,R8=entryR2. Ordered:

R1=byte[R5+52];if signed(R1)>=254:R1=255
R4=R0
word[SP+84]=word[R4+72]
R6=word[word[SP+84]+4]
R7=word[freshword[SP+84]+8]
R0=word[SP+84]+4;call451598();word[SP+108]=R0
R0=freshword[SP+84]+4;call4515A4();word[SP+164]=R0
word[SP+76]=word[R4+76]
R2=u32(R4+56);R1=SP+44;R0=SP+168;call450BCC()
if R0==0:branch5409BE // shared epilogue outside this packet
R1=R8;R0=SP+92;call540024()
R2=FFFFFFFF;R1=FFFFFFFF;R0=SP+92;call450B98()
R8=word[R5+28]
R0=SP+92;call451598();R9=R0
R0=SP+92;call4515A4()
if s32(R9)<s32(R0):R0=SP+92;call451598()
else:R0=SP+92;call4515A4()
R1=ASR(R0,1)
if s32(R1)<s32(R8):R8=ASR(R0,1)
continue540144

Children451598/4515A4 have existing geometry dimension map10420; preserve repeated calls (fresh reads) and child R1 effects. R1byte saturation atentry is overwritten by first dimensionchild, not asserted as a retained parameter. Otherchildren450BCC/540024/450B98 contracts remain explicit external packet dependencies; no effects silently assumed. ASR roundsnegativeodd towardnegativeinfinity. No fullfunction return/ABI/semantic closure, physical drawing/alias/fault/concurrency qualification or C/gates.


# Dimension clamp, allocation and diagnostic loop, 0x540144..0x5401B6

Partial; accepted:false.114bytes continuation of2446byte rawcandidate540036, frame224active. Ordered:

R9=word[R5+28]
R0=SP+148;call451598();R10=R0
R0=SP+148;call4515A4()
if s32(R10)<s32(R0):R0=SP+148;call451598()
else:R0=SP+148;call4515A4()
R1=ASR(R0,1)
if s32(R1)<s32(R9):R9=ASR(R0,1)
R0=freshword[R5+36];R9=u32(R9+R0)
R0=u32(R9*R9);call44F718();word[SP+88]=R0
R0=freshword[SP+88]
if R0!=0:continue5401B6
word[SP+8]=word[5409C4]
word[SP+4]=word[5409C8]
word[SP+0]=word[5409CC]
R3=word[5409D0];R2=111;R1=word[5409D4];R0=3
call44D25C()
loop5401AC:
 R0=0;R1=FFFFFFFF;word[FFFFFFFF]=0
 branch5401AC

44F718 result used as pointer later; allocation/diagnostic names inferred from zero gate and error path, child semantics separately required. Square/add arithmeticwrap32 with no overflow/sign checks. Failure loop includes unchecked unaligned invalidaddressstore: actual fault/bus outcome depends on memory architecture, not asserted as normal completion. This operation is plausible source of raw Ghidra memory-range error, not established toolrootcause. Literal pool outside rawfunction envelope recorded by references, not code. No FP in this packet, nofullreturn/ABI/hardwarequalification or C/admission/gates.


# Mode bit, centers and buffer acquisition, 0x5401B6..0x5401FE

Partial; accepted:false.72bytes continuation, frame224 active. Enteronly priorpointerSP88NZ. Ordered:

R0=byte[R5+53]&1;byte[SP+80]=R0
R0=SP+44;call451598()
R1=word[SP+44];R2=2;R10=u32(SDIV(s32(R0),2)+R1)
R0=SP+44;call4515A4()
R1=word[SP+48];R2=2;R11=u32(SDIV(s32(R0),2)+R1)
R2=word[SP+108];R1=freshword[SP+108];R0=word[SP+76];call4B0B5A()
R0=UXTB(R0)
if R0==1:continue5401FE
R0=word[SP+88];call44F758()
branch5409BE // epilogue outside packet

FreshSP108 reads into twoargs retained for aliases/ordering; SDIVtrunczero, adds wrap. Child4B0B5A lowbyte1 is onlysuccess value; upperbitsdiscarded. Failure calls44F758 with pointer, result ignoredbybranch; cleanup naming inferred, effects unresolved. Geometryhelpers451598/4515A4 existing10420 packet reused. No standaloneABI/return claim, C/admission/gates.


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


# First region clip continuation, 0x540264..0x5402C8

Partial; accepted:false.100bytes continuation, frame224active. Ordered wrapped expressions and childcalls:

word[SP+20]=word[SP+52]
R0=freshword[SP+52];R0=u32(R0-R9);R0=u32(R0+1);word[SP+12]=R0
word[SP+16]=word[SP+48]
R0=freshword[SP+48];R0=u32(R9+R0);R0=u32(R0-1);word[SP+24]=R0
R1=SP+12;R0=SP+60;call540024()
R0=word[SP+12]
if s32(R10)<s32(R0):R0=freshword[SP+12]
else:R0=R10
word[SP+60]=R0
R0=word[SP+24]
if s32(R0)<s32(R11):R0=freshword[SP+24]
else:R0=R11
word[SP+72]=R0
R2=u32(R4+56);R1=SP+60;R0=SP+28;call450BCC()
if R0==0:branch540308
R2=R8;R1=SP+92;R0=SP+28;call450F28()
if R0!=0:branch540308
R0=SP+112;call561810()
continue5402C8

Max/min comparisons signed; repeatedloadsaftercompare retained, not collapsed into immutableminmax. Copy/clipping/geometry initialization names inference only; opaque childmemoryeffects and exactcontracts unresolved. Both skipbranches joinoutsidepacket at540308. No fullfunction return/ABI or physicaldrawing/alias/fault/concurrency qualification, no C/gates.


# First region transform continuation, 0x5402C8..0x540308

Partial; accepted:false. 64 original bytes, active 224-byte frame of candidate540036. Ordered register operations:

R0=u32(R7-word[SP+16]); S0.bits=R0; S1=VCVT.F32.S32(S0)
R0=u32(R6-word[SP+12]); S0.bits=R0; S0=VCVT.F32.S32(S0)
R0=SP+112; call561856()
R0=SP+112; call5226E8()
R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0(); continue540308

Conversions reinterpret wrapped subtraction as signed32 before conversion to binary32; they do not convert an unbounded signed difference. VCVT.F32.S32 follows architectural floating-point rounding controls; floating exception/status and enable/trap state remain architectural conditions. S0/S1 are explicit call context, without inventing a child prototype or assuming child preservation. Child memory effects unresolved. Registers loaded after both transform calls reflect potentially changed local rectangle words. Join540308 also receives skipped-region branches from prior packet. No whole-function, physical rendering, admission, C or gates.


# Second region clip continuation, 0x540308..0x540372

Partial; accepted:false. 106 original bytes; 224-byte frame remains active.

word[SP+20]=word[SP+52]
R0=freshword[SP+52]; word[SP+12]=u32(R0-R9+1)
R0=word[SP+56]; word[SP+16]=u32(R0-R9+1)
word[SP+24]=freshword[SP+56]
R1=SP+12; R0=SP+60; call540024()
R0=word[SP+12]
if s32(R10)<s32(R0): R0=freshword[SP+12]
else: R0=R10
word[SP+60]=R0
R0=u32(R11+1); R1=word[SP+16]
if s32(R0)<s32(R1): R0=freshword[SP+16]
else: R0=u32(R11+1)
word[SP+64]=R0
R2=u32(R4+56); R1=SP+60; R0=SP+28; call450BCC()
if R0==0: branch5403C8
R2=R8; R1=SP+92; R0=SP+28; call450F28()
if R0!=0: branch5403C8
R0=SP+112; call561810(); continue540372

Signed comparisons operate on wrapped32 values, especially R11+1 overflow. Fresh loads after comparison retained. Opaque children may change memory, including subsequent rectangle inputs. Geometry/clip names inferred. No claimed whole routine, ABI, physical behavior, accepted coverage or gates.


# Second region transform continuation, 0x540372..0x5403C8

Partial; accepted:false. 86 original bytes; active224-byte frame.

R0=SP+112; R1=word[0x5409D8]; word[R0+16]=R1
R1=word[SP+12]; R1=u32(R1-R6); S0.bits=R1; S0=VCVT.F32.S32(S0); word[R0+8]=S0.bits
R1=word[SP+16]; R1=u32(R1+R9); R1=u32(R1-1); R1=u32(R1-R7)
S0.bits=R1; S0=VCVT.F32.S32(S0); word[R0+20]=S0.bits
R0=SP+112; call561B38()
R0=SP+112; call5226E8()
R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0(); continue5403C8

5409D8 is literal data outside this code span, explicitly recorded by PC-relative reference. Conversion uses signed interpretation of wrapped32 and architectural binary32 conversion with floating-point rounding controls, with floating status/trap/enable conditions unresolved. Child return values overwritten; child contracts and effects unresolved. Join5403C8 also reached from preceding skip branches. No C, admission, gate or physical rendering qualification.


# Third region continuation, 0x5403C8..0x54049A

210 original bytes. Ordered register/memory operations:

word[SP+12]=word[SP+44]
R0=freshword[SP+44]; word[SP+20]=u32(R9+R0-1)
R0=word[SP+56]; word[SP+16]=u32(R0-R9+1)
word[SP+24]=freshword[SP+56]
R1=SP+12; R0=SP+60; call540024()
R0=u32(R11+1); R1=word[SP+16]
if s32(R0)<s32(R1): R0=freshword[SP+16]
else: R0=u32(R11+1)
word[SP+64]=R0
R0=word[SP+20]; R1=u32(R10-1)
if s32(R0)<s32(R1): R0=freshword[SP+20]
else: R0=u32(R10-1)
word[SP+68]=R0
R2=u32(R4+56); R1=SP+60; R0=SP+28; call450BCC()
if R0==0: branch54049A
R2=R8; R1=SP+92; R0=SP+28; call450F28()
if R0!=0: branch54049A
R0=SP+112; call561810()
S0.bits=BF800000; word[SP+112]=S0.bits
R0=SP+112; word[R0+16]=S0.bits
R1=word[SP+12]; R1=u32(R1+R9); R1=u32(R1-1); R1=u32(R1-R6)
S0=F(R1); word[R0+8]=S0.bits
R1=word[SP+16]; R1=u32(R1+R9); R1=u32(R1-1); R1=u32(R1-R7)
S0=F(R1); word[R0+20]=S0.bits
R0=SP+112; call561B38()
R0=SP+112; call5226E8()
R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0(); continue54049A

Signed selection uses wrapped R10-1 and R11+1, not unbounded min/max. BF800000 is immediate binary32 negative one. Geometry and region names are inference only.

For each shown conversion F(x), transfer u32(x) bits into S0 then execute VCVT.F32.S32 S0,S0; signed32 interpretation and architectural floating-point rounding/status controls apply. u32 wraps each arithmetic operation. Children are opaque, may modify memory; loads following a child are fresh. Frame224 remains active. This packet is partial/accepted:false, no whole-function or physical-rendering qualification, no admission, C or gates.


# Fourth region continuation, 0x54049A..0x54055A

192 original bytes. Ordered register/memory operations:

word[SP+12]=word[SP+44]
R0=freshword[SP+44]; word[SP+20]=u32(R9+R0-1)
word[SP+16]=word[SP+48]
R0=freshword[SP+48]; word[SP+24]=u32(R9+R0-1)
R1=SP+12; R0=SP+60; call540024()
R0=word[SP+20]; R1=u32(R10-1)
if s32(R0)<s32(R1): R0=freshword[SP+20]
else: R0=u32(R10-1)
word[SP+68]=R0
R0=word[SP+24]
if s32(R0)<s32(R11): R0=freshword[SP+24]
else: R0=R11
word[SP+72]=R0
R2=u32(R4+56); R1=SP+60; R0=SP+28; call450BCC()
if R0==0: branch54055A
R2=R8; R1=SP+92; R0=SP+28; call450F28()
if R0!=0: branch54055A
R0=SP+112; call561810()
R0=word[0x5409D8]; word[SP+112]=R0
R0=SP+112
R1=word[SP+12]; R1=u32(R1+R9); R1=u32(R1-1); R1=u32(R1-R6)
S0=F(R1); word[R0+8]=S0.bits
R1=word[SP+16]; R1=u32(R1-R7)
S0=F(R1); word[R0+20]=S0.bits
R0=SP+112; call561B38()
R0=SP+112; call5226E8()
R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0(); continue54055A

Literal5409D8 outside this instruction span is retained as a data reference. Comparisons signed after wrapping. Repeated rectangle loads retained; child effects not assumed absent. Region/transform names are inference only.

For each shown conversion F(x), transfer u32(x) bits into S0 then execute VCVT.F32.S32 S0,S0; signed32 interpretation and architectural floating-point rounding/status controls apply. u32 wraps each arithmetic operation. Children are opaque, may modify memory; loads following a child are fresh. Frame224 remains active. This packet is partial/accepted:false, no whole-function or physical-rendering qualification, no admission, C or gates.


# Fifth region, 0x54055A..0x5405F2, 152 bytes

word[SP+12]=u32(R9+word[SP+44])
word[SP+20]=u32(word[SP+52]-R9)
word[SP+16]=word[SP+48]
word[SP+24]=u32(R9+freshword[SP+48]-1)
R1=SP+12; R0=SP+60; call540024()
R0=word[SP+24]
if s32(R0)<s32(R11): R0=freshword[SP+24]
else: R0=R11
word[SP+72]=R0
R2=u32(R4+56); R1=SP+60; R0=SP+28; call450BCC()
if R0==0: branch5405F2
R2=R8; R1=SP+92; R0=SP+28; call450F28()
if R0!=0: branch5405F2
R0=SP+112; call561810()
R0=u32(R7-word[SP+16]); S0.bits=R0; S1=F(R0)
R0=u32(R6-word[SP+20]); S0.bits=R0; S0=F(R0)
R0=SP+112; call561856()
R0=SP+112; call5226E8()

R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0()
continue5405F2

Partial; accepted:false. Frame224 of candidate540036 active. u32 wraps each operation; comparisons use signed32. F(x) means transfer wrapped32 bits to S0 and VCVT.F32.S32 into the indicated S register, under architectural rounding/status/enable controls. Opaque children may modify memory; subsequent loads are fresh. Child prototypes, physical rendering, whole-function behavior, faults and concurrent mutation unresolved. Names are inference. No admission, C, freeze or gate changes.


# Sixth region, 0x5405F2..0x5406A4, 178 bytes

word[SP+12]=u32(R9+word[SP+44])
word[SP+20]=u32(word[SP+52]-R9)
word[SP+16]=u32(word[SP+56]-R9+1)
word[SP+24]=freshword[SP+56]
R1=SP+12; R0=SP+60; call540024()
R0=u32(R11+1); R1=word[SP+16]
if s32(R0)<s32(R1): R0=freshword[SP+16]
else: R0=u32(R11+1)
word[SP+64]=R0
R2=u32(R4+56); R1=SP+60; R0=SP+28; call450BCC()
if R0==0: branch5406A4
R2=R8; R1=SP+92; R0=SP+28; call450F28()
if R0!=0: branch5406A4
R0=SP+112; call561810()
R0=SP+112; R1=word[0x5409D8]; word[R0+16]=R1
R1=u32(word[SP+20]-R6); S0=F(R1); word[R0+8]=S0.bits
R1=word[SP+16]; R1=u32(R1+R9); R1=u32(R1-1); R1=u32(R1-R7)
S0=F(R1); word[R0+20]=S0.bits
R0=SP+112; call561B38()
R0=SP+112; call5226E8()

R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0()
continue5406A4
Literal5409D8 remains data outside code span.

Partial; accepted:false. Frame224 of candidate540036 active. u32 wraps each operation; comparisons use signed32. F(x) means transfer wrapped32 bits to S0 and VCVT.F32.S32 into the indicated S register, under architectural rounding/status/enable controls. Opaque children may modify memory; subsequent loads are fresh. Child prototypes, physical rendering, whole-function behavior, faults and concurrent mutation unresolved. Names are inference. No admission, C, freeze or gate changes.


# Seventh region, 0x5406A4..0x540764, 192 bytes

word[SP+12]=u32(word[SP+52]-R9+1)
word[SP+20]=freshword[SP+52]
word[SP+16]=u32(R9+word[SP+48])
word[SP+24]=u32(word[SP+56]-R9)
R1=SP+12; R0=SP+60; call540024()
R0=word[SP+16]; R1=u32(R11+1)
if s32(R0)<s32(R1): R0=freshword[SP+16]
else: R0=u32(R11+1)
word[SP+64]=R0
R0=word[SP+24]
if s32(R11)<s32(R0): R0=freshword[SP+24]
else: R0=R11
word[SP+72]=R0
R0=word[SP+12]
if s32(R10)<s32(R0): R0=freshword[SP+12]
else: R0=R10
word[SP+60]=R0
R2=u32(R4+56); R1=SP+60; R0=SP+28; call450BCC()
if R0==0: branch540764
R2=R8; R1=SP+92; R0=SP+28; call450F28()
if R0!=0: branch540764
R0=SP+112; call561810()
R0=word[SP+16]; R0=u32(R7-R0); R0=u32(R9+R0); R0=u32(R0-1)
S0.bits=R0; S1=F(R0)
R0=u32(R6-word[SP+12]); S0.bits=R0; S0=F(R0)
R0=SP+112; call561856()
R0=SP+112; call5226E8()

R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0()
continue540764
The SP+72 selection here is a maximum, unlike earlier minima.

Partial; accepted:false. Frame224 of candidate540036 active. u32 wraps each operation; comparisons use signed32. F(x) means transfer wrapped32 bits to S0 and VCVT.F32.S32 into the indicated S register, under architectural rounding/status/enable controls. Opaque children may modify memory; subsequent loads are fresh. Child prototypes, physical rendering, whole-function behavior, faults and concurrent mutation unresolved. Names are inference. No admission, C, freeze or gate changes.


# Eighth region, 0x540764..0x540842, 222 bytes

word[SP+12]=word[SP+44]
word[SP+20]=u32(R9+freshword[SP+44]-1)
word[SP+16]=u32(R9+word[SP+48])
word[SP+24]=u32(word[SP+56]-R9)
R1=SP+12; R0=SP+60; call540024()
R0=word[SP+16]; R1=u32(R11+1)
if s32(R0)<s32(R1): R0=freshword[SP+16]
else: R0=u32(R11+1)
word[SP+64]=R0
R0=word[SP+24]
if s32(R11)<s32(R0): R0=freshword[SP+24]
else: R0=R11
word[SP+72]=R0
R0=word[SP+20]; R1=u32(R10-1)
if s32(R0)<s32(R1): R10=freshword[SP+20]
else: R10=u32(R10-1)
word[SP+68]=R10
R2=u32(R4+56); R1=SP+60; R0=SP+28; call450BCC()
if R0==0: branch540842
R2=R8; R1=SP+92; R0=SP+28; call450F28()
if R0!=0: branch540842
R0=SP+112; call561810()
R0=word[0x5409D8]; word[SP+112]=R0
R0=SP+112
R1=word[SP+12]; R1=u32(R1+R9); R1=u32(R1-1); R1=u32(R1-R6)
S0=F(R1); word[R0+8]=S0.bits
R1=word[SP+16]; R1=u32(R1-R9); R1=u32(R1+1); R1=u32(R1-R7)
S0=F(R1); word[R0+20]=S0.bits
R0=SP+112; call561B38()
R0=SP+112; call5226E8()

R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0()
continue540842
R10 is overwritten by selection even when clipping later skips drawing. Literal5409D8 outside code.

Partial; accepted:false. Frame224 of candidate540036 active. u32 wraps each operation; comparisons use signed32. F(x) means transfer wrapped32 bits to S0 and VCVT.F32.S32 into the indicated S register, under architectural rounding/status/enable controls. Opaque children may modify memory; subsequent loads are fresh. Child prototypes, physical rendering, whole-function behavior, faults and concurrent mutation unresolved. Names are inference. No admission, C, freeze or gate changes.


# Final region and cleanup, 0x540842..0x5409C4, 386 bytes

word[SP+4]=0; word[SP+0]=FFFFFFFF
R3=FFFFFFFF; R2=1; R1=1; R0=word[SP+76]; call4B06C0()
R0=FF000000; call522A16()
word[SP+12]=u32(R9+word[SP+44])
word[SP+20]=u32(word[SP+52]-R9)
word[SP+16]=u32(R9+word[SP+48])
R0=word[SP+56]; R9=u32(R0-R9); word[SP+24]=R9
R1=SP+12; R0=SP+60; call540024()
R0=word[SP+16]; R1=u32(R11+1)
if s32(R0)<s32(R1): R0=freshword[SP+16]
else: R0=u32(R11+1)
word[SP+64]=R0
R0=word[SP+24]
if s32(R11)<s32(R0): R11=freshword[SP+24]
word[SP+72]=R11
R2=u32(R4+56); R1=SP+60; R0=SP+28; call450BCC()
if R0==0: goto5408EA
R2=R8; R1=SP+92; R0=SP+28; call450F28()
if R0!=0: goto5408EA

R3=word[SP+40]; R0=word[SP+32]; R3=u32(R3-R0+1)
R2=word[SP+36]; R0=word[SP+28]; R2=u32(R2-R0+1)
R1=word[SP+32]; R1=u32(R1-R7)
R0=word[SP+28]; R0=u32(R0-R6)
call522AE0()

5408EA:
R0=byte[SP+80]
if R0==0:
 R0=0; call522A16()
 R0=SP+92; call4515A4(); R4=R0
 R0=SP+92; call451598()
 word[SP+0]=R8; R3=R4; R2=R0
 R1=u32(word[SP+96]-R7); R0=u32(word[SP+92]-R6); call522B30()
54091A:
R0=word[SP+84]; R0=byte[R0+20]
if R0==16: R4=0x501
else: R4=0x504
R0=SP+112; call561810()
R0=SP+112; call5226E8()
R0=SP; R1=u32(R5+32); R2=3; call439BE4()
R1=byte[R5+52]; R0=word[SP+0]; call4B06A8(); R8=R0
R0=freshbyte[R5+52]
if R0==255:
 R1=R4; R0=word[SP+76]; call4B0748()
else:
 R4=R4|08000000; R1=R4; R0=word[SP+76]; call4B0748()
 R0=R8; call513E2E()
540974:
R0=R8; call4B146C()
call4B1548() // inherits previous child's R0 and other caller registers; no reset
R0=SP+44; call4515A4(); R4=R0
R0=SP+44; call451598()
R3=R4; R2=R0
R0=word[SP+48]; R7=u32(R0-R7); R1=R7
R0=word[SP+44]; R6=u32(R0-R6); R0=R6
call522AE0()
call5144FA() // inherits prior return context
R4=R0
R0=R4; call514CF2()
R0=R4; call514D00()
R0=R4; call514384()
R0=word[SP+88]; call44F758()
5409BE:
SP=u32(SP+188)
restore R4,R5,R6,R7,R8,R9,R10,R11,PC from nine consecutive words at SP; SP+=36

Final R0 is the 44F758 child result on normal completed path. Early paths from5400F8 (initial clip failure) and5401FC (acquire rejection afterfree) branch directly to5409BE retaining their child return context. Epilogue skips saved entryR3 by adding188 after184-byte locals, restores other saved registers, and consumes savedLR intoPC. Total frame224 restored. Final clipping mutates R9/R11; previous packet mutates R10, all later restored from entry saves. Stack0 is reused for arguments and then three-byte copy; remaining fourth byte is not assumed zero before subsequent wordload. Repeated alpha loads may differ afterchild effects; no invented saturation here.

Partial; accepted:false. Frame224 of candidate540036 active. u32 wraps each operation; comparisons use signed32. F(x) means transfer wrapped32 bits to S0 and VCVT.F32.S32 into the indicated S register, under architectural rounding/status/enable controls. Opaque children may modify memory; subsequent loads are fresh. Child prototypes, physical rendering, whole-function behavior, faults and concurrent mutation unresolved. Names are inference. No admission, C, freeze or gate changes.
