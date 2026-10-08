# Limit failure and saved-slot return 0x46A74A..0x46A77E

Partial/unaccepted;52instructionbytes. Inherit24-byte PUSH0/1/2/3/4/LRframe; failurediagnosticprefix storedliteral46B030SP4. Store482SP0;call43D574(4,literal46A834,literal46A830,literal46B028). At75E fresh43D0CE(liveargs) bit0set or,ifclear, anotherfresh43D0CE bit2set calls43CE9E(0x10000000,literal46B034,sameliteral,liveR3). No explicitR3setup inthiscall. Clearqualifyingbits bypasscall.

Shared77C POP0/1/2/3/4/PC restores24bytes. ReturnR0comesSP0: originalentryR0 ifno bit1diagnosticexecuted,477 onincrementpathdiagnostic,482 onlimitfailurediagnostic. AlllaterchildR0resultsdiscarded. R1/R2also restore possiblyoverwritten savedslots; R3originalentryR3 andR4originalentryR4. Keep distinctstatusreads and stackalias effects. No C/freeze/corpusclaim.
