# Saved-entry wrapper and unsigned indexed sixteen-byte copy

Partial/unaccepted;40instructionbytes47EF10..47EF38,twoentries.
EF10 PUSH R7,LR8;4D3C0A(liveentryargs);POP R0,PC returns savedentryR7 subjectcallee stackwrites,discardhelperresult.
EF18 PUSH R7,LR8. FullentryR0zero OR unsignedentryR1>=34→R0=6,skiphelper. NonzeroentryR0 AND unsignedindex<34→R2=literal47F944base;R1=(index<<4)+base modulo2^32;439C04(entryR0,R1,16,liveR3);R0=0regardlesshelperresult. POP R1,PC setsR1=savedentryR7. No additionaldestinationsizecheck/templateownershipinferred. Negativeindexasunsignedrejectedby>=34;indices0..33exactstride16. No C/freeze/completenessclaim.
