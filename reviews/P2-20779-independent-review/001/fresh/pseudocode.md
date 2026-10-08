# Nine saved register seventy-two frame entry diagnostics

Partial/unaccepted;74instructionbytes. PUSH R4,R5,R6,R7,R8,R9,R10,R11,LR36bytes thenSP-=36creates72-byteframe. Query43D0CEwithliveentryarguments;statusbit1zero skips0x47BC5C. OtherwiseSP4literal47C53C,SP0=2003;call43D574(4,literal47C548,literal47C544,literal47C540,fifth2003,sixthliteral47C53C). TheseSP0/4writesarelocals,not savedregisterslots.
At0x47BC5Cqueryfreshstatus;bit0oneenters0x47BC6C,otherwisequeryagainandbit2zero skips0x47BC7A. MaskpathR1literal47C54C,R2same,liveR3;call43CE9E(0x10000000,R1,R2,liveR3). Fallthroughpending0x47BC7A. No entryargumentscopiedtocallee-savedregistersinthisslice;do notinventretainedentryR0/R1orfinalreturn. Preserveseparatequeries/liveargs. No C,freezeorcompletenessclaim.
