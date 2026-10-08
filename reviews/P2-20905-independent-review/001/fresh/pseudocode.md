# Full helper guards two-message selection saved R5 return

Partial/unaccepted;88instructionbytes. PUSH R5,R6,R7,LR16frame. Call4A2FDCwithliveargs;fullresultnonzero→D85C. ZeroD822query43D0CEbit1zero→D83E;elseSP4=literal47D9B4,SP0=253;43D574(4,literal47D918,literal47D914,literal47D9B8,253,literal47D9B4). D83Efreshquerybit0one→D84E;elseanotherquerybit2zero→D85A;D84E43CE9E(0x10000000,literal47D9BC,same,liveR3). D85AbranchD86E;no messagecalloninitialzeroresultpath.
D85Ccall4A2914withliveargs;fullresultzero→D86Acall47CF28(liveargs);nonzero→D864call47CED6(liveargs). BothrejoinD86E. No LOW8testforhelperselection.
D86EPOP R0,R1,R2,PC16;R0=savedSP0 entryR5unlesslogger253overwroteit;R1=savedentryR6unlessloggerliteralD9B4overwroteSP4;R2=savedentryR7. HelperresultR0discarded. SavedR5/R6/R7notrestoredbythisPOP. No C/freeze/completenessclaim.
