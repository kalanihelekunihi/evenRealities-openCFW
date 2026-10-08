# Post-scan full maximum index diagnostics

Partial/unaccepted; 78 instruction bytes; inherited 72-byte frame. R6 maximum threshold and R8 its index are full width.
At 47BFD2 query 43D0CE with live arguments. Bit1 zero skips BFFE. Otherwise set SP12=fullR6, SP8=fullR8, SP4=literal47CAC4, SP0=2046. Call 43D574(4,literal47C548,literal47C544,literal47C540,2046,literal47CAC4,fullR8,fullR6).
At BFFE query status afresh; bit0 one goes C00E. Otherwise query again; bit2 zero goes pending47C020. At C00E set SP0=fullR6; call 43CE9E(0x10800000,literal47CAC8,same,fullR8,fullR6). Fall through pending47C020.
Preserve separate queries, live arguments and full values. No field contract, C implementation, freeze or completeness claim.
