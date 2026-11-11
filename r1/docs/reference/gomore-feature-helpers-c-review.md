# R1 IIR, percentile and confidence helpers in C

`native_gomore_feature_helpers.c` supplies the feature reducer's three remaining
lower providers: IIR filtering `0x64274`, percentile calculation `0x7ed30`, and
bounded linear complement `0x56c54`. The reducer's filter declaration now includes
the observed word return, without changing reducer object bytes. Guarded generic
utilities retain their original bodies under `_checked` names. No inline assembly,
trap, executable data, persistent RAM or stub is added.

The IIR implementation captures each input before overwrite, cold-starts its two
input/output histories, multiplies each coefficient/product in hardware float,
then uses the native raw promotion/add/reverse-subtract/narrow primitives in their
original operand order. History shifts precede final narrowing/publication. Its
signed-word loop returns the original count, including zero/negative counts. The
coefficients are pinned to the locked ROM literal at `0x6437c` pointing to table
`0xbd648`: feedback `3f800000 bfe71223 3f511616`, feedforward
`3dbba7a8 00000000 bdbba7a8`. The copied zero-order feedback word is unused by the
native recurrence. C embeds the used constant values; the private ROM-copy and
history storage operations are not instruction-identical. The coefficient proof
binds the locked image and complete table words.

Percentile calls inclusive sort before processing endpoints. It computes and
preserves the step before endpoint returns, using signed count-minus-one
conversion except singleton step zero. The index uses defined-range C conversion;
overflow/NaN cases explicitly reproduce VCVT saturation/zero and IOC via the
already-reviewed C invalid-operation helper. Address arithmetic wraps as native
words. Remainder selection uses a **signed raw encoding comparison** against
`0x3dcccccd`, not a floating comparison. Both interpolation values are loaded
before the repeated zero-step check. Thus a singleton interpolation path can read
the following sample even though slope stays zero; the raw C provider preserves
that access and final nonfused multiply-add rather than inventing an empty or
singleton guard. Huge-count sorting is modeled only in the dedicated raw-word
cases, with caller-register clobbers.

Confidence preserves signed raw-word gates `0x40a00000` and `0x3f333333` before
arithmetic. In particular, positive and negative NaN encodings do not take the
same path. Secondary promotion/division by raw double 0.7 precedes primary float
division by five. Native soft add, multiply by 0.5, reverse subtract from one and
narrowing preserve the stock non-IEEE encoded behavior.

Final production verification includes:

- **442 IIR pairs**, including signed count boundaries, raw special values, and
  42 finite 250-sample impulse/wave/noise vectors. The impulse's first published
  coefficient is separately asserted as `0x3dbba7a8`.
- **500 percentile pairs** with actual native qsort and the C comparator, plus
  **64 modeled-sort raw-word cases** covering signed extremes and out-of-range
  conversion. The complete suite includes **21 fault comparisons**: 18 in the raw
  modeled-sort matrix and three dedicated faults, including singleton's following
  sample read. Modeled sort checks raw arguments and clobbers caller registers;
  it does not establish actual huge-count sort safety.
- **2,823 confidence pairs**, including all 17 selected raw patterns crossed with
  each other under seven rounding/FZ/DN configurations, plus 800 randomized pairs.
- Across these direct cases, raw return/result, buffer state, ordered external
  writes, full FPSCR, native soft-provider argument traces, completion, SP and
  preserved general/FP registers agree. Native/C qsort callback pointers are
  checked against their respective known implementations, then normalized in the
  trace because the C comparator necessarily has another code address.
- **90 actual reducer pairs**, plus six faults and four incoming-argument aliases,
  use all three C helpers. Another **180 modeled reducer pairs**, three targeted
  fallback vectors and four argument aliases retain the prior provider-clobber
  and output-pointer reload checks. Initial statistics, filter, extrema and
  confidence are modeled in that second fixture; it is not additional C filter
  or confidence body coverage.
- **112 actual optical-root pairs** pass the strict earlier trace, including exact
  nested extrema counter pointers and SP. They exercise **24 C IIR, 48 C percentile
  and 16 C confidence calls**, alongside C reducer/control and other reviewed
  processing helpers.
- **13 compiled semantic defects are rejected**: IIR feedforward, feedback,
  history, zero term and return; percentile step, singleton, remainder sign,
  upper read and saturation; confidence bound, signed gate and factor. Rejection
  requires an actual stock/C mismatch; compile/link and harness errors do not count.

The private frames differ: IIR C uses 64 bytes versus native 104 at soft calls;
confidence C uses 16 versus native 24; percentile C uses 40 versus native 16 at
initial qsort. The later qsort recursion adds its own frames. Private stack writes
and all hardware bus/alignment/fault timing are outside proof. Actual replay still
executes stock qsort and soft-double primitives, and caller fixtures execute stock
double power/square root and remaining optical code. This is not a complete C
runtime, whole executable identity or physical hardware validation.

The final build passes **704 units: 630 application and 74 bootloader**, with no
failures or duplicate strong symbols. All **702 prior objects** outside the
renamed checked-API owner retain their bytes. All **703 probe objects** outside
that owner are byte-identical to final objects, binding the caller/defect replay
checkpoint to the final build. All three lower reducer imports resolve, reducing
application imports from 182 to **179**, with no added imports; bootloader imports
remain **34**. The normal manifest includes the new source under the strict GCC
floating-point profile.

Scoped qualification selects zero regions. Hybrid equality passes with 4,381
source-built executable bytes, 641,779 stock executable bytes and 248 resource
bytes; the canonical plan remains unchanged. The interval merger, optical root,
complete source linking, whole executable byte identity and physical validation
remain open. The [receipt](gomore-feature-helpers-c-review.json) binds evidence.
