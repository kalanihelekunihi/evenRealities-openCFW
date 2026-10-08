# Floating integer digits, zero width, sign and output

Partial/unaccepted;176 instructionbytes48355C..48360C,continues48335080-byteframe. WhileunsignedR8<32: R4=10,R7=SDIV(R5,10)towardzero,R4=R5-10*R7mod,add48;R7=SP16buffer,storelowbyteR4[buffer+R8],R8++;R4=10,R5=SDIV(R5,10);nonzeroR5repeat,zerobreak. Atleastonedigitifspace;actualsignedremainder preserved.

FlagsR12&3==1 enableszero-widthpadding. IfR6width!=0 and(UXTB(LRsign)!=0 OR(flags&12)!=0),R6--mod. LoopunsignedR8<R6andR8<32 writesASCII48SP16+R8,R8++;otherwiseends. Flagsotherpatternskippadding. Ifcount<32: LR=UXTB(LR),nonzeroappend45minus;zero flagsbit2append43plus;elseflagsbit3append32space;else none. Allsignstoresbeforecountincrements;priorityminus/plus/space.

OrderedstackargsR12flagsSP12,R6adjustedwidthSP8,R8countSP4,R4=SP16buffer→SP0;call48306C withretainedentryR0/R1/R2/R3 (nocallswithinnormalpathsincelastentrychecks). Fallthrough48360Creturnunresolved. Preservefullcountbound,unsignedpaddingversussigneddigitdivision,byteLRsignandwrappingwidthadjustment. No C,freeze,wholecoverage or equalityclaim.
