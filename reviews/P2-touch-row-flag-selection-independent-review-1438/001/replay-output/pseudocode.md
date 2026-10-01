# Row flag selection at 6294

The 150-byte code body [6294,632A) is followed by alignment NOP and literal 65535 at 632C. Sum row halfword +44 and context byte +77, saturating at 65535. Clear bit 7 of row byte +56, read context byte +78 as shift, record byte +136 as decision mode and +135 as percentage. Original 6220 yields the context halfword +60 scale; original 6262 yields a shift factor from the cleared row byte and shift.

Original 6270 receives row halfword +14, base 8 for record mode +122 equal to 1 or 10, otherwise 4, percentage and shift. Original 61F0 receives decision mode, factor, returned budget, scale, and saturated total as its fifth stack argument. Return its boolean OR 4.

The 1152 fixtures execute the entire recovered helper chain. Only unsigned division helpers A6C0/A7CC are controlled; their exact argument traces, returned flag and restored frame are checked against a separate arithmetic model. No zero scale divisor occurs because 6220 returns at least 1. Wider inputs, division bodies, pointer validity and physical meanings remain open. No canonical admission or C implementation.
