# Constant size final diagnostics and live return

Partial/unaccepted;152 instruction bytes; inherited64-byte frame.
C46C query43D0CEbit1zero→C498;elseSP12=64,SP8=256,SP4=literal47CB30,SP0=2146;43D574(4,literal47C548,literal47C544,literal47CB0C,2146,literal47CB30,256,64).
C498 freshquerybit0one→C4A8;elseanotherquerybit2zero→C4BE. C4A8SP0=64;43CE9E(0x10800000,literal47CB34,same,256,64).
C4BE querybit1zero→C4E0;elseSP4=literal47CB38,SP0=2147;43D574(4,literal47C548,literal47C544,literal47CB0C,2147,literal47CB38).
C4E0freshquerybit0one→C4F0;elseanotherquerybit2zero→C4FE. C4F043CE9E(0x10000000,literal47CB3C,same,liveR3),no explicitR3assignment in setup.
C4FE add40SP;POP R4,R5,R6,R7,R8,PC24 completes64frame. ReturnliveR0 from final status/diagnostic path without explicit count/bool assignment. LocalSP0 writes discarded. Preserve separatequery calls and constantargumentorder. RoutineendsC504. No C/freeze/completenessclaim.
