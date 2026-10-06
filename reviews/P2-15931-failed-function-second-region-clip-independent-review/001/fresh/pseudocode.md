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
