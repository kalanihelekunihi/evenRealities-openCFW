# Post-scan final diagnostic and live result return

Partial/unaccepted; 74 instruction bytes; inherited 72-byte frame (36 locals and nine saved registers).
At 47C020 query 43D0CE with live arguments. Bit1 zero goes C046. Otherwise SP4=literal47CACC and SP0=2048; call 43D574(4,literal47C548,literal47C544,literal47C540,2048,literal47CACC).
At C046 query status afresh. Bit0 one goes C056; otherwise query again, bit2 zero goes C064. At C056 call 43CE9E(0x10000000,literal47CAD0,same,liveR3). R3 is not explicitly assigned in this mask setup. No fifth argument is explicitly established for this call.
At C064 add36 to SP then pop R4,R5,R6,R7,R8,R9,R10,R11,PC (36 bytes). Return live R0 from the executed diagnostic/status path; there is no explicit count, bool or selected-index return assignment.
No field contract, C implementation, freeze or completeness claim. Routine ends C06A; later bytes are outside this instruction map.
