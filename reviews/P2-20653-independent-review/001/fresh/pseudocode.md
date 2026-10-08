# No free slot diagnostics and explicit pointer return

Partial/unaccepted; 76 instruction bytes, inherited40-byte frame. At0x47A80A query0x43D0CE with live arguments; bit1 zero skips0x47A830. Otherwise write literal47AE74 SP4 and947 SP0; call0x43D574(4,literal47AE28,literal47ADCC,literal47AE6C,fifth947,sixthliteral47AE74).
At0x47A830 query status afresh. Bit0 one enters0x47A840; otherwise query again and bit2zero skips0x47A84E. Maskpath loadsR1=literal47B4AC,R2=R1, leaves liveR3 and calls0x43CE9E(0x10000000,R1,R2,liveR3). At0x47A84E explicitly R0=0.
Shared0x47A850 addsSP16 to discard saved entryR0..R3/writable diagnostic slots, then POP R4,R5,R6,R7,R8,PC consumesremaining24bytes. The success branch0x47A808 arrives withR0=selectedR6; failure arrivesR0zero. Restore40-byte frame and return explicit fullpointer/zero rather than saved entryargument. No C, freeze or completeness claim.
