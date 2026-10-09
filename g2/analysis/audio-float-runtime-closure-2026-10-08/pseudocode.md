# Float-runtime bit algorithms

```
floor/round/ceil(input_bits):
  exponent = bits.exponent -126
  exponent<=0: apply signed-zero/unit/half-case rule
  exponent>=24: return input bits unchanged
  mask = 0x00FFFFFF >> exponent
  floor: add mask only for negative input, then clear mask
  ceil: add mask only for nonnegative input, then clear mask
  round: clear lower-half mask; add mask; clear mask

fmod(numerator_bits,denominator_bits):
  classify raw exponent/significand without float arithmetic
  finite / zero: errno[0x20074F14]=33; return0x7FFFFFFF
  Inf/NaN numerator orNaN denominator: return0x7FFFFFFF
  finite /Inf orabs(numerator)<abs(denominator): return numerator
  abs equality: return numerator-signed zero
  normalize subnormal significands usingCLZ
  reduce exponent gap in8-bit chunks with integer remainder
  reduce final remainder, normalize, restore sign and exponent
  underflowed result uses guarded ARM-compatible right shift
```

No routine modifiesFPSCR. Preserve exact payload bits for floor/ceil/round nonfinites. Fmod invalid classification/errno behavior follows stockCMN/carry paths, not a host floating operation. Scalar errno address is provenance-bound data; it is not an executable blob. Calls from SYSPLL generator supply floatMHz values; the typed header is an offline recovered interface.
