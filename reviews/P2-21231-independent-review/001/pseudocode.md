# Floating layout locale byte, short count and general precision selection

Partial/unaccepted;86 instruction bytes4820BC..482112. Continues481836232frame. Entry4820BC R6=R0retainedcount,R5wordSP0exponent;zero-valueentry4820C0alreadyR6=R5=0. Call4D43A8 withliveR0/R1/R2/R3;freshword[returnedR0+36]pointer;freshbyte[pointer]→R7separator. No nullguard/helpersemanticsassumption. R8precisionwordSP56;R0=SXTHR6;if<=0 R6=1,R4ADR4826F8fallbackdigitpointer. ElsefullR6retained.

R0=R11OR32conversion. f102→R5++mod2^32,branch482112fixedlayout. Otherg103: SXTHR5exponent<-4 signed→482180;orSXTHR5>=R8signed→482180. OtherwiseR5++;freshbyteSP64flagsbit3set skipscountprecisionclamp. Bit3clear:R0=SXTHR6;ifR0<=R8signed,R8=R0. ThenR0=SXTHR5;R8-=R0mod2^32;ifresultnegativeconditionMI R8=0;fallthrough482112. Otherconversion→482174 unresolvedscientific/hexpath. PreserveSXTHtruncationsvsfullregistervalues andITflagdependence;no C/freeze/fullcoverage/equality claim.
