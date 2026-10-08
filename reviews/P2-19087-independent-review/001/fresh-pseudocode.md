# Guarded entry 0x46921C..0x46928C

Partial/unaccepted; 112 instruction bytes. PUSH R0/R4/R5/LR then SUB SP16 creates32-byte frame. SP16 holds original R0 word; SP20/24 saved R4/R5; SP28 saved LR. Diagnostic SP0/SP4 are local slots and do not overwrite saved original input.

R0=literal 0x469B44; load unsigned byte [R0]. Byte zero branches 0x46926E. Nonzero calls 0x43D0CE with live R0/R1/R2/R3. Fresh result bit1 diagnostic: SP4=literal0x469B48; SP0=88; R3=literal0x469B4C; R2=literal0x469B38; R1=literal0x469B3C; R0=4 -> 0x43D574. Separate fresh mask bit0 or conditional third fresh bit2 enables R1=literal0x469B50, R2=R1, R0=0x10000000, liveR3 ->0x43CE9E. This nonzero guard arm branches0x469384 outside chunk.

Zero guard arm: R0=1, R1=literal0x469B54, store byte1 at[R1]. Call0x46919E with live arguments; save full returned bool toR5. Fresh unsigned byte fromSP16 is low8 original R0; bytezero branches0x46931C. Nonzero calls0x443484 with R0 that byte and live otherargs; FULL childresultzero branches0x46931C, nonzero continues0x46928C diagnostics outsidechunk. Preserve distinct global literal addresses and saved-input byte read. No interpretation of lock/state or child contracts; no wholefunction completion, C, runtime or gateclaim.
