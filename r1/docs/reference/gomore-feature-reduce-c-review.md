# R1 locomotion feature reducer in C

`native_gomore_feature_reduce.c` implements `0x68840`, including its noncontiguous
native body. The control extractor's previously explicit reducer import now
resolves. Its declaration is updated to the reducer's native zero word return;
this produces unchanged control-extractor object bytes. The guarded generic
utility retains its behavior under `_checked`; its body is unchanged.

The reconstruction follows instructions rather than decompiler parameter guesses
or the earlier guarded utility. Mean precedes deviation. Normalization preserves
the signaling zero test and then the in-place native IIR call. The extrema return
status is ignored, and both sort/percentile paths run even for empty counts.
Thresholds preserve native promotion, multiplication by the raw double 0.2 and
native narrowing. The two crossing scans retain byte indices, strict ordered
thresholds, the last opposing index when exhausted, byte output counts, and
reload the previous index after publishing a rate. Rates use native 12.5/delta*60
soft-double operations with the distinct native integer/float promotion paths.

Fallback scans both read the second extrema bank. The first uses second-count
minus one; the second uses first-count minus one. The upper distance bound is
raw double `0x405cbfffffffffff` (just below 115), and later/earlier indices are
reloaded before conversion and rate publication. Three targeted vectors establish
these differing bounds separately from general replay. Output initialization
occurs after selection/fallback, not at entry. Mean/deviation bounds and included
sums preserve nonfused FP operand order and strict ordered comparisons. The
squared sum promotes the current float accumulator, adds the full double power,
and narrows each iteration. The primary output is stored before confidence work;
the secondary argument is reloaded after the confidence provider returns.

To retain native extrema publications, the outer C frame is **96 bytes**, with
minimum count at own SP+20 and maximum count at SP+24. A volatile private aggregate
retains those offsets; only the two native count words are initialized. The
fallback and final statistics are private C helpers. Their additional call frames
and the full private layout are not instruction-identical. No assembly, trap,
executable data or persistent RAM is introduced.

Final production verification includes:

- **90 actual-dependency pairs**, plus **six invalid-pointer faults and four
  incoming stack-argument alias cases**. Inputs include constant signals, noisy
  waves, raw FP special values, seven rounding/FZ/DN settings, and overlaps among
  signal, extrema banks, controls and outputs. Results, externally visible memory,
  ordered writes, full FPSCR, public provider arguments, SP and preserved general/FP
  registers agree. There are 61 square-root/confidence calls in
  this complete fixture, including alias cases.
- **180 modeled pairs**, **three targeted fallback vectors**, and **four incoming
  argument aliases**. Initial mean/deviation, filter, extrema and confidence are
  modeled; the model clobbers caller-saved general/FP registers, emits zero through
  twenty extrema per bank and varied status returns, mutates the incoming primary
  argument after native capture, and changes the secondary pointer at confidence
  return. Provider traces and outputs agree. Modeled invalid-pointer writes are
  excluded; the six native-dependency faults provide that evidence.
- **112 actual optical-root pairs**, invoking the C reducer **24 times** along with
  C control extraction, expansion, fill, peak matching and existing processing
  helpers. The strict earlier trace retains exact nested extrema count pointers
  and call SP, with no pointer normalization. The verifier now records direct C
  extrema entries once, as well as redirected native calls; it does not omit those
  calls from comparison.
- **11 compiled semantic defects rejected**, covering normalization, threshold
  scale, percentile, rate scale, fallback bound/neighbor, upper bound, output order,
  minimum included count, power exponent and confidence divisor. Compile/link or
  harness errors do not count as rejected controls.

Actual fixtures still execute native IIR filtering, percentile, confidence,
qsort, double power/square root and soft-double primitives. C supplies statistics,
extrema, sort and the reducer; caller fixtures also use the other reviewed C
pipeline helpers. Private stack writes are excluded. The result is bounded
behavioral evidence, not a complete source-only runtime, all possible input proof,
physical bus/alignment proof or hardware validation.

The normal build passes **703 units: 629 application and 74 bootloader**, with no
failures or duplicate strong symbols. All **701 prior objects** outside the renamed
checked-API owner retain their bytes. Application imports change from 180 to 182:
`r1_gomore_locomotion_feature_reduce_native` resolves, and three lower providers
become explicit: `r1_gomore_sleep_iir2_filter_native` (`0x64274`),
`r1_gomore_sorted_percentile_native` (`0x7ed30`) and
`r1_gomore_bounded_linear_complement_native` (`0x56c54`). Bootloader imports remain
34. No stub hides these dependencies.

Scoped qualification selects zero regions. Hybrid equality passes with 4,381
source-built executable bytes, 641,779 stock executable bytes and 248 resource
bytes; the canonical plan is unchanged. The lower providers, remaining optical
selectors/root, complete source linking, whole executable byte identity and
physical validation remain open. The [receipt](gomore-feature-reduce-c-review.json)
binds current evidence.
