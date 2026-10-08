# Five optional callback wrappers including saved-entry return

Partial/unaccepted;106 instruction bytes480358..4803C2. EachPUSH R7,LR8;R1literal4806FCtablepointer. Wrappers0358/036E/0384/03AC useoffset20/24/28/32respectively: freshword[table+offset]→R0,zero→explicitR0=0;nonzero→independentreloadsamewordR0,BLX R0 withR0secondcallbackaddress,R1tablepointer,entryR2/R3live. ReturnsfullcallbackR0orzero;POP R1,PC releases8 andrestoresentryR7intoR1. Separatetest/reloadmaychangeincludingzero,noimmutabletableassumption.

039Awrapperoffset44: freshwordR0testzero skipscall;nonzeroindependentreloadR0BLX withsamearguments. CommonPOP R0,PC alwaysreturnsfullentryR7,overwritingcallbackresult orzero. No absentcallbackoutputwrites/initializationinvented. No PRIMASKoperations;callbacktargets/ownership/semanticsstillunresolved. NoC/freeze/fullcoverageclaim.
