# Numeric sign insertion and reverse-output call tail

Partial/unaccepted;66 instructionbytes4831C8..48320A,continues4830DA48-byteframe. UnsignedR0count>=32 skipsallsignchecks/writes. OtherwiseR6=UXTB(R6);nonzero selectsASCII45minus,store[R7+R0],incrementR0mod. ZeroR6 flagsLRbit2set viaLSL29MI selectsASCII43plus;elseflagsbit3set viaLSL28MI selectsASCII32space;else no signwrite. Eachselectedpathstorebytebeforecountincrement;onlyinitialcountboundtestrequiredonebyte.

Common4831F4 storefullLRflagsSP12,R5widthSP8,R0countSP4,R7bufferSP0 inthatorder;R0=R4callback;call48306C withretainedentryR1/R2/R3 andthese fourstackarguments. RetainreturnedR0. ADDSP20 bypasses16localsand savedscratchR3slot,POP{R4,R5,R6,R7,R8,R9,PC}28bytes,total48released. Preserveflagpriorityminus>plus>space,currentwidth/count andoriginalentryR1/R2/R3 untouchedinthisroutinebeforecall. No C,freeze,wholecoverage or equalityclaim.
