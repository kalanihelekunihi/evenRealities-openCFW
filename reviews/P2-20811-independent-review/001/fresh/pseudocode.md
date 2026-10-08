# Sixty-four-byte frame diagnostics and scan initialization

Partial/unaccepted;90 instruction bytes.47C2BC PUSH R4,R5,R6,R7,R8,LR (24bytes),SUB SP40:64-byte frame.
C2C2 query43D0CE with livearguments;bit1zero→C2E4;otherwise SP4=literal47CB08,SP0=2123;43D574(4,literal47C548,literal47C544,literal47CB0C,2123,literal47CB08).
C2E4 freshquerybit0one→C2F4;elseanotherquerybit2zero→C302. C2F4:43CE9E(0x10000000,literal47CB10,same,liveR3);mask setup leavesR3unassigned.
C302:R4=literal47CB14,R5=0,R6=0;475014(0,1,liveR2/R3);R7=0;branchpending47C3DC. Initial diagnostic writes are localSP0/SP4, not saved entry registers. No entry argument captured before calls; do not infer a source parameter contract. No C/freeze/completenessclaim.
