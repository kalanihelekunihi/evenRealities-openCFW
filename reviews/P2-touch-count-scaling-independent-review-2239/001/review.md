# Independent review 2239

**Result:** PASS_SCOPED.

The source hash, `[0x5528,0x5548)` body hash, and all candidate artifact hashes match the receipt. The Thumb/M-class decode agrees with the pseudocode: the helper masks mode to its low two bits and returns the input count unchanged unless that value is 2. In that case it uses logical right shift by two for kind 1 or 10, and by one for every other kind. The epilogue restores R4 and SP; R1 and R2 are unchanged, and R3 contains the masked mode.

An isolated replay regenerated all 1,232 fixtures. Its Cartesian cases cover seven kind values, all 16 modes, and 11 counts including high-bit and maximum values. The assertions verify result and R1/R2/R4/SP preservation.

**Limits:** This is bounded private instruction evidence. It does not establish the physical meaning of the inputs or caller completeness. No canonical admission is made.
