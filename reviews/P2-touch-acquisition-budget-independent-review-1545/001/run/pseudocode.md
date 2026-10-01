# Acquisition budget at 7288

The exact 112-byte body [7288,72F8) has 0 instructions. R0 selects a 144-byte record from descriptor word +12; R2 is the descriptor. R1 is overwritten before use. Resolve row through record word +0 and context through descriptor word +8. Let width be row halfword +14 and mode be row byte +33 & 3.

Compute base = context halfword +48 + context halfword +50 + context byte +83. Add (width >> 2) times a halfword pair: offsets 62 and 66 for mode 2, otherwise offsets 64 and 68. Then add width times (context byte +77 + row halfword +44). For mode 2, double the resulting wrapped word. Multiply by record byte +132 modulo 2^32, divide unsigned by 46 using original A6C0, then return quotient times 5 modulo 2^32. All intermediate machine additions and multiplications wrap at 32 bits. Restore the 24-byte frame.

108 original-instruction fixtures vary all three indices, all four modes, independent patterned fields, width extrema and factors 0/1/255. Original division executes. Fixtures verify quotient and wrapped result, return and restored frame, and absence of non-stack writes. No sensor acquisition occurs in this body; the historical acquisition boundary was a timing calculation. Index and pointer validity are caller obligations. Physical time units remain unresolved. No canonical admission or C implementation.
