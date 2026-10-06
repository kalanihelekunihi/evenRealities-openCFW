# Explicit viewport command pair, 0x4B1516..0x4B1548,50 bytes
PUSH R4,R5,LR12
R4=u32(entryR2+entryR0); R5=u32(entryR3+entryR1); SP-=4
if entryR0 signbit==1: R0=0
if entryR1 signbit==1: R1=0
R1=(R0&FFFF)|((R1<<16)&FFFF0000); R0=272; call514846()
R1=(R4&FFFF)|((R5<<16)&FFFF0000)
SP+=4; R0=276; restore R4,R5,LR; SP+=12; tailbranch514846

Endcoordinates computedwrapped BEFORE negative startcoordinates clippedtozero. Low16 truncation, not numerical saturation. Firstchildresult discarded; secondtailchildcontextreturned. Totalframe16 restoredbeforetail.

Partial; accepted:false. Original instruction bytes; opaque children supply return/register/memory effects. Aliasing, fault and concurrentglobal effects remain conditional; names inferred. No C, admission, freeze or gates.
