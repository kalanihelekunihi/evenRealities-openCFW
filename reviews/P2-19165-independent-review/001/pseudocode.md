# Event dispatch entry 0x469FA2..0x469FF2

Partial/unaccepted;80instructionbytes. PUSH R1/R2/R3/R4/R5/LR creates24frame;SP0originalR1,SP4originalR2,SP8originalR3,SP12savedR4,SP16savedR5,SP20LR. R4=FULLoriginalR2selector,R5originalR3. Fresh43D0CEbit1diagnostic SP8=FULLR4 overwritingoriginalR3;SP4literal46AAC0,SP0=242,R3literal46AAC4,R2literal46A830,R1literal46A834,R0=4 ->43D574.

Separatefresh43D0CEbit0 orconditional thirdfreshbit2 enables R1literal46AAC8,R3FULLR4,R2R1,R0=0x10400000 ->43CE9E. At469FEE compareFULLR4==10; unequalbranches46A050 outsidechunk,equalfalls469FF2. Freshmaskcalls/orderandFULLselector retained; diagnosticsoverwriteallthree savedargumentwords. R5originalR3snapshotremainsavailablethoughliveR3mayclobbered. No C,freezeorwholefunctionclaim.
