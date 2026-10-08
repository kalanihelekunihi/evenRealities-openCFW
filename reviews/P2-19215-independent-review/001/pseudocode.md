# Decrement failure and return 0x46A7FA..0x46A822

Partial/unaccepted;40instructionbytes. Inherit24-byte PUSH0/1/2/3/4/LRframe;failurediagnosticprefixR3literal46B03C,R2literal46A830,SP0=496,SP4literal46B044. R1literal46A834,R0=4 ->43D574. At802 fresh43D0CE(liveargs) bit0set or,ifclear,anotherfresh43D0CE bit2set calls43CE9E(0x10000000,literal46B048,sameliteral,liveR3). Clearbits bypasscall.

Shared820 POP0/1/2/3/4/PC restores24bytes. ReturnR0fromSP0 originalentryR0 ifno bit1diagnosticexecuted,491 ondecrementdiagnosticroute,496 onfailurediagnosticroute. LaterchildR0discarded. R1/R2restorepotentiallyoverwrittenSP4/SP8;R3/R4restoreoriginalvalues. Adjacentword at822 excluded pending dataaccounting. No C/freeze/corpusclaim.
