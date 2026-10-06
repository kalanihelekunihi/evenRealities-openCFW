# Global viewport command pair, 0x4B1548..0x4B1588,64 bytes
R0=word[0x4B178C]; PUSH R4,R5,LR12
R2=word[R0]; SP-=4
R1=word[R2+40]; R0=word[R2+36]; R4=word[R2+44]; R5=word[R2+48]
R4=u32(R4+R0); R5=u32(R5+R1)
if R0 signbit==1: R0=0
if R1 signbit==1: R1=0
R1=(R0&FFFF)|((R1<<16)&FFFF0000); R0=272; call514846()
R1=(R4&FFFF)|((R5<<16)&FFFF0000)
SP+=4; R0=276; restore R4,R5,LR; SP+=12; tailbranch514846

EntryR0 ignored; literal4B178C pointer data outsidecode. Globalcoordinates/endpoints readbeforefirstchild, no rereadsafterchild. Endcoordinatescomputedbeforeclippingstarts. No ownership/lifetime qualification.

Partial; accepted:false. Original instruction bytes; opaque children supply return/register/memory effects. Aliasing, fault and concurrentglobal effects remain conditional; names inferred. No C, admission, freeze or gates.
