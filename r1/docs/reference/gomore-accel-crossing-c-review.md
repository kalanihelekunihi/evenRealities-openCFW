# R1 accelerometer crossing baseline and dispatcher in C

`native_gomore_accel_crossing.c` adds two native-ABI C providers beneath the
still-unresolved accelerometer classifier at `0x67e4c`:

- `0x58aee`, `r1_gomore_accel_positive_fill_native`: descend from ring length
  through `end + 1`, carrying only strictly positive samples; then descend from
  end through begin and accumulate the carried value. Index subtraction and
  total wrap to 32 bits. A negative index gets one length correction, then
  narrows to signed eight bits. The denominator is wrapped `end - begin + 1`;
  zero returns zero, otherwise signed division precedes signed-halfword return.
- `0x56cf4`, `r1_gomore_accel_crossing_native`: read the signed cursor byte,
  compute the eight-slot baseline, then call the period estimator in mode 2
  followed by mode 1, with S0 = -1.0 and the same raw signed baseline. Each
  output survives only when its raw word plus `0xbd900000` is unsigned <=
  `0x01000000`; this accepts inclusive raw endpoints `42700000` / `43700000`
  and rejects nonfinite/negative/out-of-range words without FP comparisons.
  Mode-2 output is written before mode-1 scratch is reloaded and filtered.

There is one C baseline implementation, shared by its public native entry and
an always-inlined specialization inside the wrapper. The recorded GCC9 `-O1`
profile and reserved frame word produce the stock 40-byte wrapper frame:
mode-2 scratch is entry SP-32 and mode-1 scratch is entry SP-36. Actual period
entry SP and these pointer values are compared without normalization. Earlier
GCC/Clang frame variants remain under ignored `build/`; only the final verified
layout remains in the production source, and none enters the canonical plan. The final source needs no inline assembly,
executable blobs, opcode arrays or frame-pointer introspection.

The period boundary at `0x56f94` is explicitly declared as
`r1_gomore_accel_crossing_period_native` and remains unresolved in normal source
composition. It is bound to the real locked stock entry only in replay fixtures.
No stub or approximate replacement is supplied. Its generic model utility and
callback wrapper are now explicitly `_checked` APIs; the checked baseline
utility delegates to the shared native implementation.

Verification passes:

- 19,969 direct baseline pairs, including 15 logical faults: both descending
  passes, every eight-slot positive-mask combination, warm carry, zero and
  negative samples, strict positivity, signed cursor/index narrowing, wrapped
  sums/denominators, empty windows, halfword truncation, overlap, alignments and
  incoming-stack aliases.
- 411 direct wrapper pairs, including 12 fault cases: 147 controlled period
  responses cover raw filter boundaries, NaNs/infinities and signed cursor
  behavior; 216 regular cases execute the actual native period estimator under
  three FPSCR modes, waveforms, periods, baseline histories and cursors. Another
  36 alias/alignment cases and 12 bad-pointer cases also use the actual period
  body. Published scratch aliases exercise the post-mode-2 reload of mode 1.
- 216 focused native-classifier pairs call the new C wrapper 216 times and the
  real period estimator 432 times. Existing C leaves, statistics and square
  root remain in that chain. The 5,816-case stage matrix passes, including 66
  fault cases, but does not visit the crossing branch; it supplies no crossing
  coverage. The focused classifier and direct wrapper suites close that gap.
- 208 compiled checked-baseline pairs and six guard cases.
- Twelve rejected defects: omitted warm pass, zero accepted as carried data,
  wrong denominator, excluded begin, missing index narrowing, unsigned division,
  strict upper filter endpoint, changed filter offset, wrong first mode,
  wrong S0 seed, removed reserved frame word and unsigned cursor. A surviving
  unsigned-cursor mutation prompted nonperiodic padded history and explicit
  negative-byte cursor cases before the final suite passed.

Tests compare raw R0, full external memory, ordered public writes, logical fault
addresses/access widths, FPSCR, preserved registers, SP and masks. Wrapper and
classifier tests additionally compare period arguments, entry depths and exact
scratch pointers. Private frame bytes are excluded except effects of explicitly
published scratch aliases. Caller-clobbered register residue, APSR and complete
exception frames are outside the proof. Nonreturning wrapped loop domains,
concurrent mutation and physical sensors remain unverified.

The normal build compiles 716 units (642 application, 74 bootloader), with no
failures or duplicate strong symbols. Imports are 179/34: the sole added symbol
is the genuine native period dependency. `make sources-check` passes. Exact
qualification selects neither body. Canonical coverage stays at 4,381 source-
built executable bytes, 641,779 stock executable bytes and 248 resource bytes;
the fresh hybrid application matches the locked stock SHA-256. These results
do not establish a complete source-only link, source completeness or C byte
identity.

Classifier closure still requires its root, the native period estimator and
its downstream filters/statistics, plus autocorrelation dispatch at `0x56d78`
and its callee `0x5c5f0`. REA direct-reference observations do not rule out
indirect callers. The [machine receipt](gomore-accel-crossing-c-review.json)
records source/object hashes, REA evidence, fixtures, build and qualification.
