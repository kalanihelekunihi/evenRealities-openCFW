# Floating special sign, range fallback and magnitude

Partial/unaccepted;126 instructionbytes4833A6..483424,continues48335080-byteframe. VLDRd2from483620eightbytes,VCMPd0,d2/VMRSflags;NE→4833DE. EQflagsR12bit2set→R4=4,R5=freshwordliteral483FFCpointer;clear→R4=3,R5=ADR483628. OrderedstoresR12SP12,R6SP8,R4SP4,R5SP0;call48306C liveentryR0/R1/R2/R3,branch48360Cunresolved.

4833DEfreshSP80fifthargument→R7;VLDRd2from48362Ceightbytes;VCMPd0,d2/VMRS;GE(N==V)→4833FC. OtherwiseVLDRd2from483634eightbytes,VCMP/VMRS;PL(N==0)→48340A,MI→4833FC. FallbackorderedstoresR12SP8,R6SP4,R7SP0;callunresolved48364C withliveentryR0/R1/R2/R3andd0,branch48360C. At48340A LR=0;VLDRd2from48363Ceightbytes,VCMPd0,d2/VMRS;PLskipto483424;MI LR=1,VNEG.f64d0,d0. Fallthrough483424. PreserveexactFPconditions(varyGE/PL),flagreadbit2,8byteconstantobligations(genericreferencesonly4byteprefixes),livehelperargsandorderedstores. No assumedinfinity/rangevaluesbeforedatareview. No C,freeze,wholecoverage or equalityclaim.
