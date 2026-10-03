# Independent review 6545

Disposition: **PASS_SCOPED**; `accepted:false`.

The complete 320-byte span 0x415AB6..0x415BF6 and packet artifacts match the pinned source. GNU Thumb decoding supports the stated signed capacity guard (<4 returns -3), F32 zero fast path, exponent limits (>=31 returns -2; <-23 returns -1), and raw IEEE word decomposition with an unconditional mantissa bit-23 OR. The fixed-point integer/fraction branches, sign emission, integer-helper arguments, post-helper NUL scan, precision clamp, decimal digit loop, one-digit lookahead rounding, backward dot skip/carry, final NUL, and output-length return match the instruction sequence. Capacity does not bound the integer-helper call or the zero-fraction fast output.

The LDR.W at 0x415AD4 targets literal 0x415FE4, whose word is 0x00302E30. It is stored whole for the zero input and the routine returns 3. The frame saves R2 at SP[0], but nonzero processing stores the raw float there; the common POP therefore returns that raw word in R1 on that path. Error and zero paths before this overwrite retain the incoming saved-R2 value. The cited child helper's implementation and possible alias effects remain outside this map.

This is static, source-bounded behavior only; it does not claim IEEE-generic behavior or canonical admission. No canonical files or gates changed.
