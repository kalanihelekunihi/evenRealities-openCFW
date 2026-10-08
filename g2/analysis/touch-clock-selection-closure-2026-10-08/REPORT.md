# Stock clock-source initialization and wake timer conversion

Independent source: `g2/components/touch/clock_selection_offline/clock.c`. **1,583 fresh original-instruction comparisons pass**, including720 mixed three-widget clock-initialization cases. No function-entry stubs. Integer division on the independent side is compiler-generated libgcc code; no original executable dependency is used.

Recovered functions: SSC decision0x61f0; polynomial period0x6220; PRS auto0x623c; LFSR dither amplitude0x6262; allowed dither0x6270; SSC auto0x6294; LFSR auto0x6352 (range selector0x6330); full clock initialization0x6384; wake timer conversion0x5d70. The public semantic comparator is verified against the pinned official source247a9a0f79eb976f144f5fbeb29488c1c2606517, SHA777300a0129f032a507e0a222bae0f321f5d4423da2ef4778058255383db5890.

## Layout and recovered behavior

Widget configuration stride144: context pointer+0, methodbyte122, dither percentage135, automatic selection mode136. Runtime stride60: sense divideru16+14, sourcebyte33, conversion countu16+44, LFSR rangebyte56. Internal context: polynomialu16+60, fine-init countbyte77, LFSR scalebyte78.

Source lowbits0/1/2 select direct/SSC/PRS. Bit4 selects SSC-auto; bit8 selects PRS-auto. LFSR byte bit128 requests automatic range selection. These labels are SDK semantics corroborating stock branches, not measured physical clocks.

Polynomial period is based on the highest set bit of a16-bit polynomial, yielding2^N-1; even polynomial0 yields1 in stock. Dither amplitude is `1 << ((range & 3) + scale + 1)`, with ARM register-shift behavior. Allowed dither is the smaller of percentage-based and minimum-divider-margin values after scaling. Multiplication/subtraction wrap32 bits. Range quantization selects0/1/2/3 for allowed values<=3,4..7,8..15,>=16.

SSC-auto first checks dither against the allowed limit. Mode2 skips period-duration tests; other modes require enough conversions for a full polynomial period; mode0 additionally requires exact divisibility. PRS-auto requires conversions plus fine-init to reach(polyPeriod+1)/4 and returns source2 or0 with bit8 retained.

The full function scans exactly three widgets. It updates automatic LFSR/source fields **before** validating the divider. Validation deliberately uses the original source byte for whether to add SSC dither to the minimum, even if auto selection wrote a different source. Methods1/10 reset minimum to8; other methods set status1 without resetting the carried minimum. A later bad divider replaces status with0x800 and stops the loop. Earlier mutations remain; later widgets are untouched. These malformed configurations are observed machine behavior, not supported SDK configurations.

## Wake timer and exact public helper evidence

Timer conversion computes the wrapped32-bit product of input and internalu32+44, shifts right14, subtracts1 if nonzero, and clamps to65535. The SDK contract identifies the input as desired microseconds and factor as ILO compensation; the instruction tests establish the integer conversion, not real elapsed time or measured ILO frequency. Large inputs may wrap before the clamp, so a64-bit rewrite changes behavior.

Two verbatim public helper bodies compile exactly with Arm GNU13.3 -Og in a minimal documented translation unit: GetPolySize0x6220 is28 bytes including its literal, GetLfsrDitherVal0x6262 is14 bytes. Both have zero relocations and a unique full-byte match in this locked raw image. **42 additional attributed bytes**, distinct from the earlier208 PDL bytes. Four optimization levels were screened. This is selected public-function attribution, not a whole SDK build, a uniquely identified producer/compiler, or whole-image equality. The tested macro environment explicitly defines LFSR_BITS_RANGE_MASK=3.

Machine shift inputs>=32 are included in independent-source tests using explicit ARM semantics; the public C expression's portable behavior for such inputs is not endorsed. Direct SSC-helper tests exclude zero period. Coherent synthetic contexts only; no analog/frequency/timing claim.
