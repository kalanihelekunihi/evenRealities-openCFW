# Selector one diagnostics fresh helper byte-four guard

Partial/unaccepted;78instructionbytes;inherited40frame,R5=fullentryR1buffer,R4inheritedzero.
D08C query43D0CEwithliveargs;bit1zero→D0B0;otherwiseSP4=literal47D930,SP0=87;43D574(4,literal47D918,literal47D914,literal47D910,87,literal47D930).
D0B0 freshquerybit0one→D0C0;elseanotherquerybit2zero→D0CE. D0C0:43CE9E(0x10000000,literal47D934,same,liveR3);noexplicitR3assignmentinmasksetup.
D0CE independentlycall45A568withliveargs;thenfreshunsignedbyte[R5+4]→R1;LOW8helperresult→R0;comparefullbytevalues. Unequal→pendingD15A;equal→pendingD0DA. Callprecedesbufferread; do notreuseearlierdiagnostichelperresultsorbyte4reads. No resultassignmentt R4inthisslice,localdiagnosticstackslots. No C/freeze/completenessclaim.
