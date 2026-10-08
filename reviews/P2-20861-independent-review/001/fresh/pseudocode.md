# Forty-byte frame entry buffer length diagnostics

Partial/unaccepted;86instructionbytes. PUSH R3,R4,R5,R6,R7,LR24+SUB SP16=40frame. R5=fullentryR1,R7=fullentryR2,R4=0,R6=R5;entryR0notcaptured.
CF6C query43D0CEwithliveentryargs;bit1zero→CF94. ElseSP12=fullR7,SP8=fullR5,SP4=literal47D90C,SP0=80;43D574(4,literal47D918,literal47D914,literal47D910,80,literal47D90C,fullR5,fullR7).
CF94 freshquerybit0one→CFA4;elseanotherquerybit2zero→pendingCFB6. CFA4 SP0=fullR7;43CE9E(0x10800000,literal47D91C,same,fullR5,fullR7);fallthroughpendingCFB6. DiagnosticSP0..12withinlocals; savedentryR3SP16untouchedinprefix. No pointervalidation,lengthbounds,bytecopyorloopcontract inferredyet. No C/freeze/completenessclaim.
