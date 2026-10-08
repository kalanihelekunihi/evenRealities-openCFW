# Five optional callback wrappers with low-byte pair dispatch

Partial/unaccepted;114 instruction bytes4803C2..480434. AllPUSH R7,LR8 andPOP R1,PC8restoreentryR7intoR1. 03C2R3literal4806FCtablepointer;freshword[table+36]R2zero→return0,R1entryunmasked,R2zero,R3tablepointer. NonzeroR0LOW8entryR0,R1LOW8entryR1;independentreloadtable+36R2→BLX R2 withR2callbackaddress,R3tablepointer;fullcallbackresultreturned. EntryR2/R3notpassedunchanged. Secondpointermaychangeincludingzero.

03DC/03F2/0408/041ER1tablepointer;offset40/48/52/56respectively, freshword→R0zero→return0;nonzeroindependentreloadR0BLX R0 withR0callbackaddress,R1tablepointer,liveentryR2/R3;fullcallbackreturn. Distincttest/reloadrequired,noimmutabletable/nullsafecallassumption. No outputwrites/initializationonabsentcallbacks; noPRIMASKoperation. Callbacktargets/tableownershipsemanticsunresolved;noC/freeze/fullcoverageclaim.
