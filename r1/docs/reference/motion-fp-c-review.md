# Motion detection floating-point operations in C

The final inline assembly in `native_motion_classifier.c` and
`native_motion_detection.c` is replaced by C. The shared
`native_float_to_signed.c` implements the ARM `VCVT.s32.f32` result and
cumulative FPSCR contract; the ring's ordered addition is a separate C function.
Neither motion file nor the new conversion provider contains inline assembly.

Finite inputs strictly between −2³¹ and +2³¹ use a defined, round-to-zero C
cast. Exact −2³¹ returns its integer bits without raising invalid. Other finite
overflow and infinities saturate to signed limits, while NaNs return zero.
An evaluated C zero-divided-by-zero operation raises IOC for those invalid
conversions; a volatile result prevents the compiler from dropping this effect
when logging is disabled. The recorded GCC9 strict IEEE floating-point profile
and resulting object are part of the contract. FP exception trap delivery is
not established. This avoids an undefined out-of-range C cast.

The motion classifier still converts once after its first log-mode query on a
state change, including when logs are disabled. The sampler uses the same
conversion for its log arguments. A noinline C addition retains left/right
operand allocation under the recorded Clang profile, preserving native NaN
payload precedence. Future compiler/profile changes require the same checks.

Verification of the final normal-build objects passes:

- 114,688 native-instruction/C conversion pairs: 3,584 raw inputs across 32
  rounding, flush, default-NaN and sticky-flag combinations. Inputs cover every
  exponent, signed zeros/subnormals, boundaries, infinities and NaN classes.
- 3,000 complete classifier pairs, including callback replacement/clearing,
  disabled logs, counter wrap, logical faults and FPSCR.
- 5,795 motion stream/sampler/ring/setup pairs with the classifier modeled.
  Expanded ring cases cover mixed NaN payloads, signaling NaNs, old sample/sum
  aliases, signed zeros and floating-point modes.
- 1,897 sampler-chain pairs executing the C sampler, square root, ring and
  classifier together, with logs and registration modeled.
- Six rejected defects: dropped invalid flag, wrong NaN saturation, invalid on
  exact signed minimum, early overflow boundary, unsigned conversion and an
  explicitly reversed VADD instruction used only in the negative test.

Comparisons retain external memory, provider arguments, logical faults and
FPSCR, with SP, preserved general/FP registers and interrupt masks checked.
Private stack bytes and caller-clobbered registers/APSR are excluded. Public
provider depths remain different: classifier logging native 32/C 40 bytes;
sampler logging native 40/C 72; stream setup native 8/C 16. No arbitrary provider
inspection of those private frames is claimed.

REA directly decodes the stock conversion at `0x483ac`. Earlier REA byte
capture for the classifier is verified against the locked application; current
GNU Thumb decoding confirms its conversion at `0x94cec` and sampler conversions
at `0x492f8`/`0x49324`. The current REA database does not recover the classifier
as a procedure, so no fresh classifier pseudocode claim is made.

All 708 units (634 application, 74 bootloader) compile and compose without
failures or duplicate strong symbols. Imports remain 178/34 and manifest
validation passes. Exact qualification selects none of the four motion bodies;
the new shared helper has no independent stock-function anchor. The canonical
plan remains 4,381 source-built executable bytes, 641,779 stock executable bytes
and 248 resource bytes; a fresh R1 hybrid matches stock. Physical sensor behavior,
concurrent operation, complete source-only linking and C byte identity remain
unfinished. The [machine receipt](motion-fp-c-review.json) records all hashes,
results, provider depths and limits.
