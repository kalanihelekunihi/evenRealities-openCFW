# Selector-ten path 0x469FF2..0x46A050

Partial/unaccepted;94instructionbytes. Inherit24frame,FULLR4selector10,R5originalR3. Fresh43D0CEbit1diagnostic SP4literal46AACC,SP0=244,R3literal46AAC4,R2literal46A830,R1literal46A834,R0=4 ->43D574. Separatefreshbit0 orconditional thirdfreshbit2 R1literal46AAD0,R2R1,R0=0x10000000,live3 ->43CE9E.

Call45A568(liveargs) FULLresult==2 setsR0=1 ->46A18A outsidechunk. FULLresult!=2 calls45A568 AGAIN withliveargs; FULLsecondresult==1 calls46A848 withliveR0/R1/R2/R3, otherwise skips. Bothpaths46A04CexplicitR0=1 ->46A18A. Do notcollapsefreshmodecalls intoonesnapshot or assumechildtakesoriginalargs. Diagnosticsmodifiedliveargs;R4/R5snapshotsretained. Nextselector72test46A050excluded. No C,freezeorwholefunctionclaim.
