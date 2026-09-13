# Binary32 scaling cutoff correction

`runtime_gx8002_scalbnf.c` preserves the observed stock algorithm for comparison.
`build_gx8002_scalbnf_probe.build(corrected=True)` derives the corrected source by
changing `exponent < -22` to `exponent < -24`, checks that the original expression
occurs exactly once, and records the derived source and ELF hashes.

The exponent variable is a biased binary32 exponent. At -24 the normalized
significand times its power of two is between one half and one unit of the
smallest subnormal. At -23 it lies between one and two units. These cases must
reach the final multiplication by 2^-25 so that rounding can use the full
significand. For nearest-even, exponents below -24 round to signed zero.
The stock early-underflow branch discards these representable rounded results.

The corrected build intentionally differs from stock. Current tests execute
actual source and stock instructions under an explicit integer nearest-even
multiplication model, then compare against direct dyadic scaling. They include
all finite exponent classes with representative fractions, both signs, selected
boundary scale arguments and INT32_MIN/MAX. This is sampling, not an exhaustive
proof. Other rounding modes, floating-point status flags, nonfinite inputs and
hardware behavior remain unqualified. No upstream fix commit is claimed.

Subsequent provenance evidence: Newlib mirror commit
`4aa696c8d6294897411cf78cae87f7f4680e9687` contains this cutoff as
`FLT_SMALLEST_EXP -22` in `newlib/libm/common/fdlibm.h`, consumed by
`sf_scalbn.c`. The source snapshot and hashes are retained under
`build/upstream-newlib-math`. This identifies an upstream lineage candidate;
it does not identify the exact stock build commit or claim an upstream fix.
