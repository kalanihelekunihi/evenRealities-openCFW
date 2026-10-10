# Localized inverse split behavior under pinned QEMU

Authentic inverse split reads packed source pairs from opposite ends, constructs coefficient B from `0x00008000 - A` lane-wise, computes exchanged dual products, and emits the high16 of two32-bit accumulators. Its assembly imaginary branch is:

```c
q31 cross = mulcax_s16_s(src_reverse, coefB);
q31 negated = packed_saturating_negate_s16(cross); // pneg.s16.s, two lanes
q31 imag = saturated_add_32(negated, exchanged_product_difference(coefA, src_forward));
out_imag = high16(imag);
```

The authentic C alternative uses scalar32-bit `-cross` before its exchanged product difference. Under this QEMU backend these operations differ even without the separate all-min-negative multiply corner.

For the endpoint-valid constant32767 spectrum, A starts `(16384,-16384)`, B becomes `(16384,16384)`, source DC/Nyquist pairs are `(32767,0)`. Cross product is `0x1fffc000`. Packed negate is `0xe0014000`; scalar negate is `0xe0004000`. The next product contributes `0x1fffc000`, leaving assembly accumulator `0x00010000` versus C0. The emitted split imaginary halfword is therefore1 versus0. Actual standalone opcode probe and complete split-stage comparison agree. The whole inverse pipeline later differs by2 after final doubling.

This recovers a source/operation distinction and reproduces a model result. It does not certify physical CK804 semantics, a stock hardware defect, numerical correctness for all inputs or universal source equivalence. No source or simulator patch was made.
