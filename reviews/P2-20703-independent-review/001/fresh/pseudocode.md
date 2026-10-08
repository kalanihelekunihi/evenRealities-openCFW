# Entry byte30 diagnostics and four selector dispatch

Partial/unaccepted;108instructionbytes. PUSH R3,R4,R5,LR16bytes thenSP-=72 creates88-byteframe. R5fullentryR0destination,R4fullentryR1source. Query0x43D0CE;bit1zero skips0x47AF06;otherwisefreshbyte[R4+30]SP8,literal47B6EC SP4,1286 SP0;call0x43D574(4,literal47B6F8,literal47B6F4,literal47B6F0,fifth1286,sixthliteral47B6EC,seventhfreshbyte30).
At0x47AF06queryfreshstatus;bit0oneenters0x47AF16,otherwisequeryagainandbit2zero skips0x47AF26. MaskpathR2literal47B6FC,R1same,freshbyte[R4+30]R3;call0x43CE9E(0x10400000,R1,R2,R3). At0x47AF26independentlyfreshbyte[R4+30]R0dispatchesexact1to0x47AF40,2to0x47B07C,4to0x47B1B8,8to0x47B29A,others0x47B2FE. Alltargets pending;do notcachethethreebyte30readsorassumestability. No C,freezeorcompletenessclaim.
