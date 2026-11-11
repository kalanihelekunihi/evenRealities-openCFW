# R1 accelerometer period-estimator IIR and transition helpers in C

`native_gomore_accel_period_helpers.c` implements two native-ABI dependencies
of the unresolved period estimator at `0x56f94`:

- `0x8f3c8`, `r1_gomore_accel_iir4_native`: select profile 1 only when the
  raw profile word equals one, otherwise use the second coefficient set.
  Four multiply/add/subtract stages wrap to 32 bits. Input-history reads precede
  output-history reads; descending shifts interleave input and output stores,
  including when buffers overlap. Store the raw input, divide the signed wrapped
  accumulator by 1000, store that result and return its full R0 word. REA's
  recovered `void` signature omits this instruction-confirmed return.
- `0x761f8`, `r1_gomore_accel_transition_native`: read current/previous bytes,
  interval word and initialized byte in native order. Preserve wrapped sums,
  signed ratio-word thresholds, signaling shape comparisons and target-unordered
  rejection. Initialization stores interval, flag byte and float estimate in
  that order. The initialized path uses strict encoded 0.9/1.1 bounds and the
  native quarter/three-quarter mix, with fresh estimate reads in native order.
  Raw R0 is preserved on accepted and rejected paths, including encoded-key
  residues from the original software comparison and raw float ratio words.

The typed IIR tables at `0xbd294`, `0xbd2a8`, `0xbd2bc`, `0xbd2d0` are:

| Table | Words |
| --- | --- |
| profile 1 feedback | 1000, -3722, 5276, -3374, 822 |
| profile 1 feedforward | 434, 0, -869, 0, 434 |
| other feedback | 1000, -2595, 2746, -1459, 347 |
| other feedforward | 9131, 0, -18262, 0, 9131 |

These are integer coefficients, not executable words. The native private table
copies are replaced with typed immutable C data. No assembly, executable blob
or opcode array is introduced.

Transition arithmetic calls the existing raw-bit C conversion/add/multiply/
normalization/rounding providers. It compares their encoded double keys in C:
negative words retain their encoding; other words map to `2^63 - bits`.
The native reverse-comparison carry means `key(b) >= key(a)`. This removes this
caller's dependency on an implicit APSR-return adapter without changing that
adapter for other firmware callers. Ordinary IEEE conversions/comparisons
would lose stock exponent/zero-sign behavior. S0 is target, S1 is unused,
S2/S3 are the shapes; R0..R3 point to interval, history pair, flag and estimate.

Verification passes:

- 7,517 direct stock/C pairs: 1,663 IIR and 5,854 transition cases, including
  28 logical faults. They cover all profile branches, arbitrary wrapped word
  arithmetic, overlapping/interleaved histories, alignments, signed ratios,
  threshold equality, exact double boundaries, floating-point classes, all
  rounding modes, cumulative flags, aliases and ordered partial writes.
- The same 7,517 cases also pass with reconstructed C shifts, binary32/binary64
  conversions, double add/multiply, normalization and rounding. The linked arithmetic subset needs no native-address bindings or placeholders.
  An independent linkage audit confirms no undefined symbols and no retained
  assembly-bearing classifier/division/flag adapters. This is a helper/math
  subset link, not a final firmware link.
- 318 native-period pairs, including 12 faults, pass with both native and C
  arithmetic backends. Each exercises 62,400 C IIR calls and 1,215 C transition
  calls. Entry/return traces compare live parent state, raw results, arguments,
  exact buffer addresses, entry depth and FPSCR, with no pointer normalization.
- Coverage inspection initially found no transition updates in the broad
  waveform matrix. A stock-only search found four inputs in 19 attempts. Paired
  replay of those inputs under three FP modes now exercises 12 initializations
  and 90 initialized updates: 102 state changes and 60 estimate changes. Native
  and C backends agree. IIR replay sees 295 distinct input words and 5,918
  distinct returned words. Search inputs and scope are recorded in the receipt.
- 216 focused classifier pairs pass with each arithmetic backend, through the
  existing C preprocessing/statistics/crossing/math chain and actual native
  period body. Each exercises the new IIR 86,400 times and transition 2,520
  times. This does not turn the classifier or period parent into source providers.
- 212 compiled checked-IIR pairs and two guard cases pass. The checked utility
  now delegates to the shared native body. The generic transition state API is
  explicitly `_checked` and retains its stricter overflow/updated-flag policy;
  it is distinct from the raw native contract.
- Seventeen rejected defects: wrong profile/coefficient, unsigned division,
  ascending history shifts, wrong feedback sign, raw double ordering, ordered
  target test, unsigned conversion/ratio ordering, strict threshold substitutions,
  one-ULP low/high bounds, narrowed consistency width, swapped state stores,
  wrong mix weight and wrong initialization return.

Tests compare raw R0, external memory and ordered writes, logical faults,
FPSCR, masks, SP and preserved registers. Private coefficient copies/save frames,
caller-clobbered register/APSR residues and complete exception frames are
excluded. Private frames differ: IIR uses 24 bytes versus native 72; transition
uses 48 versus native 40, plus nested C calls. Parent-buffer pointers and helper
entry depths match, but on-device stack headroom is not validated. Concurrent
mutation, inputs into private callee frames and physical sensors remain outside
this proof.

The fresh normal build compiles 717 units (643 application, 74 bootloader),
without failures or duplicate strong symbols. Import sets remain 179/34 and
`make sources-check` passes. Exact qualification selects neither body. Canonical
accounting stays at 4,381 source-built executable bytes, 641,779 stock executable
bytes and 248 resource bytes. The fresh hybrid application matches the locked
stock SHA-256. Compilation, relocatable composition and retained-stock hybrid
assembly do not establish source completeness, a complete source-only link or
C byte identity.

The native period parent, autocorrelation dispatch/estimator and classifier
root remain unfinished. REA observes the period estimator as both helpers'
direct caller; indirect uses are not excluded. The
[machine receipt](gomore-accel-period-helpers-c-review.json) records evidence,
source/object hashes, tests, input search, backend closure and qualification.
