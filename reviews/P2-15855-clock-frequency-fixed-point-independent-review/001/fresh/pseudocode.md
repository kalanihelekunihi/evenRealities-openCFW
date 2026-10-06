# Clock frequency fixed-point calculation, 0x4D38EA..0x4D3914

Partial; accepted:false.42 instruction bytes. Leaf no stack. input=entryR0, requested=entryR1, exponent=entryR2, output=entryR3. Ordered architectural operations:

S0bits=requested
S0=VCVT.F32.U32(S0bits)
R1=1
R2=LSL_register(1,exponent) // uses low8 of exponent, zero for shifts>=32
R0=UDIV(input,R2)
S1bits=R0
S1=VCVT.F32.U32(S1bits)
S0=VDIV.F32(S0,S1)
S0bits=VCVT.U32.F32_fixed(S0,fractional_bits=15)
word[output]=S0bits
return0

Retains single-precision rounding/conversion steps, not collapsed to integer ratio. Output pointer unchecked; R1=1,R2=shiftresult,R3=output,R4-R12/SP unchanged; S0/S1 changed. UDIV zero denominator depends on CCR.DIV_0_TRP; floating zero denominator/NaN/overflow/conversion and FP availability depend on architectural FP state. No universal normal result asserted for these boundaries; FP flags not discarded from behavioral scope. Numeric FP and fault behavior not independently executed yet. No C/admission/gates.
