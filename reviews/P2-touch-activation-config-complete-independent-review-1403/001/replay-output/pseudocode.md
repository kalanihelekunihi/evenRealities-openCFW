# Touch activation configuration complete local flow

Body71C8..7284 is188 instructionbytes,followed byliteral. Initialcopy/callbackprefix isdocumented in1398. Ifaccumulated6384/5378status iszero,call6AC0(1,descriptor),ORresult. Ifstillzero,call6AC0(2,descriptor),ORresult. Ifstillzero,call7064(descriptor) andreplaceaccumulatedstatus withitsreturn. Thenforeachindex0,1,2 call7DDE(index,descriptor); ifnonzero,call5CAC(index,descriptor) andORreturn. Returnaccumulatedstatus,restorefour-wordframe.

Receipt-derived originalinstruction fixtures extend1398 throughreturn,varyingfirststatuses,twostatecallstatuses andall-rowenableflag. Deeperhelpers controlled;nullcallback supplied. Exactcopywrites,reachedcallsequence,returnedstatus andSP checked. Callbacknonnullbehavior,realhelpercontracts andphysicalactivation remainunresolved. No canonicaladmission orCimplementation.
