# R1 accelerometer axis gate and fixed ring score in C

Two more native-ABI C providers implement direct dependencies of the unresolved
accelerometer classifier at `0x67e4c`:

- `native_gomore_accel_axis_gate.c`, stock `0x582c4`, reads three circular
  histories in x/y/z order. Index subtraction and sums wrap to 32 bits; a
  negative index gets one length correction, then narrows to signed eight bits.
  Threshold counts wrap to bytes and are read as signed bytes by the final
  >= 3 gate. Ranking starts with two zero sums and axis-zero selections, uses
  strict comparisons, and can select axis zero twice when all sums are
  nonpositive. The ninth caller argument is unused by the native eight-argument
  function; replay varies it independently.
- `native_gomore_accel_ring_score.c`, stock `0x56a0c`, sums six circular
  histories, sorts the final three wrapped signed sums, and evaluates the fixed
  model with the native sequence of integer-to-float conversions, non-fused
  multiply/adds, division, bias and scale. It uses the shared C native float-to-
  signed conversion, clamps to [-32000, 32000], and returns a signed halfword.
  Its early guard uses the sign bit of wrapped `length - window`.

The six typed coefficient words at `0xbd27c` are `ba8e0d9f`, `3c5d639e`,
`ba815ee5`, `bca9fb3c`, `bc0befee`, `3c2c7c80`. Bias at `0x56b98` is
`3f8f797d`, scale is `447a0000`, and the empty-window score starts at +0.
The C score replaces the native private coefficient-copy scratch with typed
immutable constants. No public callback or buffer is published by that copy.
No executable blob, opcode array or inline assembly is introduced. The recorded
strict GCC9 FP profile is part of the tested contract.

Verification passes:

- 8,671 direct axis-gate pairs, including 18 logical faults. Cases exercise
  signed byte wrap, equal/negative sums, independent threshold counts, strict
  rank ties, 32-bit sum overflow, one-wrap/signed-byte indexing, input overlap,
  incoming-stack aliases, pointer alignment and signed/nonpositive counts.
- 5,018 direct fixed-score pairs, including 36 logical faults. Cases cover
  permutations of the final three channels, wrapped sums, all rounding modes,
  cumulative FPSCR flags, empty/negative windows, clamp boundaries, one-ULP
  bias-sensitive integer boundaries, alignments, aliases and malformed pointers.
- 5,816 actual accelerometer-stage pairs, including 66 fault pairs, call each
  new C provider 2,214 times. A separate 216-pair classifier matrix exercises
  each provider 216 times. Existing C preprocessing, collector, history,
  statistics, conversion, square root and seven previously reviewed classifier
  leaves remain in the replay chain. Classifier and spectral routines stay stock.
- 640 compiled checked-axis-wrapper pairs and seven guard cases. The old axis
  utility now delegates to the native provider and is named `_checked`. The
  general six-channel utility retains its caller-supplied model interface and
  is explicitly named `_checked`; it does not claim the fixed native ABI.
- Seventeen rejected defects: unsigned counts, removing zero baselines,
  inclusive best/runner ties and primary/secondary thresholds, missing index
  narrowing, wrong runner count, ordinary signed guard, unsigned sum conversion,
  wrong first coefficient/sort, one-ULP bias, fused multiply-add, shifted upper/
  lower clamp thresholds and wrong empty-window value. A clamp mutation
  survivor prompted narrow-clamp-boundary cases before the final suite passed.

Tests compare raw R0, complete external memory, ordered public writes, logical
fault addresses/access widths, FPSCR, preserved registers, SP and masks.
Integration compares callee arguments, entry depths and caller-visible buffer
addresses. Private frames and coefficient-copy scratch/call, caller-clobbered
register residue, APSR and full exception frames remain outside the proof.
Inputs into private callee frames, nonreturning INT_MAX loops, concurrent
mutation and physical sensors are not validated.

The fresh normal build compiles 715 units (641 application, 74 bootloader),
without failures or duplicate strong symbols. Imports remain 178/34 with the
same symbol sets. `make sources-check` passes. Exact qualification selects
neither body; canonical accounting stays at 4,381 source-built executable bytes,
641,779 stock executable bytes and 248 resource bytes. The fresh hybrid
application has the locked stock SHA-256. These checks do not establish a
complete source-only link, source completeness or C byte identity.

The remaining direct classifier wrappers are `0x56cf4` (crossing estimate,
calling `0x58aee` and `0x56f94`) and `0x56d78` (autocorrelation dispatch,
calling `0x5c5f0`). Their transitive routines and the classifier itself remain
unfinished. REA's observed direct references do not rule out indirect uses.
The [machine receipt](gomore-accel-axis-score-c-review.json) records source,
object, REA, fixture and build hashes with the proof boundaries.
