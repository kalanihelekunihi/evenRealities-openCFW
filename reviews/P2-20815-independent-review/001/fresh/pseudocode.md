# Post-scan two counts and base pointer diagnostics

Partial/unaccepted;140 instruction bytes; inherited64-byte frame. R5eligiblecount,R6visitcount,R4tablebase,allfullwidth.
C3E0 query43D0CE bit1zero→C406;otherwiseSP12=R6,SP8=R5,SP4=literal47CB20,SP0=2144;43D574(4,literal47C548,literal47C544,literal47CB0C,2144,literal47CB20,fullR5,fullR6).
C406 freshquerybit0one→C416;elseanotherquerybit2zero→C428. C416SP0=fullR6;43CE9E(0x10800000,literal47CB24,same,fullR5,fullR6).
C428 querybit1zero→C44C;otherwiseSP8=fullR4,SP4=literal47CB28,SP0=2145;43D574(4,literal47C548,literal47C544,literal47CB0C,2145,literal47CB28,fullR4).
C44C freshquerybit0one→C45C;elseanotherquerybit2zero→pendingC46C. C45C43CE9E(0x10400000,literal47CB2C,same,fullR4);fallthroughpendingC46C. All writes localstack,queries distinct, no narrowing or implied pointer dereference. No C/freeze/completenessclaim.
