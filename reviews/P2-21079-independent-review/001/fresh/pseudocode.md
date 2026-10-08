# Frameless ten ordered independent word updates

Partial/unaccepted;86 instruction bytes47FE12..47FE68. R0=literal4801D0value,usedpointer. Ten successive independentlyfreshword[R0] RMWstores in order: OR0x20000;OR0x40000;OR0x80000;OR0x10000;AND~0x10;OR0xE;OR1;AND~0x200;OR0x1C0;OR0x20. Each operationreloads word afterpriorstore;do notcollapseintooneRMWorassumereadbackequalsstoredvalue. FinalR1=lastfreshwordOR0x20;R0remainspointer literalvalue,returnedfullthroughBX LR. R2/R3unchanged;no stack/helper/PRIMASK operations. No pointedownership/MMIO/timing/C/freeze/fullcoverageclaim.
