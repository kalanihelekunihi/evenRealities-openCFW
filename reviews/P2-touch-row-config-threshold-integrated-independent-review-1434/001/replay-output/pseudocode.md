# Validator with original threshold flags

Original 6384 now executes 623C and its original 6220 dependency on the bit-3 path, alongside the original range-factor and shift chains inherited from 1425. The initialized context scale and offset, and row halfword +44, are zero: threshold is zero, so 623C returns 10 and the parent stores that byte. Subsequent branch decisions retain the originally loaded flags.

The 216 original-instruction fixtures check exact writes, remaining 6294 and A6C0 controls, final status and frame. Broader threshold inputs are covered by 1431. Physical meaning, pointer validity and 6294 remain unresolved. No canonical admission or C implementation.
