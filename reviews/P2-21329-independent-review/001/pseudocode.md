# Floating output self compare and negative-bound special path

Partial/unaccepted;86 instructionbytes483350..4833A6. PUSH{R4,R5,R6,R7,R8,R9,R10,LR}32bytes,SUBSP48,total80. FreshwordSP84→R6(sixthargument),SP88→R12(seventh),R8=0. VLDR d1 from48363C readsEIGHTliteralbytes;vcmp.f64 d0,d0;VMRSAPSR_nzcv,FPSCR. EQ→483382. Otherwise orderedstoresR12SP12,R6SP8,R4=3→SP4,R4=ADR483614→SP0;call48306C withentryR0/R1/R2/R3 stilllive,branchunresolved48360C.

483382 VLDRd2from483618 EIGHTbytes;vcmp.f64d0,d2;VMRSflags;PL→unresolved4833A6. MIpathorderedstoresR12SP12,R6SP8,R4=4→SP4;freshwordliteral483FCC→R4pointer→SP0;call48306C withliveentryR0/R1/R2/R3,branch48360C. Floatingconditionflags recordedexactlywithoutunverifiedliteralclassifications. references.json generic4byteslicesareonlyliteralprefixesforVLDRd1/d2;full8bytepayloads remaindatarecoveryobligation. Do not inferstringcontents or NaN/infinitylabelwithoutdataevidence. No C,freeze,wholecoverage or equalityclaim.
