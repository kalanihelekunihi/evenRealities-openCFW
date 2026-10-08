# Post-scan full count and minimum diagnostics

Partial/unaccepted; 164 instruction bytes; inherited 72-byte frame. R11 is full eligible count; R5 minimum threshold and R7 its index remain full width.
At 47BF2E call 43D0CE with live arguments. Bit1 zero skips to BF5C. Otherwise set SP12=10, SP8=full R11, SP4=literal47C8C4, SP0=2043; call 43D574(4,literal47C548,literal47C544,literal47C540,2043,literal47C8C4,fullR11,10).
At BF5C query status afresh. Bit0 one goes BF6C; otherwise query again and bit2 zero goes BF80. At BF6C set SP0=10 and call 43CE9E(0x10800000,literal47C8C8,same,fullR11,10).
At BF80 signed full R11<1 branches to pending47C020. Otherwise query status at BF86; bit1 zero skips BFB0. Otherwise SP12=fullR5, SP8=fullR7, SP4=literal47CA98, SP0=2045; call 43D574(4,literal47C548,literal47C544,literal47C540,2045,literal47CA98,fullR7,fullR5).
At BFB0 query status afresh. Bit0 one goes BFC0; otherwise query again and bit2 zero goes pending BFD2. At BFC0 SP0=fullR5; call 43CE9E(0x10800000,literal47CAC0,same,fullR7,fullR5); fall through pending BFD2.
Preserve separate status queries and live incoming arguments. No narrowing, field contract, C implementation, freeze or completeness claim.
