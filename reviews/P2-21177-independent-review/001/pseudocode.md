# Alternate-bank mask/output, invalid selector and unwind

Partial/unaccepted;172 instruction bytes4813BC..481468. Continues4812F6;56-byteframe,R6bankselector,R7maskenable,R5outputpointer,R4statusinitial0,SP0saved473940result,SP4..28maskarray. R6=UXTB(R6);ifnot1→R4=6at48145A,nooutputwrites;joinrestore. Bank1:R7=UXTB(R7);ifnonzero loadpointerliterals481784+4*k for k0..6,freshword→SP4+4*k ordered;zero retainsinitializedallonesmask (subjecthelperaliasing). Then k0..6 loadpointerliterals4817BC+4*k,freshtargetword,reloadmaskSP4+4*k,AND,storeoutputR5+4*k inthatorder. Preservetargetread-beforemaskreload andoutput/stackaliasing;no outputpointerguard. Bank0prefix alsojoinsrestore.

48145C reloadSP0,MSR PRIMASK,R0;R0=R4status0or6. ADDSP36 discards32localsplus savedentryR3;POP R4,R5,R6,R7,PC20 releasesremaining,total56. Invalidbankselectorlowbyte2..255 stillinitializedmasksandcalledhelperbeforevalidation,thenrestoresPRIMASK;noerroroutputinitialization. No C/freeze/fullcoverage/equality claim.
