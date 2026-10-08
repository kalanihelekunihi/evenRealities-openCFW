# State three final paths and return 0x46AA22..0x46AAB6

Partial/unaccepted;148instructionbytes. Inherit24frame andstate-one diagnosticargsR0=4,R1literal46B058,R2literal46B054,R3literal46B050,SP0=529,SP4literal46B070;call43D574. Fresh43D0CE bit0set or,ifclear,anotherfresh43D0CE bit2set calls43CE9E(0x10000000,literal46B074,sameliteral,liveR3). ThenbranchAAB2.

IndependentincomingAA46 inheritsR1addressliteral46AE98from996 withpreviousfreshreadnot1. Anotherfreshword[R1]FULLnot2 exitsAAB2. FULL2 fresh43D0CE bit1set storesliteral46B068SP4,532SP0,then43D574(4,literal46B058,literal46B054,literal46B050). Fresh43D0CE bit0set or,ifclear,anotherfresh43D0CE bit2set calls43CE9E(0x10000000,literal46B06C,sameliteral,liveR3). Call45A568(liveargs);FULLnot1 exitsAAB2;FULL1 ordered464C36(34,0,0,0),45ACCC(6,15,0,500).

SharedAAB2 ADDSP20 discards savedR3/R4/R5/R6/R7 slots withoutrestoringthem;POPPC4 returnsliveR0, NOT overwrittenSP0. These callee-savedregister effects must notbe silently normalized;prefixdiagnostic-slotwrites are discarded notpopped. No C/freeze/corpusclaim.
