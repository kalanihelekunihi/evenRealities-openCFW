# Selector two sixteen byte mask fresh nibble mask

Partial/unaccepted;102instructionbytes,inherited88-byteframe,R4source. Query0x43D0CE;bit0oneenters0x47B162,otherwisequeryagainandbit2zero skips0x47B1B6. MaskpathloadR1literal47B71C. Independentlyfreshreadbytes[R4+19..5]descendingorder;foroffsetjfrom19downto5storeunsignedbyteatSP(4*j-20),coveringSP56..0. Thenfreshbyte[R4+4]R3,R2=R1. Independentlyreadbyte[R4+14]againintoR0,maskLOW4bits,shiftleft22,OR0x10000000. Call0x43CE9E(0x10000000|((freshSecondByte14&15)<<22),R1,R2,byte4,fifthbyte5,...,nineteenthbyte19). Secondbyte14readnotcachedfromearlierstackargument;preservepossiblememorychangeandreadorder.
At0x47B1B6branchpending0x47B348. No returnorhelpersemanticsinferred. No C,freezeorcompletenessclaim.
